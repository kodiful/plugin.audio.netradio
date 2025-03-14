# -*- coding: utf-8 -*-

import os
import html

from .common import Common
from resources.lib.rss import Stations


class Download(Common):

    def __init__(self):
        super().__init__()

    def prep(self, title):
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'download.xml')) as f:
            self.template = f.read()
        prompt = self.STR(30493) % title
        self.template = self.template.format(prompt=html.escape(prompt))

    def get(self, cid):
        self.SET('cid', str(cid))

    def set(self):
        cid = self.GET('cid')
        sql = 'SELECT s.protocol, c.station, c.start, c.end FROM contents AS c JOIN stations AS s ON c.sid = s.sid WHERE c.cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid)})
        protocol, station, start, end = self.db.cursor.fetchone()
        filename = self.db.filename(station, start, end)
        sql = 'UPDATE contents SET cstatus = 1, filename = :filename, kid = -1 WHERE cstatus = 0 AND cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid), 'filename': filename})
        # RSSインデクス再作成
        Stations().create_index()
        # 再描画
        self.refresh()
