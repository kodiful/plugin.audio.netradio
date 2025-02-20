# -*- coding: utf-8 -*-

import os
import html

from resources.lib.settings.common import Common


class Content(Common):
    
    def __init__(self):
        super().__init__()

    def prep(self, title):
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'content.xml')) as f:
            self.template = f.read()
        prompt = self.STR(30517) % title
        self.template = self.template.format(prompt=html.escape(prompt))

    def get(self, cid):
        self.SET('cid', str(cid))

    def set(self):
        cid = self.GET('cid')
        sql = 'SELECT * FROM contents WHERE cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid)})
        cdata = self.db.cursor.fetchone()
        filename = self.db.filename(cdata)
        sql = 'UPDATE contents SET cstatus = 1, filename = :filename, kid = -1 WHERE cstatus = 0 AND cid = :cid'
        self.db.cursor.execute(sql, {'cid': int(cid), 'filename': filename})
