# -*- coding: utf-8 -*-

import os
import shutil
import threading
import queue
import json
import time

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.localproxy import LocalProxy
from resources.lib.authenticator import AuthenticationManager
from resources.lib.scheduler import ScheduleManager
from resources.lib.downloader import DownloadManager


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


class Service(AuthenticationManager, ScheduleManager, DownloadManager):

    def __init__(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # authテーブルを初期化
        db.cursor.executescript(db.sql_auth_init)
        # statusテーブルを初期化
        db.cursor.executescript(db.sql_status_init)
        # ダウンロードを失敗/中断したmp3ファイルを削除
        sql = '''SELECT c.filename, k.dirname 
        FROM contents c JOIN keywords k ON c.kid = k.kid
        WHERE c.cstatus = -2 or c.cstatus = 3'''
        db.cursor.execute(sql)
        for filename, dirname in db.cursor.fetchall():
            mp3file = os.path.join(db.CONTENTS_PATH, dirname, filename)
            if os.path.exists(mp3file):
                os.remove(mp3file)
        # ダウンロード済み以外の番組情報を削除
        db.cursor.execute('DELETE FROM contents WHERE cstatus != -1')
        # 番組表更新予定時間を初期化
        db.cursor.execute("UPDATE stations SET nextaired = '1970-01-01 09:00:00'")
        # 設定画面をデフォルトに設定
        shutil.copy(os.path.join(Common.DATA_PATH, 'settings', 'settings.xml'), Common.DIALOG_FILE)
        # stations/logoを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'stations', 'logo')) is False:
            shutil.copytree(os.path.join(self.DATA_PATH, 'stations', 'logo'), os.path.join(self.PROFILE_PATH, 'stations', 'logo'))
        # keywords/qrを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'keywords', 'qr')) is False:
            os.makedirs(os.path.join(self.PROFILE_PATH, 'keywords', 'qr'), exist_ok=True)
        # scheduleを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'schedule')) is False:
            os.makedirs(os.path.join(self.PROFILE_PATH, 'schedule'), exist_ok=True)
        # hls cacheをクリア
        if os.path.isdir(self.HLS_CACHE_PATH) is True:
            shutil.rmtree(self.HLS_CACHE_PATH)
        os.makedirs(self.HLS_CACHE_PATH)
        # ローカルプロキシを初期化
        self.httpd = LocalProxy()
        # 別スレッドでローカルプロキシを起動
        thread = threading.Thread(target=self.httpd.serve_forever)
        thread.start()

    def monitor(self):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # スレッドのDBインスタンスを作成
        db = ThreadLocal.db = DB()
        # 認証予定時刻
        self.update_auth = 0
        # ダウンロードプロセスを格納するキューを初期化
        self.queue = queue.Queue()
        # 監視を開始
        monitor = Monitor()
        while monitor.abortRequested() is False:
            # radiko認証更新
            self.maintain_auth()
            # 番組表更新
            self.maintain_schedule()
            # 表示中画面が設定画面でなければ、設定画面はデフォルトに戻す
            if xbmcgui.getCurrentWindowDialogId() == 9999:
                db.cursor.execute('SELECT keyword, station FROM status')
                keyword, station = db.cursor.fetchone()
                if keyword or station:
                    db.cursor.execute("UPDATE status SET keyword = '', station = ''")  # statusテーブル
                    shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'settings.xml'), self.DIALOG_FILE)  # アドオン設定画面
            # ダウンロード開始判定
            self.maintain_download()
            # CHECK_INTERVALの間待機
            t = time.time()
            dt = t - int(t)
            dt += int(t) % self.CHECK_INTERVAL
            monitor.waitForAbort(self.CHECK_INTERVAL - dt)
        # ローカルプロキシを終了
        self.log('shutting down local proxy.')
        self.httpd.shutdown()
        # スレッドのプロセスを終了
        self.log('shutting down thread processes.')
        while self.queue.qsize() > 0:
            process = self.queue.get()
            if process.poll() is None:  # 実行中だったら
                process.kill()
        # スレッドのDBインスタンスを終了
        db.conn.close()
        # 監視終了を通知
        self.log('exit monitor.')
