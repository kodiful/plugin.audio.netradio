# -*- coding: utf-8 -*-

import sys
import os
import locale
from urllib.parse import urlencode

import xbmc
import xbmcplugin
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.rss import Keywords, Stations


class Contents(Common):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # ロケール設定
        locale.setlocale(locale.LC_ALL, '')

    def show(self, kid=0, protocol='', station=''):
        if kid > 0:
            sql = '''SELECT *
            FROM contents AS c 
            JOIN keywords AS k ON c.kid = k.kid
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 AND c.kid = :kid 
            ORDER BY c.start DESC'''
            self.db.cursor.execute(sql, {'kid': kid})
        if protocol != '' and station != '':
            sql = '''SELECT *
            FROM contents AS c
            JOIN keywords AS k ON c.kid = k.kid
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 AND c.kid = -1 AND s.protocol = :protocol AND s.station = :station
            ORDER BY c.start DESC'''
            self.db.cursor.execute(sql, {'protocol': protocol, 'station': station})
        for cksdata in self.db.cursor.fetchall():
            # リストアイテムを追加
            self._add_download(cksdata)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        # statusテーブルに格納されている表示中の放送局をクリア
        self.db.cursor.execute("UPDATE status SET front = '[]'")

    def delete(self, cid):
        # 削除するファイルの情報を取得
        sql = '''SELECT *
        FROM contents c 
        JOIN keywords k ON c.kid = k.kid
        WHERE c.cid = :cid'''
        self.db.cursor.execute(sql, {'cid': cid})
        ckdata = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno(self.STR(30150), self.STR(30151) % ckdata['title'])
        if ok:
            # ファイルを削除
            path = os.path.join(self.CONTENTS_PATH, ckdata['dirname'], ckdata['filename'])
            if os.path.exists(path):
                os.remove(path)
            # DBから削除
            sql = 'DELETE FROM contents WHERE cid = :cid'
            self.db.cursor.execute(sql, {'cid': cid})
            self.refresh()
    
    def confirm_play(self, path):
        ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30158))
        if ok:
            xbmc.executebuiltin('PlayMedia(%s)' % path)
    
    def confirm_cancel(self, cid):
        ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30159))
        if ok:
            # タイマー予約を削除
            result = self.db.cursor.execute('DELETE FROM contents WHERE cid = :cid AND kid = -1', {'cid': cid})
            if result.rowcount == 0:
                # タイマー予約の削除ができないときは、キーワード予約の設定をリセット
                self.db.cursor.execute('UPDATE contents SET cstatus = 0, kid = 0 WHERE cid = :cid AND kid > 0', {'cid': cid})
            self.refresh()

    def show_error(self, cid):
        ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30160))
        if ok:
            self.db.cursor.execute('SELECT description FROM contents WHERE cid = :cid', {'cid': cid})
            description, = self.db.cursor.fetchone()
            xbmcgui.Dialog().textviewer(self.STR(30153), description)

    def _add_download(self, cksdata):
        cstatus = cksdata['cstatus']
        # listitemを追加する    
        li = xbmcgui.ListItem(self._title(cksdata))
        if cstatus == -1:
            li.setProperty('IsPlayable', 'true')
        # メタデータ設定
        tag = li.getMusicInfoTag()
        tag.setTitle(cksdata['title'])
        # サムネイル設定
        logo = os.path.join(self.PROFILE_PATH, 'stations', 'logo', cksdata['protocol'], cksdata['station'] + '.png')
        li.setArt({'thumb': logo, 'icon': logo})
        # コンテクストメニュー
        self.contextmenu = []
        if cstatus < 0:
            self._contextmenu(self.STR(30112), {'action': 'delete_download', 'cid': cksdata['cid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # 再生するファイルのパス
        path = os.path.join(self.CONTENTS_PATH, cksdata['dirname'], cksdata['filename'])
        if cstatus == -1:  # 正常
            url = path
        elif cstatus > 1:  # 保存中
            query = urlencode({'action': 'confirm_play', 'path': path})
            url = '%s?%s' % (sys.argv[0], query)
        elif cstatus == 1:  # 予約中
            query = urlencode({'action': 'confirm_cancel', 'cid': cksdata['cid']})
            url = '%s?%s' % (sys.argv[0], query)
        else:  # エラー
            query = urlencode({'action': 'show_error', 'cid': cksdata['cid']})
            url = '%s?%s' % (sys.argv[0], query)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _title(self, ckdata):
        # %Y年%m月%d日(%%s) %H:%M
        format = self.STR(30919)
        # 月,火,水,木,金,土,日
        weekdays = self.STR(30920)
        weekdays = weekdays.split(',')
        # 放送開始時刻
        #d = datetime.strptime(ckdata['start'], '%Y-%m-%d %H:%M:%S')
        #w = d.weekday()
        d = self.datetime(ckdata['start'])
        w = self.weekday(ckdata['start'])
        # 放送終了時刻
        end = ckdata['end'][11:16]
        # 8月31日(土)
        format = d.strftime(format)
        date = format % weekdays[w]
        # カラー
        if ckdata['cstatus'] > 1:  # 保存中
            title = '[COLOR white]%s-%s[/COLOR]  [COLOR white]%s[/COLOR]' % (date, end, ckdata['title'])
        elif ckdata['cstatus'] == 1:  # 予約中
            title = '[COLOR lightgray]%s-%s[/COLOR]  [COLOR lightgray]%s[/COLOR]' % (date, end, ckdata['title'])
        elif ckdata['cstatus'] < -1:  # エラー
            title = '[COLOR gray]%s-%s[/COLOR]  [COLOR gray]%s[/COLOR]' % (date, end, ckdata['title'])
        elif w == 6 or self.db.is_holiday(d.strftime('%Y-%m-%d')):
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        elif w == 5:
            title = '[COLOR blue]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        else:
            title = '%s-%s  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        return title

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def update_rss(self, notify=False):
        # RSS設定がされていない場合は終了
        if self.GET('rss') == 'false': return
        # キーワードRSS作成
        sql = '''SELECT DISTINCT k.keyword, k.dirname
        FROM contents AS c JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cstatus = -1 AND c.kid > 0'''
        self.db.cursor.execute(sql)
        for keyword, dirname in self.db.cursor.fetchall():
            Keywords(keyword, dirname).create_rss()
        # キーワードインデクス作成
        Keywords().create_index()
        # 放送局RSS作成
        sql = '''SELECT DISTINCT s.protocol, c.station
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid
        WHERE c.cstatus = -1 AND c.kid = -1'''
        self.db.cursor.execute(sql)
        for protocol, station in self.db.cursor.fetchall():
            Stations(protocol, station).create_rss()
        # 放送局インデクス作成
        Stations().create_index()
        # 完了通知
        if notify:
            self.notify('RSS has been updated')
