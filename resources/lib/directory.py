# -*- coding: utf-8 -*-

import sys
import os
import glob
import shutil
import time
import re
import platform

from urllib.parse import urlencode
from qrcode import QRCode
from sqlite3 import dbapi2 as sqlite

from resources.lib.common import Common
from resources.lib.prefecture import Prefecture
from resources.lib.localproxy import LocalProxy

import xbmc
import xbmcgui
import xbmcplugin

class Directory(Common, Prefecture):

    def __init__(self):
        # radiko認証
        auth = self.read_as_json(self.AUTH_FILE)
        self.token = auth['auth_token']
        _, self.region, self.pref = self.radiko_place(auth['area_id'])
        # キーワード設定
        self.dlsupport = platform.system() in ('Windows', 'Darwin') and self.GET('download') == 'true'

    def show(self, path=None):
        if path is None:
            # 放送局
            self._setup_stations()
            # ディレクトリ
            self._setup_directory()
            # キーワード
            if self.dlsupport:
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
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30001))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'path': os.path.join(self.STR(30001), self.region)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 民放ラジオ(radiko)
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30002))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'path': os.path.join(self.STR(30002), self.region, self.pref)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # コミュニティラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30003))
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'path': os.path.join(self.STR(30003))})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
    
    def _add_directory(self, path, item):
        name = os.path.basename(item)
        li = xbmcgui.ListItem(name)
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu('self.STR(30100)', {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_station', 'path': os.path.join(path, name)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station(self, path, item):
        # jsonファイルからデータを取得する
        data = self.read_as_json(item)
        # listitemを追加する
        li = xbmcgui.ListItem(self._title(data))
        logo = os.path.join(self.LOGO_PATH, data['type'], '%s.png' % data['station'])
        li.setArt({'thumb': logo, 'icon': logo})
        li.setInfo(type='music', infoLabels={'title': data['station']})
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        if path is None:
            if data['type'] in ('nhkr', 'radk'):
                self._contextmenu(self.STR(30110), {'action': 'update_info'})
            if data['type'] == 'user':
                self._contextmenu(self.STR(30104), {'action': 'set_station', 'path': item})
                self._contextmenu(self.STR(30105), {'action': 'delete_from_top', 'path': item})
            else:
                self._contextmenu(self.STR(30102), {'action': 'delete_from_top', 'path': item})
        else:
            self._contextmenu(self.STR(30101), {'action': 'add_to_top', 'path': item})
        if self.dlsupport and data['type'] in ('nhkr', 'radk'):
            self._contextmenu(self.STR(30106), {'action': 'set_keyword', 'path': os.path.join(self.TIMETABLE_PATH, data['type'], f'%s.json' % data['station'])})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ストリームURL
        stream = self._stream(data)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), stream, listitem=li, isFolder=False)

    def _add_keyword(self, item):
        # jsonファイルからデータを取得する
        data = self.read_as_json(item)
        # listitemを追加する
        name = data['keyword']
        li = xbmcgui.ListItem(name)
        logo = self._qrcode(data)
        li.setArt({'thumb': logo, 'icon': logo})
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30107), {'action': 'set_keyword', 'path': item})
        self._contextmenu(self.STR(30108), {'action': 'delete_from_top', 'path': item})
        self._contextmenu(self.STR(30109), {'action': 'open_folder', 'keyword': data['keyword']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # リストアイテムを追加
        query = urlencode({'action': 'show_download', 'path': os.path.join(self.GET('folder'), name)})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _sort(self, item):
        if os.path.isfile(item):
            # ソートキー
            data = self.read_as_json(item)
            key = {
                'nhkr': 1,
                'radk': 2,
                'csra': 3,
                'plap': 3,
                'jcba': 3,
                'lsnr': 3,
                'siml': 3,
                'user': 9
            }
            # type, code, nameでソートする
            key1 = key[data['type']]
            key2 = data['id'] if data['type'] == 'nhkr' else ''
            key3 = data['code']
            key4 = data['station']
            return key1, key2, key3, key4
        else:
            # ディレクトリの場合
            children = glob.glob(os.path.join(item, '*'))
            return self._sort(min(children))
        
    def _title(self, data):
        if data['type'] in ('nhkr', 'radk'):
            color = None
            station = data['station']
            if data['type'] == 'radk' and data['pref'] != self.pref:
                # 認証された地域と一致しない場合はグレイ表示
                color = 'gray'
                station = f'[COLOR {color}]{station}[/COLOR]'
            progs = self.read_as_json(os.path.join(self.TIMETABLE_PATH, data['type'], f'%s.json' % data['station']))
            for i, p in enumerate(progs):
                title = '%s (%s～%s)' % (p['title'], self._time(p['start']), self._time(p['end']))
                if i == 0:
                    color1 = color or 'khaki'
                    station += f' [COLOR {color1}]▶ {title}[/COLOR]'
                else:
                    color2 = color or 'lightgreen'
                    station += f' [COLOR {color2}]▶ {title}[/COLOR]'
        elif data['type'] in ('csra', 'jcba', 'plap', 'lsnr', 'siml'):
            station = f"{data['station']}({data['pref']}{data['city']})"
            if data['description']:
                station += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        else:
            station = data['station']
            if data['description']:
                station += f" [COLOR khaki]▶ {data['description']}[/COLOR]"
        return station
    
    def _time(self, t):
        return time.strftime("%H:%M", time.localtime(t))

    def _stream(self, data):
        if data['type'] == 'radk':
            stream = LocalProxy.proxy_radk(data['id'], token=self.token)
        elif data['type'] == 'jcba':
            stream = LocalProxy.proxy_jcba(data['id'])
        elif data['type'] == 'plap':
            stream = LocalProxy.proxy_plap(data['id'])
        else:
            stream = LocalProxy.proxy_redirect(data['stream'])
        return stream

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def _qrcode(self, data=None):
        if self.GET('rss') == 'false':
            return 'special://skin/extras/icons/search.png'
        if data is None:
            url = os.path.join(self.GET('rssurl'), 'rss.xml')
        else:
            url = os.path.join(self.GET('rssurl'), data['keyword'], 'rss.xml')
        path = os.path.join(self.KEYWORDS_PATH, '%s.png' % data['keyword'])
        # QRコードを生成
        qr = QRCode(version=1, box_size=10, border=4)
        qr.add_data(re.sub(r'^http(s?)://', r'podcast\1://', url))
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(path, 'PNG')
        # DBから画像のキャッシュを削除
        conn = sqlite.connect(self.IMAGE_CACHE)
        conn.cursor().execute("DELETE FROM texture WHERE url = '%s';" % path)
        conn.commit()
        conn.close()
        return path