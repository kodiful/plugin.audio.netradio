# -*- coding: utf-8 -*-

import os
import json

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Updater_20251005(Common):

    def __init__(self):
        self.db = ThreadLocal.db

    def run(self):
        sql = 'SELECT * FROM stations WHERE direct = :direct'
        self.db.cursor.execute(sql, {'direct': 'https://radio-stream.nhk.jp/hls/live/2023229/nhkradiruakr1/master.m3u8'})
        results = self.db.cursor.fetchone()
        if results is not None:
            # プラグインの放送局フォルダ直下のjsonフォルダにあるjsonファイルから読み込む
            with open(os.path.join(self.DATA_PATH, 'stations', 'json', 'NHK.json'), encoding='utf-8') as f:
                # jsonファイルを読み込む
                for data in json.loads(f.read()):
                    # protocol, key, code, regionが同じレコードのdirectを更新してversionを9.1にする
                    sql = 'UPDATE stations SET direct = :direct, version = :version WHERE protocol = :protocol AND key = :key AND code = :code'
                    self.db.cursor.execute(sql, {
                        'direct': data['direct'],
                        'protocol': data['protocol'],
                        'key': data['key'],
                        'code': data['code'],
                        'version': '9.1',
                    })
            # ログ
            self.log('Updater_20251005 applied')
