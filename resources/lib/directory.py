# -*- coding: utf-8 -*-

import sys
import os
from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.localproxy import LocalProxy

import xbmc
import xbmcgui
import xbmcplugin


class Directory(Common):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # radiko認証
        sql = "SELECT auth_token, region, pref FROM auth JOIN codes ON auth.area_id = codes.radiko WHERE codes.city = ''"
        self.db.cursor.execute(sql)
        self.token, self.region, self.pref = self.db.cursor.fetchone()

    def show(self, type=None, region=None, pref=None):
        if type == 'nhkr':
            sql = 'SELECT * FROM stations WHERE type = :type and region = :region ORDER BY station'
            self.db.cursor.execute(sql, {'type': 'nhkr', 'region': region})
            for sdata in self.db.cursor.fetchall():
                self._add_station(sdata)
        elif type == 'radk':
            sql = 'SELECT * FROM stations WHERE type = :type and region = :region and pref = :pref ORDER BY station'
            self.db.cursor.execute(sql, {'type': 'radk', 'region': region, 'pref': pref})
            for sdata in self.db.cursor.fetchall():
                self._add_station(sdata)
        elif type == 'comm':
            types = '''('csra', 'fmpp', 'jcba', 'lsnr')'''
            if region is None:  # 地域リスト
                sql = 'SELECT DISTINCT region FROM stations WHERE type IN %s ORDER BY code' % types
                self.db.cursor.execute(sql)
                for region, in self.db.cursor.fetchall():
                    self._add_directory(region=region)
            elif pref is None:  # 都道府県リスト
                sql = 'SELECT DISTINCT pref FROM stations WHERE type IN %s and region = :region ORDER BY code' % types
                self.db.cursor.execute(sql, {'region': region})
                for pref, in self.db.cursor.fetchall():
                    self._add_directory(region=region, pref=pref)
            else:  # 放送局リスト
                sql = 'SELECT * FROM stations WHERE type IN %s and region = :region and pref = :pref ORDER BY code' % types
                self.db.cursor.execute(sql, {'region': region, 'pref': pref})
                for sdata in self.db.cursor.fetchall():
                    self._add_station(sdata)
        else:
            self._setup_stations()  # 放送局
            self._setup_directory()  # ディレクトリ
            self._setup_keywords()  # キーワード
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

    def _setup_stations(self):
        # ユーザがトップページに追加した放送局を追加
        sql = '''SELECT * FROM stations WHERE top = 1 ORDER BY
        CASE type
            WHEN 'nhkr' THEN 1
            WHEN 'radk' THEN 2
            WHEN 'csra' THEN 3
            WHEN 'fmpp' THEN 3
            WHEN 'jcba' THEN 3
            WHEN 'lsnr' THEN 3
            WHEN 'user' THEN 4
            ELSE 9
        END, code, station'''
        self.db.cursor.execute(sql)
        for sdata in self.db.cursor.fetchall():
            self._add_station(sdata)
    
    def _setup_directory(self):
        # NHKラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30001))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'type': 'nhkr', 'region': self.region})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 民放ラジオ(radiko)
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30002))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'type': 'radk', 'region': self.region, 'pref': self.pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # コミュニティラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30003))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'type': 'comm'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
    
    def _setup_keywords(self):
        sql = 'SELECT kid, keyword, dirname FROM keywords ORDER BY keyword'
        self.db.cursor.execute(sql)
        for kid, keyword, dirname in self.db.cursor.fetchall():
            self._add_keyword(kid, keyword, dirname)

    def _add_directory(self, region, pref=None):
        li = xbmcgui.ListItem(pref or region)
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('self.STR(30100)', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        if pref is None:
            query = urlencode({'action': 'show_station', 'type': 'comm', 'region': region})
        else:
            query = urlencode({'action': 'show_station', 'type': 'comm', 'region': region, 'pref': pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station(self, sdata):
        # listitemを追加する
        li = xbmcgui.ListItem(self._title(sdata))
        # サムネイル画像
        logo = os.path.join(self.PROFILE_PATH, 'stations', 'logo', sdata['type'], sdata['station'] + '.png')
        li.setArt({'thumb': logo, 'icon': logo})
        li.setInfo(type='music', infoLabels={'title': sdata['station']})
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        if sdata['top'] == 1:
            if sdata['type'] in ('nhkr', 'radk'):
                self._contextmenu(self.STR(30111), {'action': 'show_info', 'sid': sdata['sid']})
                self._contextmenu(self.STR(30110), {'action': 'update_info'})
            if sdata['type'] == 'user':
                self._contextmenu(self.STR(30104), {'action': 'set_station', 'sid': sdata['sid']})
                self._contextmenu(self.STR(30105), {'action': 'delete_station', 'sid': sdata['sid']})
            else:
                self._contextmenu(self.STR(30102), {'action': 'delete_from_top', 'sid': sdata['sid']})
        else:
            self._contextmenu(self.STR(30101), {'action': 'add_to_top', 'sid': sdata['sid']})
        if self.GET('download') == 'true' and sdata['type'] in ('nhkr', 'radk'):
            self._contextmenu(self.STR(30106), {'action': 'set_keyword', 'sid': sdata['sid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ストリームURL
        url = LocalProxy.proxy(sdata['type'], abbr=sdata['abbr'], direct=sdata['direct'], token=self.token)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _add_keyword(self, kid, keyword, dirname):
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
        
    def _title(self, data):
        if data['type'] in ('nhkr', 'radk'):
            station = data['station']
            sql = 'SELECT title, start, end FROM contents WHERE sid = :sid AND end > NOW() ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': data['sid']})
            try:
                (title, start, end) = self.db.cursor.fetchone()
                station += f' [COLOR khaki]▶ {title} ({start[11:16]}～{end[11:16]})[/COLOR]'
                (title, start, end) = self.db.cursor.fetchone()
                station += f' [COLOR lightgreen]▶ {title} ({start[11:16]}～{end[11:16]})[/COLOR]'
            except:
                pass
        elif data['type'] in ('csra', 'jcba', 'fmpp', 'lsnr'):
            station = f"{data['station']}({data['pref']}{data['city']})"
            if data['description']:
                station += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        else:
            station = data['station']
            if data['description']:
                station += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        return station

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
