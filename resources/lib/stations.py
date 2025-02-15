# -*- coding: utf-8 -*-

import os
import shutil
import json
import re

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Stations(Common):
    
    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db

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
        shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'station.xml'), self.DIALOG_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    def add(self):
        # 設定後の値
        after = dict([(key, self.GET(key)) for key in ('sid', 'station', 'description', 'direct', 'logo', 'site')])
        after.update({'protocol': 'USER', 'key': ''})
        # stationテーブルに書き込む
        self.db.add_station(after, top=1)
        xbmc.executebuiltin('Container.Refresh')

    def delete(self, sid):
        # キーワード情報取得
        sql = 'SELECT station FROM stations WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        station, = self.db.cursor.fetchone()
        ok = xbmcgui.Dialog().yesno(self.STR(30607), self.STR(30608) % station)
        if ok:
            self.db.delete_station(sid)
            xbmc.executebuiltin('Container.Refresh')

    def show_info(self, sid):
        # 番組情報を検索
        sql = 'SELECT title, description FROM contents WHERE sid = :sid AND end > NOW() ORDER BY start LIMIT 2'
        self.db.cursor.execute(sql, {'sid': sid})
        data = [(title, description) for title, description in self.db.cursor.fetchall()]
        # 選択ダイアログを表示
        index = xbmcgui.Dialog().select(self.STR(30606), [title for title, _ in data])
        if index == -1:
            return
        # 選択された番組の情報を表示
        _, description = data[index]
        # テキストを整形
        if description:
            description = re.sub(r'<p class="(?:act|info|desc)">(.*?)</p>', r'\1\n\n', description)
            description = re.sub(r'<br */>', r'\n', description)
            description = re.sub(r'<.*?>', '', description)
            description = re.sub(r'\n{3,}', r'\n\n', description)
        else:
            description = self.STR(30610)
        xbmcgui.Dialog().textviewer(self.STR(30609), description)
