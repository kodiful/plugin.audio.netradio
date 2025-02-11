# -*- coding: utf-8 -*-

import requests
import os
import re
import unicodedata

from resources.lib.common import Common as Main
from resources.lib.db import ThreadLocal


class Common(Main):

    LOGO_PATH = os.path.join(Main.DATA_PATH, 'stations', 'logo')
    SOURCE_PATH = os.path.join(Main.DATA_PATH, 'stations', 'source')
    JSON_PATH = os.path.join(Main.DATA_PATH, 'stations', 'json')

    def __init__(self, protocol=None):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # ディレクトリ設定
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{protocol}.txt')
        self.JSON_FILE = os.path.join(self.JSON_PATH, f'{self.PROTOCOL}.json')
        os.makedirs(os.path.dirname(self.SOURCE_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(self.JSON_FILE), exist_ok=True)
        os.makedirs(self.LOGO_PATH, exist_ok=True)

    # ファイルをパースする
    def parse(self, data):
        # to be overwritten
        return []

    # 一連の処理を実行する
    def run(self):
        if not os.path.isfile(self.SOURCE_FILE):
            data = requests.get(self.URL).content.decode('utf-8')
            with open(self.SOURCE_FILE, 'wb') as f:
                f.write(data.encode('utf-8'))
        with open(self.SOURCE_FILE, 'rb') as f:
            data = f.read().decode('utf-8')
        return sorted(self.parse(data), key=lambda x: x['code'])
  
    # 文字列を正規化する
    @staticmethod
    def normalize(text):
        text = re.sub('～', '〜', text)
        text = re.sub('（', '(', text)
        text = re.sub('）', ')', text)
        text = re.sub('[\r\n\t]', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub('[ ]{2,}', ' ', text)
        return text.strip()
