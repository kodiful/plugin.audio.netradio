# -*- coding: utf-8 -*-

import sys
import os
import locale
import html
import shutil
from urllib.parse import urlencode

import xbmc
import xbmcplugin
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Contents(Common):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # ロケール設定
        locale.setlocale(locale.LC_ALL, '')

    def show(self, kid):
        sql = '''SELECT *
        FROM contents c 
        JOIN keywords k ON c.kid = k.kid
        JOIN stations s ON c.sid = s.sid
        WHERE c.kid = :kid AND c.cstatus != 0
        ORDER BY c.start DESC'''
        self.db.cursor.execute(sql, {'kid': kid})
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
            xbmc.executebuiltin('Container.Refresh')

    def cancel(self, cid):
        # キャンセルするファイルの情報を取得
        sql = '''SELECT *
        FROM contents c 
        JOIN keywords k ON c.kid = k.kid
        WHERE c.cstatus = 1 AND c.cid = :cid'''
        self.db.cursor.execute(sql, {'cid': cid})
        ckdata = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno(self.STR(30152), self.STR(30153) % ckdata['title'])
        if ok:
            # DBから削除
            sql = 'DELETE FROM contents WHERE cid = :cid'
            self.db.cursor.execute(sql, {'cid': cid})
            xbmc.executebuiltin('Container.Refresh')
    
    def alert(self, message):
        xbmcgui.Dialog().ok(self.STR(30160), message)

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
        elif cstatus == 1:
            self._contextmenu(self.STR(30117), {'action': 'cancel_download', 'cid': cksdata['cid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # 再生するファイルのパス
        if cstatus == -1:
            url = os.path.join(self.CONTENTS_PATH, cksdata['dirname'], cksdata['filename'])
        elif cstatus == 1:
            query = urlencode({'action': 'alert_download', 'message': self.STR(30161)})
            url = '%s?%s' % (sys.argv[0], query)
        elif cstatus > 1:
            query = urlencode({'action': 'alert_download', 'message': self.STR(30162)})
            url = '%s?%s' % (sys.argv[0], query)
        else:
            query = urlencode({'action': 'alert_download', 'message': self.STR(30163)})
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
        if ckdata['cstatus'] > 0:
            title = '[COLOR gray]%s-%s[/COLOR]  [COLOR gray]%s[/COLOR]' % (date, end, ckdata['title'])
        elif ckdata['cstatus'] < -1:
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR red]%s[/COLOR]' % (date, end, ckdata['title'])
        elif w == 6 or self.db.is_holiday(d.strftime('%Y-%m-%d')):
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        elif w == 5:
            title = '[COLOR blue]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        else:
            title = '%s-%s  [COLOR khaki]%s[/COLOR]' % (date, end, ckdata['title'])
        return title

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def update_rss(self):
        # RSS設定がされていない場合は終了
        if self.GET('rss') == 'false': return
        # RSS作成
        sql = 'SELECT kid, keyword, dirname FROM keywords'
        self.db.cursor.execute(sql)
        for kid, keyword, dirname in self.db.cursor.fetchall():
            self.create_rss(kid, keyword, dirname)
        # インデクス作成
        self.create_index()
        # 完了通知
        self.notify('RSS has been updated')

    def create_rss(self, kid, keyword, dirname):
        # RSS設定がされていない場合は終了
        if self.GET('rss') == 'false': return
        # templates
        with open(os.path.join(self.DATA_PATH, 'rss', 'header.xml'), 'r', encoding='utf-8') as f:
            header = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'body.xml'), 'r', encoding='utf-8') as f:
            body = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'footer.xml'), 'r', encoding='utf-8') as f:
            footer = f.read()
        # 時刻表記のロケール設定                                                                                                                                                             
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # open writer
        if os.path.exists(os.path.join(self.CONTENTS_PATH, dirname)) is False:
            os.makedirs(os.path.join(self.CONTENTS_PATH, dirname), exist_ok=True)
        writer = open(os.path.join(self.CONTENTS_PATH, dirname, 'rss.xml'), 'w', encoding='utf-8')
        # write header
        writer.write(header.format(image='icon.png', title=html.escape(keyword)))
        # body
        sql = '''SELECT filename, title, start, station, description, site, duration
        FROM contents
        WHERE kid = :kid AND cstatus = -1
        ORDER BY start DESC'''
        self.db.cursor.execute(sql, {'kid': kid})
        for filename, title, start, station, description, site, duration in self.db.cursor.fetchall():
            writer.write(
                body.format(
                    title=html.escape(title),
                    date=self._date(start),
                    url=site,
                    filename=filename,
                    description=html.escape(description),
                    pubdate=self._pubdate(start),
                    station=station,
                    duration='%02d:%02d:%02d' % (duration // 3600, duration // 60 % 60, duration % 60),
                    filesize=os.path.getsize(os.path.join(self.CONTENTS_PATH, dirname, filename))
                )
            )
        # write footer
        writer.write(footer)
        # close writer
        writer.close()
        # RSSから参照できるように、スタイルシートとアイコン画像をダウンロードフォルダにコピーする
        for filename in ('stylesheet.xsl', 'icon.png'):
            shutil.copy(os.path.join(self.DATA_PATH, 'rss', filename), os.path.join(self.CONTENTS_PATH, dirname, filename))

    def create_index(self):
        # templates
        with open(os.path.join(self.DATA_PATH, 'rss', 'header.xml'), 'r', encoding='utf-8') as f:
            header = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'body.xml'), 'r', encoding='utf-8') as f:
            body = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'footer.xml'), 'r', encoding='utf-8') as f:
            footer = f.read()
        # open writer
        if os.path.exists(os.path.join(self.CONTENTS_PATH)) is False:
            os.makedirs(os.path.join(self.CONTENTS_PATH), exist_ok=True)
        writer = open(os.path.join(self.CONTENTS_PATH, 'index.xml'), 'w', encoding='utf-8')
        # write header
        writer.write(header.format(image='icon.png', title='NetRadio Client'))
        # body
        sql = '''SELECT keyword, dirname FROM keywords ORDER BY 
        CASE kid
            WHEN -1 THEN 1
            ELSE 0
        END, keyword COLLATE NOCASE'''
        self.db.cursor.execute(sql, {})
        for keyword, dirname in self.db.cursor.fetchall():
            writer.write(
                body.format(
                    title=html.escape(keyword),
                    date='',
                    url=f'{dirname}/rss.xml',
                    filename='',
                    description='',
                    pubdate='',
                    station='',
                    duration='',
                    filesize=''
                )
            )
        # write footer
        writer.write(footer)
        # close writer
        writer.close()
        # RSSから参照できるように、スタイルシートとアイコン画像をダウンロードフォルダにコピーする
        for filename in ('stylesheet.xsl', 'icon.png'):
            shutil.copy(os.path.join(self.DATA_PATH, 'rss', filename), os.path.join(self.CONTENTS_PATH, filename))

    def _date(self, date):
        # "2023-04-20 14:00:00" -> "2023-04-20"
        return date[0:10]

    def _pubdate(self, date):
        # "2023-04-20 14:00:00" -> "Thu, 20 Apr 2023 14:00:00 +0900"
        pubdate = self.datetime(date).strftime('%a, %d %b %Y %H:%M:%S +0900')
        return pubdate
    