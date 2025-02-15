# -*- coding: utf-8 -*-

import sys
import os
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.db import ThreadLocal
from resources.lib.localproxy import LocalProxy
from resources.lib.schedule import Schedule


class Directory(Schedule):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # radiko認証
        sql = "SELECT auth_token, region, pref FROM auth JOIN cities ON auth.area_id = cities.area_id WHERE cities.city = ''"
        self.db.cursor.execute(sql)
        self.token, self.region, self.pref = self.db.cursor.fetchone()
        self.need_refresh = False

    def show(self, protocol=None, region=None, pref=None):
        # 表示中の放送局を格納するリスト
        front = []
        # 番組表取得フラグ
        stations = []
        # 表示
        if protocol == 'NHK':
            # NHKの放送局一覧を表示
            sql = 'SELECT * FROM stations WHERE protocol = :protocol AND display = 1 ORDER BY station'
            self.db.cursor.execute(sql, {'protocol': 'NHK'})
            for sdata in self.db.cursor.fetchall():
                self._add_station(sdata)
                if sdata['schedule'] == 1:
                    stations.append((sdata['protocol'], sdata['sid'], 1))
        elif protocol == 'RDK':
            # RDKの放送局一覧を表示
            sql = 'SELECT * FROM stations WHERE protocol = :protocol AND display = 1 ORDER BY station'
            self.db.cursor.execute(sql, {'protocol': 'RDK'})
            for sdata in self.db.cursor.fetchall():
                self._add_station(sdata)
                if sdata['schedule'] == 1:
                    stations.append((sdata['protocol'], sdata['sid'], 1))
        elif protocol == 'COMM':
            protocols = "('SJ', 'LR', 'SP', 'SR')"
            if region == '北海道': pref = '北海道'
            if region is None:  # 地域リスト
                sql = 'SELECT DISTINCT region FROM stations WHERE protocol IN %s ORDER BY code' % protocols
                self.db.cursor.execute(sql)
                for region, in self.db.cursor.fetchall():
                    self._add_directory(region=region)
            elif pref is None:  # 都道府県リスト
                sql = 'SELECT DISTINCT pref FROM stations WHERE protocol IN %s AND region = :region ORDER BY code' % protocols
                self.db.cursor.execute(sql, {'region': region})
                for pref, in self.db.cursor.fetchall():
                    self._add_directory(region=region, pref=pref)
            else:  # 放送局リスト
                sql = 'SELECT * FROM stations WHERE protocol IN %s AND region = :region AND pref = :pref AND display = 1 ORDER BY code' % protocols
                self.db.cursor.execute(sql, {'region': region, 'pref': pref})
                for sdata in self.db.cursor.fetchall():
                    self._add_station(sdata)
                    if sdata['schedule'] == 1:
                        stations.append((sdata['protocol'], sdata['sid'], 1))
        else:
            # トップページの放送局一覧を表示
            sql = '''SELECT * FROM stations WHERE top = 1 AND display = 1 ORDER BY
            CASE protocol
                WHEN 'NHK' THEN 1
                WHEN 'RDK' THEN 2
                WHEN 'SJ' THEN 3
                WHEN 'LR' THEN 3
                WHEN 'SP' THEN 3
                WHEN 'SR' THEN 3
                WHEN 'USER' THEN 4
                ELSE 9
            END, code, station'''
            self.db.cursor.execute(sql)
            for sdata in self.db.cursor.fetchall():
                self._add_station(sdata)
                if sdata['schedule'] == 1:
                    stations.append((sdata['protocol'], sdata['sid'], 1))
            # ディレクトリの一覧を表示
            self._setup_directory()
            # キーワードの一覧を表示
            self._setup_keywords()
        # 番組表取得
        self.maintain_schedule(stations)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def add_to_top(self, sid):
        sql = 'UPDATE stations SET top = 1 WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    def delete_from_top(self, sid):
        sql = 'UPDATE stations SET top = 0 WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
    
    def _setup_directory(self):
        # NHKラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30001))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'protocol': 'NHK', 'region': self.region})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 民放ラジオ(radiko)
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30002))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'protocol': 'RDK', 'region': self.region, 'pref': self.pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # コミュニティラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30003))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'protocol': 'COMM'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
    
    def _setup_keywords(self):
        sql = 'SELECT kid, keyword, dirname FROM keywords ORDER BY keyword'
        self.db.cursor.execute(sql)
        for kid, keyword, dirname in self.db.cursor.fetchall():
            self._add_keyword(kid, keyword)

    def _add_directory(self, region, pref=None):
        li = xbmcgui.ListItem(pref or region)
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('self.STR(30100)', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        if pref is None:
            query = urlencode({'action': 'show_station', 'protocol': 'COMM', 'region': region})
        else:
            query = urlencode({'action': 'show_station', 'protocol': 'COMM', 'region': region, 'pref': pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station(self, sdata):
        # listitemを追加する
        li = xbmcgui.ListItem(self._title(sdata))
        li.setProperty('IsPlayable', 'true')
        # メタデータ設定
        tag = li.getMusicInfoTag()
        tag.setTitle(sdata['station'])
        # サムネイル設定
        image = os.path.join(self.PROFILE_PATH, 'stations', 'logo', sdata['protocol'], sdata['station'] + '.png')
        li.setArt({'thumb': image, 'icon': image})
        # コンテクストメニュー
        self.contextmenu = []
        if sdata['top'] == 1:
            if sdata['schedule'] == 1:
                self._contextmenu(self.STR(30111), {'action': 'show_info', 'sid': sdata['sid']})
                self._contextmenu(self.STR(30110), {'action': 'update_info'})
            if sdata['protocol'] == 'USER':
                self._contextmenu(self.STR(30104), {'action': 'set_station', 'sid': sdata['sid']})
                self._contextmenu(self.STR(30105), {'action': 'delete_station', 'sid': sdata['sid']})
            else:
                self._contextmenu(self.STR(30102), {'action': 'delete_from_top', 'sid': sdata['sid']})
        else:
            if sdata['schedule'] == 1:
                self._contextmenu(self.STR(30111), {'action': 'show_info', 'sid': sdata['sid']})
                self._contextmenu(self.STR(30110), {'action': 'update_info'})
            self._contextmenu(self.STR(30101), {'action': 'add_to_top', 'sid': sdata['sid']})
        if self.GET('download') == 'true' and sdata['download'] == 1:
            self._contextmenu(self.STR(30106), {'action': 'set_keyword', 'sid': sdata['sid']})
        self._contextmenu(self.STR(30112), {'action': 'open_site', 'url': sdata['site']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ストリームURL
        url = LocalProxy.proxy(sdata['protocol'], key=sdata['key'], direct=sdata['direct'], token=self.token)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _add_keyword(self, kid, keyword):
        # listitemを追加する
        if kid > 0:
            li = xbmcgui.ListItem(keyword)
        else:
            li = xbmcgui.ListItem(f'[COLOR gray]{keyword}[/COLOR]')  # キーワード編集できない場合はグレイ表示
        # サムネイル画像
        if self.GET('rss') == 'false':
            logo = 'special://skin/extras/icons/search.png'
        else:
            logo = os.path.join(self.PROFILE_PATH, 'keywords', 'qr', f'{kid}.png')
        li.setArt({'thumb': logo, 'icon': logo})
        # コンテクストメニュー
        self.contextmenu = []
        if kid > 0:
            self._contextmenu(self.STR(30107), {'action': 'set_keyword', 'kid': kid})
            self._contextmenu(self.STR(30108), {'action': 'delete_keyword', 'kid': kid})
        self._contextmenu(self.STR(30109), {'action': 'open_folder', 'kid': kid})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # リストアイテムを追加
        query = urlencode({'action': 'show_download', 'kid': kid})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        
    def _title(self, sdata):
        # コミュニティ放送局用に都市名を追加
        basename = sdata['station']
        if sdata['protocol'] not in ('NHK', 'RDK', 'USER'):
            basename += f"({sdata['pref']}{sdata['city']})"
        station = basename
        # 番組情報等を追加
        if sdata['schedule'] == 1:
            sql = 'SELECT title, start, end FROM contents WHERE sid = :sid AND end > NOW() ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': sdata['sid']})
            try:
                # 2025-02-11 06:30:00
                (title, start, end) = self.db.cursor.fetchone()
                station += f' [COLOR khaki]▶ {title} ({start[11:16]}～{end[11:16]})[/COLOR]'
                (title, start, end) = self.db.cursor.fetchone()
                station += f' [COLOR lightgreen]▶ {title} ({start[11:16]}～{end[11:16]})[/COLOR]'
            except:
                # 番組情報が取得できない場合
                if station == basename:
                    station +=  f'[COLOR gray]▶ {self.STR(30700)}[/COLOR]'
        else:
            if sdata['description']:
                station += f" [COLOR khaki]▶ {sdata['description']}[/COLOR]"
        return station

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
