# -*- coding: utf-8 -*-

from resources.lib.common import Common
from resources.lib.prefdata import PrefData
from resources.lib.authenticate import Authenticate
from resources.lib.timetable.nhkr import Scraper as Nhkr
from resources.lib.timetable.radk import Scraper as Radk

import os
import shutil
import datetime
import platform

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
                self.notify('Station settings changed')
                return


class Service(Common, PrefData):

    CHECK_INTERVAL = 30
    AUTH_INTERVAL = 3600

    def __init__(self):
        # ディレクトリをチェック
        if not os.path.isdir(self.DIRECTORY_PATH):
            shutil.copytree(os.path.join(self.RESOURCES_PATH, 'lib', 'stations', 'directory'), self.DIRECTORY_PATH)
        if not os.path.isdir(self.LOGO_PATH):
            shutil.copytree(os.path.join(self.RESOURCES_PATH, 'lib', 'stations', 'logo'), self.LOGO_PATH)
        if not os.path.isdir(self.TIMETABLE_PATH):
            os.makedirs(self.TIMETABLE_PATH, exist_ok=True)
        if not os.path.isdir(self.HLS_CACHE_PATH):
            os.makedirs(self.HLS_CACHE_PATH, exist_ok=True)
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
    
    def monitor(self, refresh=False):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # 現在時刻
        now = self._now()
        # radiko認証
        self._authenticate()
        update_auth = now + self.AUTH_INTERVAL
        # 番組表取得
        update_nhkr = now + Nhkr(self.region).update(force=True)
        update_radk = now + Radk(self.pref).update(force=True)
        # 監視を開始
        monitor = Monitor()
        while monitor.abortRequested() is False:
            # 現在時刻
            now = self._now()
            # 現在時刻がRadiko認証更新時刻を過ぎていたら
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
                # カレントウィンドウをチェック
                if xbmcgui.getCurrentWindowDialogId() == 9999:
                    path = xbmc.getInfoLabel('Container.FolderPath')
                    argv = 'plugin://%s/' % self.ADDON_ID
                    if path == argv or path.startswith(f'{argv}?action=show'):
                        xbmc.executebuiltin('Container.Refresh')
                    refresh = False
            # CHECK_INTERVALの間待機
            monitor.waitForAbort(self.CHECK_INTERVAL)
        # 監視終了を通知
        self.log('exit monitor.')
