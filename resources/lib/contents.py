# -*- coding: utf-8 -*-

import sys
import os
import re
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

    def show(self, kid=0, protocol='', station='', date=''):
        if kid > 0:
            sql = '''SELECT *
            FROM contents AS c
            JOIN keywords AS k ON c.kid = k.kid
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 AND c.kid = :kid
            ORDER BY SUBSTR(c.start, 1, 10) DESC, SUBSTR(c.start, 12) ASC'''
            self.db.cursor.execute(sql, {'kid': kid})
        if protocol != '' and station != '':
            sql = '''SELECT *
            FROM contents AS c
            JOIN keywords AS k ON c.kid = k.kid
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 AND s.protocol = :protocol AND s.station = :station
            ORDER BY SUBSTR(c.start, 1, 10) DESC, SUBSTR(c.start, 12) ASC'''
            self.db.cursor.execute(sql, {'protocol': protocol, 'station': station})
        if date != '':
            sql = '''SELECT *
            FROM contents AS c
            JOIN keywords AS k ON c.kid = k.kid
            JOIN stations AS s ON c.sid = s.sid
            WHERE c.cstatus != 0 AND SUBSTR(c.start, 1, 10) = :date
            ORDER BY SUBSTR(c.start, 1, 10) DESC, SUBSTR(c.start, 12) ASC'''
            self.db.cursor.execute(sql, {'date': date})
        for cksdata in self.db.cursor.fetchall():
            # リストアイテムを追加
            self._add_download(cksdata)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        # statusテーブルに格納されている表示中の放送局をクリア
        self.db.cursor.execute("UPDATE status SET front = '[]'")

    def delete(self, cid):
        # 削除するファイルの情報を取得
        sql = '''SELECT k.dirname, s.protocol, s.station, c.filename, c.title
        FROM contents AS c
        JOIN stations AS s ON c.sid = s.sid
        JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cid = :cid'''
        self.db.cursor.execute(sql, {'cid': cid})
        dirname, protocol, station, filename, title = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno(self.STR(30150), self.STR(30151) % title)
        if ok:
            # ファイルを削除
            path = os.path.join(self.CONTENTS_PATH, dirname, protocol, station, filename)
            if os.path.exists(path):
                os.remove(path)
            # DBから削除
            sql = 'DELETE FROM contents WHERE cid = :cid'
            self.db.cursor.execute(sql, {'cid': cid})
            self.refresh()

    def play(self, cid):
        # 再生するファイルの情報を取得
        sql = '''SELECT c.cstatus, k.dirname, s.protocol, s.station, c.filename
        FROM contents AS c
        JOIN stations AS s ON c.sid = s.sid
        JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cid = :cid'''
        self.db.cursor.execute(sql, {'cid': cid})
        cstatus, dirname, protocol, station, filename = self.db.cursor.fetchone()
        # ファイルのパス
        path = os.path.join(self.CONTENTS_PATH, dirname, protocol, station, filename)
        # cstatusに応じて処理
        if cstatus == -1:  # 正常
            xbmc.executebuiltin('PlayMedia("%s")' % path)
        elif cstatus > 1:  # 保存中
            ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30158))  # 保存中です。保存を継続したまま再生しますか？
            if ok:
                xbmc.executebuiltin('PlayMedia("%s")' % path)
        elif cstatus == 1:  # 予約中
            ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30159))  # 保存を待機中です。保存をキャンセルしますか？
            if ok:
                # タイマー予約を削除
                result = self.db.cursor.execute('DELETE FROM contents WHERE cid = :cid AND kid = -1', {'cid': cid})
                if result.rowcount == 0:
                    # タイマー予約の削除ができないときは、キーワード予約の設定をリセット
                    self.db.cursor.execute('UPDATE contents SET cstatus = 0, kid = 0 WHERE cid = :cid AND kid > 0', {'cid': cid})
                self.refresh()
        else:  # エラー
            ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30160))  # 保存を失敗したため再生できません。エラー情報を表示しますか？
            if ok:
                self.db.cursor.execute('SELECT description FROM contents WHERE cid = :cid', {'cid': cid})
                description, = self.db.cursor.fetchone()
                xbmcgui.Dialog().textviewer(self.STR(30153), description)

    def info(self, cid):
        # 番組情報を検索
        sql = 'SELECT description FROM contents WHERE cid = :cid'
        self.db.cursor.execute(sql, {'cid': cid})
        description, = self.db.cursor.fetchone()
        # テキストを整形
        description = self.sanitize(description) if description else self.STR(30610)
        xbmcgui.Dialog().textviewer(self.STR(30609), description)

    def _add_download(self, cksdata):
        cstatus = cksdata['cstatus']
        # listitemを追加する
        li = xbmcgui.ListItem(self._title(cksdata))
        # メタデータ設定
        tag = li.getMusicInfoTag()
        tag.setTitle(cksdata['title'])
        # サムネイル設定
        logo = os.path.join(self.PROFILE_PATH, 'stations', 'logo', cksdata['protocol'], cksdata['station'] + '.png')
        li.setArt({'thumb': logo, 'icon': logo})
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30111), {'action': 'info_download', 'cid': cksdata['cid']})
        if cstatus == -1:
            self._contextmenu(self.STR(30112), {'action': 'delete_download', 'cid': cksdata['cid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # ファイル再生
        query = urlencode({'action': 'play_download', 'cid': cksdata['cid']})
        url = '%s?%s' % (sys.argv[0], query)
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _title(self, ckdata):
        # 日付
        d = self.datetime(ckdata['start'])
        w = self.weekday(ckdata['start'])
        date = d.strftime(self.STR(30918)) % self.STR(30920).split(',')[w]  # 2025年03月06日(木)
        # 時刻
        start = ckdata['start'][11:16]
        end = ckdata['end'][11:16]
        # タイトル
        title = ckdata['title']
        cstatus = ckdata['cstatus']
        if cstatus > 1:  # 保存中
            title = f'[COLOR white]{date} {start}-{end}[/COLOR]  [COLOR white]{title}[/COLOR]'
        elif cstatus == 1:  # 予約中
            title = f'[COLOR lightgray]{date} {start}-{end}[/COLOR]  [COLOR lightgray]{title}[/COLOR]'
        elif cstatus < -1:  # エラー
            title = f'[COLOR gray]{date} {start}-{end}[/COLOR]  [COLOR gray]{title}[/COLOR]'
        elif w == 6 or self.db.is_holiday(d.strftime('%Y-%m-%d')):
            title = f'[COLOR red]{date} {start}-{end}[/COLOR]  [COLOR khaki]{title}[/COLOR]'
        elif w == 5:
            title = f'[COLOR blue]{date} {start}-{end}[/COLOR]  [COLOR khaki]{title}[/COLOR]'
        else:
            title = f'{date} {start}-{end}  [COLOR khaki]{title}[/COLOR]'
        return title

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def update_rss(self, notify=False):
        # RSS設定がされていない場合は終了
        if self.is_enabled('rss') is False: return
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
        WHERE c.cstatus = -1'''
        self.db.cursor.execute(sql)
        for protocol, station in self.db.cursor.fetchall():
            Stations(protocol, station).create_rss()
        # 放送局インデクス作成
        Stations().create_index()
        # 完了通知
        if notify:
            self.notify('RSS has been updated')
