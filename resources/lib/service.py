# -*- coding: utf-8 -*-

import os
import shutil
import threading
import queue
import json
import time
import ffmpeg  # https://github.com/kkroening/ffmpeg-python

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.authenticate import Authenticate
from resources.lib.localproxy import LocalProxy

from resources.lib.timetable.nhkr import Scraper as Nhkr
from resources.lib.timetable.radk import Scraper as Radk


class Monitor(xbmc.Monitor, Common):

    def __init__(self):
        super().__init__()
        # DBの共有インスタンス
        self.db = ThreadLocal.db

    def onSettingsChanged(self):
        # ダイアログが最前面でない場合
        if xbmcgui.getCurrentWindowDialogId() == 9999:
            # 以前の設定値を取得
            self.db.cursor.execute('SELECT keyword, station FROM status')
            keyword, station = self.db.cursor.fetchone()
            # キーワードの設定値を比較
            if keyword:
                before = json.loads(keyword)
                after = dict([(key, self.GET(key)) for key in ('kid', 'kstatus', 'keyword', 'match', 'weekday', 'station')])
                if after != before:
                    xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_keyword)' % self.ADDON_ID)  # 設定変更
            # 放送局の設定値を比較
            if station:
                before = json.loads(station)
                after = dict([(key, self.GET(key)) for key in ('sid', 'station', 'description', 'direct', 'logo', 'site')])
                if after != before:
                    xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_station)' % self.ADDON_ID)  # 設定変更
            # キーワード、放送局以外の変更のために再描画する
            xbmc.executebuiltin('Container.Refresh')


