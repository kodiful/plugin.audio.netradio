# -*- coding: utf-8 -*-

import os
import html

from resources.lib.settings.common import Common


class Download(Common):
    
    def __init__(self):
        super().__init__()

    def prep(self, title):
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'download.xml')) as f:
            self.template = f.read()
        prompt = self.STR(30491) % title
        self.template = self.template.format(prompt=html.escape(prompt))

    def get(self, cid):
        self.SET('cid', str(cid))

    def set(self):
        cid = self.GET('cid')
        sql = 'SELECT station, start, end FROM contents WHERE cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid)})
        station, start, end = self.db.cursor.fetchone()
        filename = self.db.filename(station, start, end)
        sql = 'UPDATE contents SET cstatus = 1, filename = :filename, kid = -1 WHERE cstatus = 0 AND cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid), 'filename': filename})
