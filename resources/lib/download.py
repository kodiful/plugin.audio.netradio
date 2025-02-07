# -*- coding: utf-8 -*-

import sys
import os
import locale
import html
import time
import shutil
from datetime import datetime
from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.holiday import Holiday

import xbmcplugin
import xbmcgui


class Download(Common):

    def __init__(self):
        # DBのインスタンスを共有
        self.db = ThreadLocal.db
        # ロケール設定
        locale.setlocale(locale.LC_ALL, '')

    def show(self, kid):
        sql = '''SELECT * FROM contents c 
        JOIN keywords k ON c.kid = k.kid
        JOIN stations s ON c.sid = s.sid
        WHERE c.kid = :kid and c.status = -1
        ORDER BY c.start DESC'''
        self.db.cursor.execute(sql, {'kid': kid})
        for cksdata in self.db.cursor.fetchall():
            # リストアイテムを追加
            self._add_download(cksdata)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def _add_download(self, cksdata):
        li = xbmcgui.ListItem(self._title(cksdata))
        logo = os.path.join(self.PROFILE_PATH, 'stations', 'logo', str(cksdata['type']), str(cksdata['station']) + '.png')
        li.setArt({'thumb': logo, 'icon': logo})
        li.setInfo(type='music', infoLabels={'title': cksdata['title']})
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30109), {'action': 'open_folder', 'kid': cksdata['kid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # 再生するファイルのパス
        url = os.path.join(self.CONTENTS_PATH, cksdata['dirname'], cksdata['filename'])
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _title(self, ckdata):
        # %Y年%m月%d日(%%s) %H:%M
        format = self.STR(30919)
        # 月,火,水,木,金,土,日
        weekdays = self.STR(30920)
        weekdays = weekdays.split(',')
        # 放送開始時刻
        d = datetime.strptime(ckdata['start'], '%Y-%m-%d %H:%M:%S')
        w = d.weekday()
        # 放送終了時刻
        end = ckdata['end'][11:16]
        # 8月31日(土)
        format = d.strftime(format)
        date1 = format % weekdays[w]
        # 2019-08-31
        date2 = d.strftime('%Y-%m-%d')
        # カラー
        if date2 in Holiday.HOLIDAYS or w == 6:
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        elif w == 5:
            title = '[COLOR blue]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        else:
            title = '%s-%s  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        return title

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def update_rss(self):
        # RSS作成
        sql = 'SELECT kid, dirname FROM keywords WHERE status = -1'
        self.db.cursor.execute(sql)
        for kid, keyword, dirname in self.db.cursor.fetchall():
            self.create_rss(kid, keyword, dirname)
        # インデクス作成
        self.create_index()
        # 完了通知
        self.notify('RSS has been updated')

    def create_rss(self, kid, keyword, dirname):
        # templates
        with open(os.path.join(self.DATA_PATH, 'rss', 'header.xml'), 'r', encoding='utf-8') as f:
            header = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'body.xml'), 'r', encoding='utf-8') as f:
            body = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'footer.xml'), 'r', encoding='utf-8') as f:
            footer = f.read()
        # 時刻表記のロケール設定                                                                                                                                                             
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # open rss writer
        writer = open(os.path.join(self.CONTENTS_PATH, dirname, 'rss.xml'), 'w', encoding='utf-8')
        # write header
        writer.write(header.format(image='icon.png', title=keyword))
        # body
        sql = '''SELECT filename, title, start, station, description, site, duration
        FROM contents
        WHERE kid = :kid AND status = -1
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
        # close rss writer
        writer.close()
        # RSSから参照できるように、スタイルシートとアイコン画像をダウンロードフォルダにコピーする
        shutil.copy(os.path.join(self.DATA_PATH, 'rss', 'stylesheet.xsl'), os.path.join(self.CONTENTS_PATH, dirname, 'stylesheet.xsl'))
        shutil.copy(os.path.join(self.PLUGIN_PATH, 'icon.png'), os.path.join(self.CONTENTS_PATH, dirname, 'icon.png'))

    def create_index(self):
        # templates
        with open(os.path.join(self.DATA_PATH, 'rss', 'header.xml'), 'r', encoding='utf-8') as f:
            header = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'body.xml'), 'r', encoding='utf-8') as f:
            body = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'footer.xml'), 'r', encoding='utf-8') as f:
            footer = f.read()
        # open rss writer
        writer = open(os.path.join(self.CONTENTS_PATH, 'index.xml'), 'w', encoding='utf-8')
        # write header
        writer.write(header.format(image='icon.png', title='NetRadio Client'))
        # body
        sql = 'SELECT keyword, dirname FROM keywords ORDER BY keyword'
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
        # close rss writer
        writer.close()
        # RSSから参照できるように、スタイルシートとアイコン画像をダウンロードフォルダにコピーする
        shutil.copy(os.path.join(self.DATA_PATH, 'rss', 'stylesheet.xsl'), os.path.join(self.CONTENTS_PATH, 'stylesheet.xsl'))
        shutil.copy(os.path.join(self.PLUGIN_PATH, 'icon.png'), os.path.join(self.CONTENTS_PATH, 'icon.png'))

    def _date(self, date):
        # "2023-04-20 14:00:00" -> "2023-04-20"
        return f'{date[0:10]}'

    def _pubdate(self, date):
        # "2023-04-20 14:00:00" -> "Thu, 20 Apr 2023 14:00:00 +0900"
        try:
            pubdate = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            pubdate = pubdate.strftime('%a, %d %b %Y %H:%M:%S +0900')
        except TypeError:
            try:
                pubdate = datetime.fromtimestamp(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))
                pubdate = pubdate.strftime('%a, %d %b %Y %H:%M:%S +0900')
            except ValueError:
                pubdate = ''
        except ValueError:
            pubdate = ''
        return pubdate
    
