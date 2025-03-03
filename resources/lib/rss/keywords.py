# -*- coding: utf-8 -*-

import os
import html

from .common import Common, decorator


class Keywords(Common):

    def __init__(self, keyword='', dirname=''):
        super().__init__()
        # RSS生成メソッドにデコレータを適用
        self.keyword = keyword
        self.dirname = dirname
        self.create_rss = decorator(self, keyword, dirname, 'rss.xml')(self.create_rss)        
        self.create_index = decorator(self, 'NetRadio Client', '.', 'keywords.xml')(self.create_index)        

    def create_rss(self):
        sql = '''SELECT c.filename, c.title, c.start, c.description, c.site, c.duration, s.protocol, s.station
        FROM contents AS c
        JOIN stations AS s ON c.sid = s.sid
        JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cstatus = -1 AND c.kid > 0 AND k.keyword = :keyword AND k.dirname = :dirname
        ORDER BY c.start DESC'''
        self.db.cursor.execute(sql, {'keyword': self.keyword, 'dirname': self.dirname})
        for filename, title, start, description, site, duration, protocol, station in self.db.cursor.fetchall():
            mp3_file = os.path.join(self.CONTENTS_PATH, self.dirname, protocol, station, filename)
            if os.path.exists(mp3_file):
                self.writer.write(
                    self.body.format(
                        title=html.escape(title),
                        date=self._date(start),
                        url=site,
                        filename=f'{protocol}/{station}/{filename}',
                        description=description.replace('<br>','<br/>'),  # add replace for compatibility
                        pubdate=self._pubdate(start),
                        station=station,
                        duration='%02d:%02d:%02d' % (duration // 3600, duration // 60 % 60, duration % 60),
                        filesize=os.path.getsize(mp3_file)
                    )
                )
            else:
                self.log('mp3 file not found:', mp3_file)

    def create_index(self):
        sql = '''SELECT DISTINCT  k.keyword, k.dirname
        FROM contents AS c JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cstatus = -1 AND c.kid > 0
        ORDER BY k.keyword COLLATE NOCASE'''
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