class Service(Common):

    # 更新確認のインターバル
    CHECK_INTERVAL = 30
    # radiko認証のインターバル
    AUTH_INTERVAL = 3600
    
    # ダウンロード予約のタイミング
    DOWNLOAD_PREPARATION = 180
    # ダウンロード開始の遅延
    DOWNLOAD_DELAY = {'nhkr': 35, 'radk': 15}
    # ダウンロード開始の余裕
    DOWNLOAD_MARGIN = 5

    def __init__(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # authテーブルを初期化
        db.cursor.executescript(db.sql_auth_init)
        # statusテーブルを初期化
        db.cursor.executescript(db.sql_status_init)
        # ダウンロード済み以外の番組情報を削除
        db.cursor.execute('DELETE FROM contents WHERE cstatus != -1')
        # ダウンロードを失敗/中断したmp3ファイルを削除
        sql = '''SELECT c.filename, k.dirname 
        FROM contents c JOIN keywords k ON c.kid = k.kid
        WHERE c.cstatus = -2 or c.cstatus = 3'''
        db.cursor.execute(sql)
        for filename, dirname in db.cursor.fetchall():
            mp3file = os.path.join(db.CONTENTS_PATH, dirname, filename)
            if os.path.exists(mp3file):
                os.remove(mp3file)
        # 設定画面をデフォルトに設定
        shutil.copy(os.path.join(Common.DATA_PATH, 'settings', 'settings.xml'), Common.DIALOG_FILE)
        # stations/logoを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'stations', 'logo')) is False:
            shutil.copytree(os.path.join(self.DATA_PATH, 'stations', 'logo'), os.path.join(self.PROFILE_PATH, 'stations', 'logo'))
        # keywords/qrを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'keywords', 'qr')) is False:
            os.makedirs(os.path.join(self.PROFILE_PATH, 'keywords', 'qr'), exist_ok=True)
        # timetableを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'timetable')) is False:
            os.makedirs(os.path.join(self.PROFILE_PATH, 'timetable'), exist_ok=True)
        # hls cacheをクリア
        if os.path.isdir(self.HLS_CACHE_PATH) is True:
            shutil.rmtree(self.HLS_CACHE_PATH)
        os.makedirs(self.HLS_CACHE_PATH)
        # キューを初期化
        self.queue = queue.Queue()  # ダウンロードプロセス
        # ローカルプロキシを初期化
        self.httpd = LocalProxy()
        # 別スレッドでローカルプロキシを起動
        thread = threading.Thread(target=self.httpd.serve_forever)
        thread.start()

    def monitor(self):
        # DBインスタンスを作成
        db = ThreadLocal.db = DB()
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # 現在時刻
        now = time.time()
        # radiko認証
        update_auth = self._update_auth()
        # 番組データ取得
        update_nhkr = self._update_nhkr()
        update_radk = self._update_radk()
        # 監視を開始
        monitor = Monitor()
        refresh = False
        while monitor.abortRequested() is False:
            # 現在時刻
            now = time.time()
            # 現在時刻がradiko認証更新時刻を過ぎていたら
            if now > update_auth:
                update_auth = self._update_auth()
            # 現在時刻が番組表更新予定時刻を過ぎていたら
            if now > update_nhkr:
                update_nhkr = self._update_nhkr()
                refresh = refresh or update_nhkr > now
            if now > update_radk:
                update_radk = self._update_radk()
                refresh = refresh or update_radk > now
            # カレントウィンドウをチェック
            if xbmcgui.getCurrentWindowDialogId() == 9999:
                db.cursor.execute('SELECT timetable, keyword, station FROM status')
                timetable, keyword, station = db.cursor.fetchone()
                # 要更新が検出されたら
                refresh = refresh or timetable == 1
                if refresh:
                    path = xbmc.getInfoLabel('Container.FolderPath')
                    argv = 'plugin://%s/' % self.ADDON_ID
                    if path == argv or path.startswith(f'{argv}?action=show'):
                        xbmc.executebuiltin('Container.Refresh')
                        refresh = False
                        db.cursor.execute('UPDATE status SET timetable = 0')
                # デフォルト設定に戻す
                if keyword or station:
                    # statusテーブル
                    db.cursor.execute("UPDATE status SET keyword = '', station = ''")
                    # 設定画面
                    shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'settings.xml'), self.DIALOG_FILE)
            # キューに格納した番組の処理
            self._process_queue()
            # CHECK_INTERVALの間待機
            monitor.waitForAbort(self.CHECK_INTERVAL)
        # ローカルプロキシを終了
        self.log('shutting down local proxy.')
        self.httpd.shutdown()
        # スレッドのプロセスを終了
        self.log('shutting down thread processes.')
        while self.queue.qsize() > 0:
            process = self.queue.get()
            process.kill()
        # 監視終了を通知
        self.log('exit monitor.')
        # DBインスタンスを終了
        db.conn.close()

    def _authenticate(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # radiko認証
        auth = Authenticate()
        if auth.response['authed'] == 0:
            # 認証失敗を通知
            self.notify('radiko authentication failed', error=True)
        # 認証情報をDBに書き込む
        data = auth.response
        set_clause = ', '.join([f'{key} = ?' for key in data.keys()])
        sql = f'UPDATE auth SET {set_clause}'
        db.cursor.execute(sql, list(data.values()))
        # 地域、都道府県を判定する
        sql = "SELECT region, pref FROM auth JOIN cities ON auth.area_id = cities.radiko WHERE cities.city = ''"
        db.cursor.execute(sql)
        self.region, self.pref = db.cursor.fetchone()
        # ログ
        self.log('radiko authentication status:', data['authed'], 'region:', self.region, 'pref:', self.pref)

    def _update_auth(self):
        try:
            # radiko認証
            self._authenticate()
            # 次のradiko認証更新時刻
            update_auth = time.time() + self.AUTH_INTERVAL
        except Exception as e:
            self.log('monitor error in _update_auth:', e)
        return update_auth
    
    def _update_nhkr(self):
        try:
            # NHKの番組データを取得
            scraper = Nhkr(self.region)
            scraper.update()
            # 次の番組情報更新時刻
            update_nhkr = scraper.next_aired()
        except Exception as e:
            self.log('monitor error in _update_nhkr:', e)
        return update_nhkr
    
    def _update_radk(self):
        try:
            # radikoの番組データを取得
            scraper = Radk(self.region, self.pref)
            scraper.update()
            # 次の番組情報更新時刻
            update_radk = scraper.next_aired()
        except Exception as e:
            self.log('monitor error in _update_radk:', e)
        return update_radk

    def _process_queue(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 保留中(cstatus=1)の番組、かつDOWNLOAD_PREPARATION以内に開始する番組を検索
        sql = '''SELECT c.cid, c.kid, c.filename, s.type, s.abbr, c.title, EPOCH(c.start) as t, EPOCH(c.end), s.direct
        FROM contents c JOIN stations s ON c.sid = s.sid
        WHERE c.cstatus = 1 AND t - EPOCH(NOW()) < :threshold
        ORDER BY c.start'''
        db.cursor.execute(sql, {'threshold': self.DOWNLOAD_PREPARATION})
        # ダウンロードを予約
        for cid, kid, filename, type, abbr, title, start, end, direct in db.cursor.fetchall():
            delay = self.DOWNLOAD_DELAY[type]
            start = start + delay - self.DOWNLOAD_MARGIN  # 開始時刻
            end = end + delay + self.DOWNLOAD_MARGIN  # 終了時刻
            # ダウンロードを予約
            args = [cid, kid, filename, type, abbr, title, end, direct, self.queue]
            thread = threading.Timer(start - int(time.time()), download, args=args)
            thread.start()
            # 待機中(cstatus=2)に更新
            sql = 'UPDATE contents SET cstatus = 2 WHERE cid = :cid'
            db.cursor.execute(sql, {'cid': cid})


def download(cid, kid, filename, type, abbr, title, end, direct, queue):
    # DBインスタンスを作成
    db = ThreadLocal.db = DB()
    # radiko認証
    sql = 'SELECT auth_token FROM auth'
    db.cursor.execute(sql)
    token, = db.cursor.fetchone()
    # ストリームURL
    url = LocalProxy.proxy(type, abbr=abbr, direct=direct, token=token, download=True)
    # 時間
    duration = end - int(time.time())
    # ビットレート
    bitrate = Common.GET('bitrate')
    if bitrate == 'auto':
        if duration <= 3600:
            bitrate = '192k'
        elif duration <= 4320:
            bitrate = '160k'
        elif duration <= 5400:
            bitrate = '128k'
        elif duration <= 7200:
            bitrate = '96k'
        else:
            bitrate = '64k'
    # 出力ディレクトリ
    sql = 'SELECT dirname FROM keywords WHERE kid = :kid'
    db.cursor.execute(sql, {'kid': kid})
    dirname, = db.cursor.fetchone()
    # 出力ファイル
    download_path = os.path.join(Common.CONTENTS_PATH, dirname)
    os.makedirs(download_path, exist_ok=True)
    mp3file = os.path.join(download_path, filename)
    # ffmpeg実行
    kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
    process = ffmpeg.input(url, f='hls', t=duration).output(mp3file, **kwargs).run_async(pipe_stderr=True)
    # プロセスをキューに追加
    queue.put(process)
    # DB更新
    sql = 'UPDATE contents SET cstatus = 3 WHERE cid = :cid'
    db.cursor.execute(sql, {'cid': cid})
    # 開始通知
    Common.notify(f'Download started "{title}"')
    # ログ
    Common.log(f'[{process.pid}] Download started.')
    # ダウンロード終了を待つ
    process.wait()
    # ダウンロード結果に応じて後処理
    if process.returncode == 0:
        # DB更新
        sql = 'UPDATE contents SET cstatus = -1 WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid})
        # ID3タグを書き込む
        db.write_id3(mp3file, cid)
        # 完了通知
        Common.notify('Download complete "%s"' % title)
        # ログ
        Common.log(f'[{process.pid}] Download complete.')
    else:
        # エラーメッセージ
        err = process.stderr.read().decode('utf-8')
        # DB更新
        sql = 'UPDATE contents SET cstatus = -2, description = :err WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid, 'err': err})
        # 完了通知
        Common.notify('Download failed "%s"' % title, error=True)
        # ログ
        Common.log(f'[{process.pid}] Download failed (returncode={process.returncode}).')
        Common.log(err)
    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
