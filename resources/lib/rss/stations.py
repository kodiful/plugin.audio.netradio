# -*- coding: utf-8 -*-

import os
import html

from .common import Common, decorator


class Stations(Common):

    def __init__(self, protocol='', station=''):
        super().__init__()
        # RSS生成メソッドにデコレータを適用
        self.protocol = protocol
        self.station = station
        self.create_rss = decorator(self, station, os.path.join('0', protocol, station), 'rss.xml')(self.create_rss)
        self.create_index = decorator(self, 'NetRadio Client', '.', 'stations.xml')(self.create_index)

    def create_rss(self):
        sql = '''SELECT k.dirname, c.filename, c.title, c.start, c.description, c.site, c.duration
        FROM contents AS c
        JOIN stations AS s ON c.sid = s.sid
        JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cstatus = -1 AND s.protocol = :protocol AND s.station = :station
        ORDER BY substr(c.start, 1, 10) DESC, substr(c.start, 12) ASC'''  # 2025-03-31 20:15:00
        self.db.cursor.execute(sql, {'protocol': self.protocol, 'station': self.station})
        for dirname, filename, title, start, description, site, duration in self.db.cursor.fetchall():
            mp3_file = os.path.join(self.CONTENTS_PATH, dirname, self.protocol, self.station, filename)
            if os.path.exists(mp3_file):
                self.writer.write(
                    self.body.format(
                        title=html.escape(title),
                        date=self._date(start),
                        url=site,
                        filename=f'../../../{dirname}/{self.protocol}/{self.station}/{filename}',
                        description=description.replace('<br>','<br/>'),  # add replace for compatibility
                        pubdate=self._pubdate(start),
                        station=self.station,
                        duration='%02d:%02d:%02d' % (duration // 3600, duration // 60 % 60, duration % 60),
                        filesize=os.path.getsize(mp3_file)
                    )
                )
            else:
                self.log('mp3 file not found:', mp3_file)

    def create_index(self):
        sql = '''SELECT DISTINCT s.protocol, c.station
        FROM contents AS c
        JOIN stations AS s ON c.sid = s.sid
        JOIN keywords AS k ON c.kid = k.kid
        WHERE c.cstatus = -1
        ORDER BY
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
            self.writer.write(
                self.body.format(
                    title=html.escape(station),
                    date='',
                    url=f'0/{protocol}/{station}/rss.xml',
                    filename='',
                    description='',
                    pubdate='',
                    station='',
                    duration='',
                    filesize=''
                )
            )
