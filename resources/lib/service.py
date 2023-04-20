# -*- coding: utf-8 -*-

from resources.lib.common import Common
from resources.lib.prefecture import Prefecture
from resources.lib.authenticate import Authenticate
from resources.lib.keyword import Keyword
from resources.lib.localproxy import LocalProxy
from resources.lib.download import Download

from resources.lib.timetable.nhkr import Scraper as Nhkr
from resources.lib.timetable.radk import Scraper as Radk

import os
import shutil
import platform
import threading
import queue

import xbmc
import xbmcgui


class Monitor(xbmc.Monitor, Common):

    def __init__(self):
        super().__init__()

    def onSettingsChanged(self):
        # カレントウィンドウをチェック
        if xbmcgui.getCurrentWindowDialogId() != 10140:
            settings = self.read(os.path.join(self.RESOURCES_PATH, 'settings.xml'))
            if settings == self.read(os.path.join(self.RESOURCES_PATH, 'station.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_station)' % self.ADDON_ID)
                #self.notify('Station settings changed')
                return
            if settings == self.read(os.path.join(self.RESOURCES_PATH, 'keyword.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=add_keyword)' % self.ADDON_ID)
                #self.notify('Keyword settings changed')
                return
            if settings == self.read(os.path.join(self.RESOURCES_PATH, 'default.xml')):
                xbmc.executebuiltin('RunPlugin(plugin://%s?action=validate)' % self.ADDON_ID)
                #self.notify('Settings changed')
                return


class Service(Common, Prefecture):

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
        # OSを判定
        self.SET('os', platform.system())
        # ディレクトリをチェック
        self._setup_userdata()
        # キューを初期化
        self.pending = []  # ダウンロード待ち
        self.processing = []  # ダウンロード中
        self.queue = queue.Queue()  # ダウンロードプロセス
        # ローカルプロキシを初期化
        self.httpd = LocalProxy()
        # 別スレッドでローカルプロキシを起動
        thread = threading.Thread(target=self.httpd.serve_forever)
        thread.start()

    def _setup_userdata(self):
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
        # hls cache
        if os.path.isdir(self.HLS_CACHE_PATH):
            shutil.rmtree(self.HLS_CACHE_PATH)
        os.makedirs(self.HLS_CACHE_PATH)
        # queue
        if os.path.isdir(self.PENDING_PATH):
            shutil.rmtree(self.PENDING_PATH)
        os.makedirs(self.PENDING_PATH)
        if os.path.isdir(self.PROCESSING_PATH):
            shutil.rmtree(self.PROCESSING_PATH)
        os.makedirs(self.PROCESSING_PATH)
        if os.path.isdir(self.DOWNLOAD_PATH):
            shutil.rmtree(self.DOWNLOAD_PATH)
        os.makedirs(self.DOWNLOAD_PATH)
        # mmap
        if os.path.isdir(self.MMAP_FILE):
            os.remove(self.MMAP_FILE)
        shutil.copy(os.path.join(self.RESOURCES_PATH, 'mmap.txt'), self.MMAP_FILE)

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
    
    def monitor(self):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # 現在時刻
        now = self.now()
        # radiko認証
        self._authenticate()
        update_auth = now + self.AUTH_INTERVAL
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
            now = self.now()
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
            # 共有メモリをチェック
            if self.read_mmap() == 'True':
                refresh = True
            # 要更新が検出されたら
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
                        self.write_mmap('False')
            # キューに格納した番組の処理
            self.pending = self._process_queue()
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

    def _process_queue(self):
        # 現在時刻
        now = self.now()
        # キューをチェック
        pending = []
        for program, path in self.pending:
            if program['end'] < now:
                # すでに終了している番組はキューから削除
                os.remove(path)
            elif program['start'] - self.DOWNLOAD_PREPARATION < now:
                # 移動先のパス
                new_path = os.path.join(self.PROCESSING_PATH, os.path.basename(path))
                # DOWNLOAD_PREPARATION以内に開始する番組はダウンロードを予約
                delay = self.DOWNLOAD_DELAY[program['type']]
                extra = delay + 2 * self.DOWNLOAD_MARGIN
                delay = program['start'] - now + delay
                if delay < self.DOWNLOAD_MARGIN:
                    delay = delay - self.DOWNLOAD_MARGIN 
                # ダウンロード時間
                thread = threading.Timer(delay, Download().download, args=[program, extra, new_path, self.queue])
                thread.start()
                # ファイルを移動
                shutil.move(path, new_path)
            else:
                # DOWNLOAD_PREPARATION以降に開始する番組はキューに残す
                pending.append((program, path))
        return pending
