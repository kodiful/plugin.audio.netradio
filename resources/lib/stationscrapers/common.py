# -*- coding: utf-8 -*-

import urllib
import os
import re
import gzip
import io
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
        # 放送局リストがなければ取得
        if not os.path.isfile(self.SOURCE_FILE):
            try:
                # HTTPリクエスト
                req = urllib.request.Request(self.URL)
                res = urllib.request.urlopen(req)
                # レスポンスがgzip圧縮されているときは展開する
                if res.info().get('Content-Encoding') == 'gzip':
                    with gzip.GzipFile(fileobj=io.BytesIO(res.read())) as gz:
                        data = gz.read()
                else:
                    data = res.read()
            except urllib.error.HTTPError as e:
                self.log(f'request error (code={e.code}):', self.URL)
            except Exception as e:
                self.log(f'request error:', self.URL)
            # ソースをファイルに保存
            with open(self.SOURCE_FILE, 'wb') as f:
                f.write(data)
        with open(self.SOURCE_FILE, 'rb') as f:
            data = f.read()
        buf = self.parse(data.decode('utf-8'))
        return sorted(buf, key=lambda x: x['code'])
  
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
