# -*- coding: utf-8 -*-

import os
import shutil
import json

from resources.lib.common import Common
from resources.lib.db import DB

import xbmc
import xbmcgui


class Station(Common):
    
    def __init__(self):
        # DBに接続
        self.db = DB()

    def __del__(self):
        # DBから切断
        self.db.conn.close()
    
    def set(self, sid=None):
        # アドオン設定画面から放送局設定画面を開いたとき、設定した値が以前の設定で書き換えられてしまうのを避ける
        xbmc.sleep(1000)
        # デフォルト設定
        self.SET('sid', '0')
        self.SET('station', '')
        self.SET('description', '')
        self.SET('direct', '')
        self.SET('logo', '')
        self.SET('site', '')
        if sid:
            # 放送局設定変更
            sql = 'SELECT * FROM stations WHERE sid = :sid'
            self.db.cursor.execute(sql, {'sid': sid})
            data = self.db.cursor.fetchone()
            self.SET('sid', str(sid))
            self.SET('station', data['station'])
            self.SET('description', data['description'])
            self.SET('direct', data['direct'])
            self.SET('logo', data['logo'])
            self.SET('site', data['site'])
        # 設定前の値
        before = dict([(key, self.GET(key)) for key in ('sid', 'station', 'description', 'direct', 'logo', 'site')])
        # statusテーブルに書き込む
        sql = 'UPDATE status SET station = :before'
        self.db.cursor.execute(sql, {'before': json.dumps(before)})
        # 放送局設定画面を開く
        shutil.copy(os.path.join(self.LIB_PATH, 'settings', 'station.xml'), self.DIALOG_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    def add(self):
        # 設定後の値
        after = dict([(key, self.GET(key)) for key in ('sid', 'station', 'description', 'direct', 'logo', 'site')])
        after.update({'type': 'user', 'abbr': ''})
        # stationテーブルに書き込む
        self.db.add_station(after, top=1)
        xbmc.executebuiltin('Container.Refresh')

    def delete(self, sid):
        # キーワード情報取得
        sql = 'SELECT station FROM stations WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        station, = self.db.cursor.fetchone()
        ok = xbmcgui.Dialog().yesno('削除確認', f'"{station}" を削除しますか？')
        if ok:
            self.db.delete_station(sid)
            xbmc.executebuiltin('Container.Refresh')