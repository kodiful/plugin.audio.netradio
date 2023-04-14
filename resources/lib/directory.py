# -*- coding: utf-8 -*-

import sys
import os
import glob
import shutil
import time

from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.prefdata import PrefData
from resources.lib.localproxy import LocalProxy

import xbmc
import xbmcgui
import xbmcplugin


class Directory(Common, PrefData):

    def __init__(self):
        auth = self.read_as_json(self.AUTH_FILE)
        self.token = auth['auth_token']
        _, self.region, self.pref = self.radiko_place(auth['area_id'])

    def show(self, path=None):
        if path is None:
            # 放送局
            self._setup_stations()
            # ディレクトリ
            self._setup_directory()
            # キーワード
            self._setup_keywords()
        else:
            # サブディレクトリ
            items = glob.glob(os.path.join(self.DIRECTORY_PATH, path, '*'))
            for item in sorted(items, key=self._sort):
                if os.path.isdir(item):
                    # リストの要素がディレクトリの場合
                    self._add_directory(path, item)
                else:
                    # リストの要素がファイルの場合
                    self._add_station(path, item)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def add_to_top(self, path):
        name = os.path.basename(path)
        dest = os.path.join(self.DIRECTORY_PATH, name)
        if os.path.isfile(dest) is False:
            shutil.copy(path, dest)
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    def delete_from_top(self, path):
        os.remove(path)
        xbmc.executebuiltin('Container.Refresh')

    def _setup_stations(self):
        # ユーザが設定した放送局を追加
        items = glob.glob(os.path.join(self.DIRECTORY_PATH, '*.json'))
        for item in sorted(items, key=self._sort):
            self._add_station(None, item)
    
    def _setup_keywords(self):
        # キーワードを追加
        items = glob.glob(os.path.join(self.KEYWORDS_PATH, '*.json'))
        for item in sorted(items):
            self._add_keyword(item)

    def _setup_directory(self):
        # NHKラジオ
        li = xbmcgui.ListItem('[COLOR orange]NHKラジオ[/COLOR]')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show', 'path': os.path.join('NHKラジオ', self.region)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 民放ラジオ(radiko)
        li = xbmcgui.ListItem('[COLOR orange]民放ラジオ(radiko)[/COLOR]')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show', 'path': os.path.join('民放ラジオ(radiko)', self.region, self.pref)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # コミュニティラジオ
        li = xbmcgui.ListItem('[COLOR orange]コミュニティラジオ[/COLOR]')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show', 'path': os.path.join('コミュニティラジオ')})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
    
    def _add_directory(self, path, item):
        name = os.path.basename(item)
        li = xbmcgui.ListItem(name)
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show', 'path': os.path.join(path, name)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station(self, path, item):
        # jsonファイルからデータを取得する
        data = self.read_as_json(item)
        # listitemを追加する
        if data['type'] in ('nhk1', 'nhk2', 'nhk3', 'radk'):
            name = self._name(data)
        elif data['type'] in ('csra', 'jcba', 'lsnr', 'siml'):
            name = f"{data['name']}({data['pref']}{data['city']})"
            if data['description']:
                name += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        else:
            name = data['name']
            if data['description']:
                name += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        li = xbmcgui.ListItem(name)
        logo = os.path.join(self.LOGO_PATH, data['type'], '%s.png' % data['name'])
        li.setArt({'thumb': logo, 'poster': logo, 'banner': logo, 'fanart': logo, 'clearart': logo, 'clearlogo': logo, 'landscape': logo, 'icon': logo})
        labels = {'title': data['name']}
        li.setInfo(type='music', infoLabels=labels)
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        if path is None:
            if data['type'] == 'user':
                self._contextmenu('放送局の設定を変更する', {'action': 'set_station', 'path': item})
            else:
                self._contextmenu('放送局を追加する', {'action': 'set_station'})
            self._contextmenu('トップ画面から削除する', {'action': 'delete_from_top', 'path': item})
        else:
            self._contextmenu('トップ画面に追加する', {'action': 'add_to_top', 'path': item})
        if data['type'] in ('nhk1', 'nhk2', 'nhk3', 'radk'):
            self._contextmenu('キーワードを追加する', {'action': 'set_keyword', 'path': os.path.join(self.TIMETABLE_PATH, data['type'], f'%s.json' % data['name'])})
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ストリームURL
        if data['type'] == 'radk':
            stream = LocalProxy.proxy_radk(data['id'], self.token)
        elif data['type'] == 'jcba':
            stream = LocalProxy.proxy_jcba(data['id'])
        else:
            stream = data['stream']
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), stream, listitem=li, isFolder=False)

    def _add_keyword(self, item):
        # jsonファイルからデータを取得する
        data = self.read_as_json(item)
        # listitemを追加する
        name = data['keyword']
        li = xbmcgui.ListItem(name)
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('キーワードの設定を変更する', {'action': 'set_keyword', 'path': item})
        self._contextmenu('トップ画面から削除する', {'action': 'delete_from_top', 'path': item})
        self._contextmenu('アドオン設定', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # リストアイテムを追加
        query = urlencode({'action': 'show', 'path': os.path.join(self.GET('folder'), name)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _sort(self, item):
        if os.path.isfile(item):
            # ソートキー
            key = {
                'nhk1': 1,
                'nhk2': 2,
                'nhk3': 3,
                'radk': 4,
                'csra': 5,
                'jcba': 5,
                'lsnr': 5,
                'siml': 5,
                'user': 9
            }
            # type, code, nameでソートする
            data = self.read_as_json(item)
            key1 = key[data['type']]
            key2 = data['code']
            key3 = data['name']
            return key1, key2, key3
        else:
            # ディレクトリの場合
            children = glob.glob(os.path.join(item, '*'))
            return self._sort(min(children))
        
    def _name(self, item):
        # 放送局名
        color = None
        name = item['name']
        if item['type'] == 'radk' and item['pref'] != self.pref:
            # 認証された地域と一致しない場合はグレイ表示
            color = 'gray'
            name = f'[COLOR {color}]{name}[/COLOR]'
        progs = self.read_as_json(os.path.join(self.TIMETABLE_PATH, item['type'], f'%s.json' % item['name']))
        for i, p in enumerate(progs):
            title = '%s (%s～%s)' % (p['title'], self._time(p['start']), self._time(p['end']))
            if i == 0:
                color1 = color or 'khaki'
                name += f' [COLOR {color1}]▶ {title}[/COLOR]'
            else:
                color2 = color or 'lightgreen'
                name += f' [COLOR {color2}]▶ {title}[/COLOR]'
        return name
    
    def _time(self, t):
        return time.strftime("%H:%M", time.localtime(t))
    
    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))