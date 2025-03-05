# -*- coding: utf-8 -*-

import sys
import os
import re
from qrcode import QRCode
from sqlite3 import dbapi2 as sqlite
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.db import ThreadLocal
from resources.lib.localproxy import LocalProxy
from resources.lib.managers import ScheduleManager


class Directory(ScheduleManager):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # radiko認証
        sql = "SELECT auth_token, region, pref FROM auth JOIN cities ON auth.area_id = cities.area_id WHERE cities.city = ''"
        self.db.cursor.execute(sql)
        self.token, self.region, self.pref = self.db.cursor.fetchone()

    def show(self, protocol=None, region=None, pref=None):
        # 表示中の放送局を格納するリスト
        front = []
        # 番組表取得フラグ
        stations = []
        # 表示
        if protocol == 'NHK':
            # NHKの放送局一覧を表示
            sql = 'SELECT * FROM stations WHERE protocol = :protocol AND vis = 1 ORDER BY key'
            self.db.cursor.execute(sql, {'protocol': 'NHK'})
            for sdata in self.db.cursor.fetchall():
                self._add_station_onair(sdata)
                stations.append((sdata['protocol'], sdata['sid'], 1))
        elif protocol == 'RDK':
            # RDKの放送局一覧を表示
            sql = 'SELECT * FROM stations WHERE protocol = :protocol AND vis = 1 ORDER BY key'
            self.db.cursor.execute(sql, {'protocol': 'RDK'})
            for sdata in self.db.cursor.fetchall():
                self._add_station_onair(sdata)
                stations.append((sdata['protocol'], sdata['sid'], 1))
        elif protocol == 'COMM':
            protocols = "('LR', 'SJ', 'SP', 'SR', 'SD')"
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
                sql = 'SELECT * FROM stations WHERE protocol IN %s AND region = :region AND pref = :pref AND vis = 1 ORDER BY code' % protocols
                self.db.cursor.execute(sql, {'region': region, 'pref': pref})
                for sdata in self.db.cursor.fetchall():
                    self._add_station_onair(sdata)
                    stations.append((sdata['protocol'], sdata['sid'], 1))
        elif protocol == 'keyword':
            # 保存ファイルのキーワード一覧を表示
            sql = 'SELECT kid, keyword, dirname FROM keywords WHERE kid > 0 ORDER BY kid DESC'
            self.db.cursor.execute(sql)
            for kid, keyword, dirname in self.db.cursor.fetchall():
                self._add_keyword_item(kid, keyword, dirname)
        elif protocol == 'station':
            # 保存ファイルの放送局一覧を表示
            sql = '''SELECT DISTINCT s.protocol, s.station
            FROM contents AS c 
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 ORDER BY
            CASE s.protocol
                WHEN 'NHK' THEN 1
                WHEN 'RDK' THEN 2
                WHEN 'SJ' THEN 3
                WHEN 'LR' THEN 3
                WHEN 'SP' THEN 3
                WHEN 'SR' THEN 3
                WHEN 'SD' THEN 3
                WHEN 'USER' THEN 4
                ELSE 9
            END, s.code, s.key'''
            self.db.cursor.execute(sql)
            for protocol, station in self.db.cursor.fetchall():
                self._add_station_item(protocol, station)
        else:
            # トップ画面の放送局一覧を表示
            sql = '''SELECT * FROM stations WHERE top = 1 AND vis = 1 ORDER BY
            CASE protocol
                WHEN 'NHK' THEN 1
                WHEN 'RDK' THEN 2
                WHEN 'SJ' THEN 3
                WHEN 'LR' THEN 3
                WHEN 'SP' THEN 3
                WHEN 'SR' THEN 3
                WHEN 'SD' THEN 3
                WHEN 'USER' THEN 4
                ELSE 9
            END, code, key'''
            self.db.cursor.execute(sql)
            for sdata in self.db.cursor.fetchall():
                self._add_station_onair(sdata)
                stations.append((sdata['protocol'], sdata['sid'], 1))
            # ディレクトリの一覧を表示
            self._setup_directory()
            # アーカイブの一覧を表示
            if self.GET('download') == 'true':
                self._setup_archives()
        # 番組表取得
        self.maintain_schedule(stations)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

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
            description = re.sub(r' *\n *', r'\n', description)
            description = re.sub(r'\n{3,}', r'\n\n', description)
        else:
            description = self.STR(30610)
        xbmcgui.Dialog().textviewer(self.STR(30609), description)

    def show_qrcode(self, url):
        path = os.path.join(self.PROFILE_PATH, 'qr.png')
        self._qrcode(url, path, True)
        xbmc.executebuiltin('ShowPicture(%s)' % path)

    def showhide(self, sid, top):
        sql = 'UPDATE stations SET top = :top WHERE (protocol, station) = (SELECT protocol, station FROM stations WHERE sid = :sid)'
        self.db.cursor.execute(sql, {'sid': sid, 'top': top})
        self.refresh(top)  # トップに追加したときはトップ画面へ

    def _setup_directory(self):
        # NHKラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30001))
        self.setArt(li, 'satellite')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_stations', 'protocol': 'NHK', 'region': self.region})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 民放ラジオ(radiko)
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30002))
        self.setArt(li, 'satellite')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_stations', 'protocol': 'RDK', 'region': self.region, 'pref': self.pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # コミュニティラジオ
        li = xbmcgui.ListItem('[COLOR orange]%s[/COLOR]' % self.STR(30003))
        self.setArt(li, 'satellite')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_stations', 'protocol': 'COMM'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _setup_archives(self):
        # 保存ファイル（キーワード別）
        li = xbmcgui.ListItem('[COLOR lightgreen]%s[/COLOR]' % self.STR(30010))
        self.setArt(li, 'set')
        # コンテクストメニュー
        self.contextmenu = []
        if self.GET('rss') == 'true':
            url = '/'.join([self.GET('rssurl'), 'keywords.xml'])
            self._contextmenu(self.STR(30118), {'action': 'show_qrcode', 'url': url})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_stations', 'protocol': 'keyword'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
        # 保存ファイル（キーワード別）
        li = xbmcgui.ListItem('[COLOR lightgreen]%s[/COLOR]' % self.STR(30011))
        self.setArt(li, 'set')
        # コンテクストメニュー
        self.contextmenu = []
        if self.GET('rss') == 'true':
            url = '/'.join([self.GET('rssurl'), 'stations.xml'])
            self._contextmenu(self.STR(30118), {'action': 'show_qrcode', 'url': url})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        query = urlencode({'action': 'show_stations', 'protocol': 'station'})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
    
    def _add_directory(self, region, pref=None):
        # listitemを追加する
        li = xbmcgui.ListItem(pref or region)
        # サムネイル画像
        self.setArt(li, 'satellite')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        if pref is None:
            query = urlencode({'action': 'show_stations', 'protocol': 'COMM', 'region': region})
        else:
            query = urlencode({'action': 'show_stations', 'protocol': 'COMM', 'region': region, 'pref': pref})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station_onair(self, sdata):
        # listitemを追加する
        li = xbmcgui.ListItem(self._title(sdata))
        li.setProperty('IsPlayable', 'true')
        # メタデータ設定
        tag = li.getMusicInfoTag()
        tag.setTitle(sdata['station'])
        # サムネイル設定
        #self.setArt(li, 'audiodsp')
        image = os.path.join(self.PROFILE_PATH, 'stations', 'logo', sdata['protocol'], sdata['station'] + '.png')
        li.setArt({'thumb': image, 'icon': image})
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30111), {'action': 'show_info', 'sid': sdata['sid']})
        self._contextmenu(self.STR(30105), {'action': 'get_download', 'sid': sdata['sid']})
        self._contextmenu(self.STR(30104), {'action': 'get_station', 'sid': sdata['sid']})
        if sdata['protocol'] != 'USER':
            if sdata['top'] == 0:
                self._contextmenu(self.STR(30120), {'action': 'add_to_top', 'sid': sdata['sid']})
            else:
                self._contextmenu(self.STR(30121), {'action': 'delete_from_top', 'sid': sdata['sid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ストリームURL
        url = LocalProxy.proxy(sdata['protocol'], key=sdata['key'], direct=sdata['direct'], token=self.token)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _add_keyword_item(self, kid, keyword, dirname):
        # listitemを追加する
        li = xbmcgui.ListItem(keyword)
        # サムネイル画像
        self.setArt(li, 'playlist')
        # コンテクストメニュー
        self.contextmenu = []
        if kid > 0:
            self._contextmenu(self.STR(30108), {'action': 'get_keyword', 'kid': kid})
        if self.GET('rss') == 'true':
            url = '/'.join([self.GET('rssurl'), dirname, 'rss.xml'])
            self._contextmenu(self.STR(30118), {'action': 'show_qrcode', 'url': url})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # リストアイテムを追加
        query = urlencode({'action': 'show_downloads', 'kid': kid})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)

    def _add_station_item(self, protocol, station):
        # listitemを追加する
        li = xbmcgui.ListItem(station)
        # サムネイル画像
        self.setArt(li, 'satellite')
        image = os.path.join(self.PROFILE_PATH, 'stations', 'logo', protocol, station + '.png')
        li.setArt({'thumb': image, 'icon': image})
        # コンテクストメニュー
        self.contextmenu = []
        if self.GET('rss') == 'true':
            url = '/'.join([self.GET('rssurl'), '0', protocol, station, 'rss.xml'])
            self._contextmenu(self.STR(30118), {'action': 'show_qrcode', 'url': url})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # リストアイテムを追加
        query = urlencode({'action': 'show_downloads', 'protocol': protocol, 'station': station})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], query), listitem=li, isFolder=True)
     
    def _title(self, sdata):
        # コミュニティ放送局用に都市名を追加
        basename = sdata['station']
        if sdata['protocol'] not in ('NHK', 'RDK', 'USER'):
            basename += '(%s)' % sdata['city']
        station = basename
        # 番組情報等を追加
        sql = '''SELECT title, start, end
        FROM contents
        WHERE sid = :sid AND end > NOW() AND kid > -1
        ORDER BY start LIMIT 2'''
        self.db.cursor.execute(sql, {'sid': sdata['sid']})
        contents = [(title, start, end) for title, start, end in self.db.cursor.fetchall()][:2]
        colors = ['khaki', 'lightgreen']
        for (title, start, end), color in zip(contents, colors):
            text = f'{title} ({start[11:16]}～{end[11:16]})'
            station += f'[COLOR {color}] ▶ {text}[/COLOR]'
        # 番組情報が取得できない場合
        if len(contents) == 0:
            self.db.cursor.execute('SELECT nextaired0, nextaired1 FROM stations WHERE sid = :sid', {'sid': sdata['sid']})
            _, nextaired1 = self.db.cursor.fetchone()
            if nextaired1 < self.now():
                # 取得中表示
                text = self.STR(30700)
                station += f'[COLOR gray] ▶ {text}[/COLOR]'
            elif sdata['description']:
                # 代替テキストを表示
                text = sdata['description']
                station += f'[COLOR khaki] ■ {text}[/COLOR]'
        return station

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def _qrcode(self, url, path, force=False):
        # ファイルを削除
        if force and os.path.exists(path):
            os.remove(path)
        # DBから画像のキャッシュを削除
        conn = sqlite.connect(self.IMAGE_CACHE)
        sql = 'DELETE FROM texture WHERE url = :path'
        conn.cursor().execute(sql, {'path': path})
        conn.commit()
        conn.close()
        # 画像がある場合はなにもしない
        if os.path.exists(path):
            return
        # 画像格納用のディレクトリを用意
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # 画像を生成
        qr = QRCode(version=1, box_size=10, border=4)
        qr.add_data(re.sub(r'^http(s?)://', r'podcast\1://', url))
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(path, 'PNG')
