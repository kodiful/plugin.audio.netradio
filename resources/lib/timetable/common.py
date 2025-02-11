# -*- coding: utf-8 -*-

import requests
import os
import re
import unicodedata
import json

from resources.lib.common import Common as Main
from resources.lib.db import ThreadLocal


class Common(Main):

    SOURCE_PATH = os.path.join(Main.PROFILE_PATH, 'timetable', 'source')
    JSON_PATH = os.path.join(Main.PROFILE_PATH, 'timetable', 'json')
    
    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # ディレクトリ設定
        os.makedirs(self.SOURCE_PATH, exist_ok=True)
        os.makedirs(self.JSON_PATH, exist_ok=True)
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{self.PROTOCOL}.txt')
        self.JSON_FILE = os.path.join(self.JSON_PATH, f'{self.PROTOCOL}.json')

    # ファイルをパースする
    def parse(self, data):
        # to be overwritten
        return []

    # 一連の処理を実行する
    def update(self):
        # 番組表情報を取得
        res = requests.get(self.URL)
        data = res.content.decode('utf-8')
        # ファイルに保存
        with open(self.SOURCE_FILE, 'wb') as f:
            f.write(data.encode('utf-8'))
        # 番組表情報をパース
        buf = self.parse(data)
        for item in buf:
            self.db.add(item)
        # パース結果をjsonファイルに保存
        with open(self.JSON_FILE, 'wb') as f:
            f.write(json.dumps(buf, ensure_ascii=False, indent=4).encode('utf-8'))

    # 次の更新予定時間
    def next_aired(self):
        sql = 'SELECT MIN(EPOCH(c.end)) FROM contents c JOIN stations s ON c.sid = s.sid WHERE c.cstatus >= 0 AND s.protocol = :protocol'
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL})
        end, = self.db.cursor.fetchone()
        return end
    
    # 文字列を正規化する
    @staticmethod
    def normalize(text):
        if text is None: return ''
        text = re.sub('～', '〜', text)
        text = re.sub('（', '(', text)
        text = re.sub('）', ')', text)
        text = re.sub('[\r\n\t]', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub('[ ]{2,}', ' ', text)
        return text.strip()
    