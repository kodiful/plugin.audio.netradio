# -*- coding: utf-8 -*-

import os
import html

from resources.lib.rss.common import Common, decorator


class Keywords(Common):

    def __init__(self, keyword, dirname):
        super().__init__()
        # RSS生成メソッドにデコレータを適用
        self.create_rss = decorator(self, keyword, dirname, 'rss.xml')(self.create_rss)        
        self.create_index = decorator(self, 'NetRadio Client', '.', 'keywords.xml')(self.create_index)        

    def create_rss(self, kid):
        sql = '''SELECT filename, title, start, station, description, site, duration
        FROM contents
        WHERE kid = :kid AND cstatus = -1
        ORDER BY start DESC'''
        self.db.cursor.execute(sql, {'kid': kid})
        for filename, title, start, station, description, site, duration in self.db.cursor.fetchall():
            self.writer.write(
                self.body.format(
                    title=html.escape(title),
                    date=self._date(start),
                    url=site,
                    filename=filename,
                    description=description,
                    pubdate=self._pubdate(start),
                    station=station,
                    duration='%02d:%02d:%02d' % (duration // 3600, duration // 60 % 60, duration % 60),
                    filesize=os.path.getsize(os.path.join(self.path, filename))
                )
            )

    def create_index(self):
        sql = '''SELECT keyword, dirname
        FROM keywords
        WHERE kid > 0
        ORDER BY keyword COLLATE NOCASE'''
        self.db.cursor.execute(sql, {})
        for keyword, dirname in self.db.cursor.fetchall():
            self.writer.write(
                self.body.format(
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
