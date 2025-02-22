# -*- coding: utf-8 -*-

import urllib.request
import os
import re
import unicodedata
import json
import gzip
import io

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
        # 番組表情報を取得
        try:
            if self.URL:
                # HTTPリクエスト
                req = urllib.request.Request(self.URL)
                res = urllib.request.urlopen(req)
                # レスポンスがgzip圧縮されているときは展開する
                if res.info().get('Content-Encoding') == 'gzip':
                    with gzip.GzipFile(fileobj=io.BytesIO(res.read())) as gz:
                        data = gz.read()
                else:
                    data = res.read()
            else:
                data = b''
        except urllib.error.HTTPError as e:
            self.log(f'request error (code={e.code}):', self.URL)
            return -1 if e.code == 404 else 0
        except Exception as e:
            self.log(f'request error:', self.URL)
            self.log(e)
            return 0
        # ソースをファイルに保存
        with open(self.SOURCE_FILE, 'wb') as f:
            f.write(data)
        # パースして番組表情報を抽出
        try:
            buf = self.parse(data.decode('utf-8'))
        except Exception as e:
            self.log(f'parse error:', self.URL)
            self.log(e)
            return 0
        # 抽出した番組情報をDBに挿入
        for item in buf:
            if self.db.add(item) > 0:
                count += 1  # DBに挿入された番組情報があればカウントアップする
        # パース結果をjsonファイルに保存
        with open(self.JSON_FILE, 'wb') as f:
            f.write(json.dumps(buf, ensure_ascii=False, indent=4).encode('utf-8'))
        # DBへ挿入した番組情報の数を返す
        return count

    def get_nextaired(self):
        sql = 'SELECT nextaired FROM stations WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': self.sid})
        nextaired, = self.db.cursor.fetchone()
        return nextaired

    def _get_nextaired(self):
        sql = '''
        SELECT MIN(c.end)
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid
        WHERE c.end > NOW() AND c.sid = :sid
        '''
        self.db.cursor.execute(sql, {'sid': self.sid})
        try:
            nextaired, = self.db.cursor.fetchone()
        except TypeError:
            nextaired = ''
        return nextaired

    def set_nextaired(self, hours=0):
        sql = '''
        UPDATE stations
        SET nextaired = :nextaired
        WHERE sid = :sid
        '''
        if hours == 0:
            nextaired = self._get_nextaired()
        else:
            nextaired = self.now(hours)
        self.db.cursor.execute(sql, {'nextaired': nextaired, 'sid': self.sid})
        return nextaired
    
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


class NullScraper(Common):
    
    def __init__(self, sid):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        self.sid = sid
        self.db.cursor.execute('SELECT station, key, region, pref, site FROM stations WHERE sid = :sid', {'sid': sid})
        self.station, self.key, self.region, self.pref, self.site = self.db.cursor.fetchone()

    def update(self):
        nextaired = self.get_nextaired()
        return 1 if nextaired < self.now() else 0
    
    def get_nextaired(self):
        self.db.cursor.execute('SELECT nextaired FROM stations WHERE sid = :sid', {'sid': self.sid})
        nextaired, = self.db.cursor.fetchone()
        return nextaired

    def set_nextaired(self):
        nextaired = self.now(hours=1)
        sql = 'UPDATE stations SET nextaired = :nextaired WHERE sid = :sid'
        self.db.cursor.execute(sql, {'nextaired': nextaired, 'sid': self.sid})
        return nextaired
    