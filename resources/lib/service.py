# -*- coding: utf-8 -*-

from resources.lib.common import Common
from resources.lib.prefdata import PrefData
from resources.lib.authenticate import Authenticate
from resources.lib.keyword import Keyword
from resources.lib.directory import Directory
from resources.lib.timetable.nhkr import Scraper as Nhkr
from resources.lib.timetable.radk import Scraper as Radk

import os
import shutil
import datetime
import platform
import json
import ffmpeg

from threading import Timer

import xbmc
import xbmcgui


class Monitor(xbmc.Monitor, Common):

    def __init__(self):
        super().__init__()

    def onSettingsChanged(self):
        # カレントウィンドウをチェック
        if xbmcgui.getCurrentWindowDialogId() != 10140:
            settings = self.read(os.path.join(Common.RESOURCES_PATH, 'settings.xml'))
            if settings == self.read(os.path.join(Common.RESOURCES_PATH, 'station.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_station)' % Common.ADDON_ID)
                #self.notify('Station settings changed')
                return
            if settings == self.read(os.path.join(Common.RESOURCES_PATH, 'keyword.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_keyword)' % Common.ADDON_ID)
                #self.notify('Keyword settings changed')
                return
            if settings == self.read(os.path.join(Common.RESOURCES_PATH, 'default.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=validate)' % Common.ADDON_ID)
                #self.notify('Settings changed')
                return


class Service(Common, PrefData):

    CHECK_INTERVAL = 30
    AUTH_INTERVAL = 3600
    DOWNLOAD_MARGIN = 180

    def __init__(self):
        # ディレクトリをチェック
        if not os.path.isdir(self.DIRECTORY_PATH):
            shutil.copytree(os.path.join(self.RESOURCES_PATH, 'lib', 'stations', 'directory'), self.DIRECTORY_PATH)
        if not os.path.isdir(self.INDEX_PATH):
            shutil.copytree(os.path.join(self.RESOURCES_PATH, 'lib', 'stations', 'json'), self.INDEX_PATH)
        if not os.path.isdir(self.LOGO_PATH):
            shutil.copytree(os.path.join(self.RESOURCES_PATH, 'lib', 'stations', 'logo'), self.LOGO_PATH)
        if not os.path.isdir(self.TIMETABLE_PATH):
            os.makedirs(self.TIMETABLE_PATH, exist_ok=True)
        if not os.path.isdir(self.KEYWORDS_PATH):
            os.makedirs(self.KEYWORDS_PATH, exist_ok=True)
        # cache, queue
        if os.path.isdir(self.HLS_CACHE_PATH):
            shutil.rmtree(self.HLS_CACHE_PATH)
        os.makedirs(self.HLS_CACHE_PATH)
        if os.path.isdir(self.PENDING_PATH):
            shutil.rmtree(self.PENDING_PATH)
        os.makedirs(self.PENDING_PATH)
        if os.path.isdir(self.PROCESSING_PATH):
            shutil.rmtree(self.PROCESSING_PATH)
        os.makedirs(self.PROCESSING_PATH)
        if os.path.isdir(self.DOWNLOAD_PATH):
            shutil.rmtree(self.DOWNLOAD_PATH)
        os.makedirs(self.DOWNLOAD_PATH)
        # キューを初期化
        self.pending = []  # ダウンロード待ち
        self.processing = []  # ダウンロード中
        # OSを判定
        self.SET('os', platform.system())

    def _authenticate(self):
        # radiko認証
        auth = Authenticate()
        if auth.response['authed'] == 0:
            # 認証失敗を通知
            self.notify('radiko authentication failed', error=True)
        # 認証情報をファイルに書き込む
        self.write_as_json(self.AUTH_FILE, auth.response)
        # 地域、都道府県を判定する
        _, self.region, self.pref = self.radiko_place(auth.response['area_id'])
        # ログ
        self.log('radiko authentication status:', auth.response['authed'], 'region:', self.region, 'pref:', self.pref)
    
    def _now(self):
        return datetime.datetime.now().timestamp()
    
    def monitor(self, localproxy):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # 現在時刻
        now = self._now()
        # radiko認証
        self._authenticate()
        update_auth = now + self.AUTH_INTERVAL
        # stream取得のためのDirectory初期化
        self.directory = Directory()
        # 番組表取得
        update_nhkr = now + Nhkr(self.region).update(force=True)
        update_radk = now + Radk(self.pref).update(force=True)
        # 設定されたキーワードと照合してダウンロード準備
        self.pending = Keyword().match()
        # 監視を開始
        monitor = Monitor()
        refresh = False
        while monitor.abortRequested() is False:
            # 現在時刻
            now = self._now()
            # 現在時刻がradiko認証更新時刻を過ぎていたら
            if now > update_auth:
                self._authenticate()  # radiko認証
                update_auth = now + self.AUTH_INTERVAL
            # 現在時刻が番組表更新予定時刻を過ぎていたら
            if now > update_nhkr:
                update_nhkr = now + Nhkr(self.region).update()  # NHKの番組データを取得
                refresh = update_nhkr > now  # 番組データが更新されたら画面更新
            if now > update_radk:
                update_radk = now + Radk(self.pref).update()  # radikoの番組データを取得
                refresh = update_radk > now  # 番組データが更新されたら画面更新
            # 画面更新が検出されたら
            if refresh:
                # 設定されたキーワードと照合してキューに格納
                self.pending = self.pending + Keyword().match()
                # カレントウィンドウをチェック
                if xbmcgui.getCurrentWindowDialogId() == 9999:
                    path = xbmc.getInfoLabel('Container.FolderPath')
                    argv = 'plugin://%s/' % self.ADDON_ID
                    if path == argv or path.startswith(f'{argv}?action=show'):
                        xbmc.executebuiltin('Container.Refresh')
                        refresh = False
            # キューに格納した番組の処理
            self._do_queue()
            # CHECK_INTERVALの間待機
            monitor.waitForAbort(self.CHECK_INTERVAL)
        # ローカルプロキシを終了
        localproxy.shutdown()
        # 監視終了を通知
        self.log('exit monitor.')

    def _do_queue(self):
        # 現在時刻
        now = self._now()
        # キューをチェック
        pending = []
        for program, path in self.pending:
            if program['end'] < now:
                # すでに終了している番組はキューから削除
                os.remove(path)
            elif program['start']  - self.DOWNLOAD_MARGIN < now:
                # 移動先のパス
                new_path = os.path.join(self.PROCESSING_PATH, os.path.basename(path))
                # DOWNLOAD_MARGIN以内に開始する番組はダウンロードを予約
                Timer(program['start'] - now, self._do_download, args=[program, new_path]).start()
                # ファイルを移動
                shutil.move(path, new_path)
            else:
                # DOWNLOAD_MARGIN以降に開始する番組はキューに残す
                pending.append((program, path))
        self.pending = pending
    
    def _search_stream(self, program):
        if program['type'] in ('nhk1', 'nhk2', 'nhk3'):
            type_ = 'nhkr'
        else:
            type_ = program['type']
        index = self.read_as_json(os.path.join(self.INDEX_PATH, '%s.json' % type_))
        station = list(filter(lambda x: x['name'] == program['name'], index))[0]
        return self.directory.stream(station)

    def _do_download(self, program, path):
        # ストリームURL
        stream = self._search_stream(program)
        self.log(stream, json.dumps(program, ensure_ascii=False))
        # 時間
        duration = program['end'] - self._now()
        # ビットレート
        bitrate = self.GET('bitrate')
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
        # 出力ファイル
        output = os.path.join(self.DOWNLOAD_PATH, '%s.mp3' % os.path.basename(path))
        # ffmpeg実行
        kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
        p = ffmpeg.input(stream, t=duration).output(output, **kwargs).run_async()
        # 開始通知
        self.notify('Download started "%s"' % program['title'])
        # ログ
        self.log(f'[{p.pid}] Download start.')
        # ダウンロード終了を待つ
        p.wait()
        # ダウンロード結果に応じて後処理
        if p.returncode == 0:
            # pathと、'*/*.mp3' (DOWNLOAD_PATH, os.path.basename(path))を、folder配下へ移動する
            '''
            # 全コンテンツのrssファイル生成
            Contents().createrss()
            # 対応するkey(=data['tit1'])のコンテンツrssファイル生成
            if data['tit1']:
                Contents(data['tit1']).createrss()
            '''
            # 完了通知
            self.notify('Download completed "%s"' % program['title'])
            # ログ
            self.log(f'[{p.pid}] Download completed.')
        else:
            # 失敗したときはjsonファイルを削除
            os.remove(path)
            # 完了通知
            self.notify('Download failed "%s"' % program['title'], error=True)
            # ログ
            self.log(f'[{p.pid}] Download failed (returncode={p.returncode}).')
