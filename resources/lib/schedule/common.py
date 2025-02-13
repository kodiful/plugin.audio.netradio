# -*- coding: utf-8 -*-

import requests
import os
import re
import unicodedata
import json

from resources.lib.common import Common as Main
from resources.lib.db import ThreadLocal


class Common(Main):

    SOURCE_PATH = os.path.join(Main.PROFILE_PATH, 'schedule', 'source')
    JSON_PATH = os.path.join(Main.PROFILE_PATH, 'schedule', 'json')
    
    def __init__(self, protocol):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # ディレクトリ設定
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{protocol}.txt')
        self.JSON_FILE = os.path.join(self.JSON_PATH, f'{protocol}.json')
        os.makedirs(os.path.dirname(self.SOURCE_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(self.JSON_FILE), exist_ok=True)

    # ファイルをパースする
    def parse(self, data):
        # to be overwritten
        return []

    # 一連の処理を実行する
    def update(self):
        # DBへ挿入する番組情報の数を初期化
        count = 0
        # 処理中のファイル
        filename = self._filename()
        # 番組表情報を取得
        res = requests.get(self.URL)
        if res.status_code == 200:
            data = res.content.decode('utf-8')
            # ソースをファイルに保存
            with open(self.SOURCE_FILE, 'wb') as f:
                f.write(data.encode('utf-8'))
            # 番組表情報をパース
            try:
                buf = self.parse(data)
            except Exception as e:
                self.log(f'parse failed ({filename}):', e)
                return 0
            # 番組情報をDBに挿入
            for item in buf:
                if self.db.add(item) > 0:
                    count += 1  # DBに挿入された番組情報があればカウントアップする
            # パース結果をjsonファイルに保存
            with open(self.JSON_FILE, 'wb') as f:
                f.write(json.dumps(buf, ensure_ascii=False, indent=4).encode('utf-8'))
        else:
            self.log(f'file retrieval failed ({filename}):', res.status_code)
            if  res.status_code == 404 and self.PROTOCOL not in ('NHK', 'RDK'):
                # NHK, radiko以外はstationsテーブルのschedule, downloadを0に変更
                sql = 'UPDATE stations SET schedule = 0, download = 0 WHERE sid = :sid'
                self.db.cursor.execute(sql, {'sid': self.sid})
                self.log('schedule & download disabled:', f'{self.PROTOCOL}/{self.sid} ({self.station})')
        # DBへ挿入した番組情報の数を返す
        return count
    
    def _filename(self):
        message = self.PROTOCOL
        if self.PROTOCOL not in ('NHK', 'RDK'):
            message += f'/{self.sid}|{self.station}'
        return message

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
    