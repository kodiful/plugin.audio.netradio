# -*- coding: utf-8 -*-

import requests
import os
import re
import unicodedata
import json
import time
import datetime
from functools import reduce


class Common:

    def __init__(self):
        os.makedirs(self.TIMETABLE_PATH, exist_ok=True)
        os.makedirs(self.SOURCE_PATH, exist_ok=True)
        os.makedirs(self.JSON_PATH, exist_ok=True)
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{self.TYPE}.txt')
        self.JSON_FILE = os.path.join(self.JSON_PATH, f'{self.TYPE}.json')

    # ページを読み込む
    def load(self):
        res = requests.get(self.URL)
        return res.text

    # ファイルを書き込む
    def write(self, data):
        with open(self.SOURCE_FILE, 'w') as f:
            f.write(data)

    # ファイルを読み込む
    def read(self):
        with open(self.SOURCE_FILE, 'r') as f:
            data = f.read()
        return data

    # ファイルをパースする
    def parse(self, data):
        # to be overwritten
        return []

    def update(self, force=False):
        # 現在時刻
        now = self.now()
        # 次の番組の開始時刻と比較する
        if force is False and os.path.isfile(self.JSON_FILE):
            with open(self.JSON_FILE) as f:
                buf = json.loads(f.read())
            nextaired = self.next_aired(buf)
            timestamp = self.timestamp(self.JSON_FILE)
            if now < nextaired:
                return nextaired - now
        # ファイル更新
        data = self.load()
        self.write(data)
        buf = self.parse(data)
        self.save_as_list(buf)
        self.save_as_file(buf)
        nextaired = self.next_aired(buf)
        return nextaired - now

     # リストをJSONとして出力する
    def save_as_list(self, buf):
        with open(self.JSON_FILE, 'w') as f:
            f.write(json.dumps(buf, sort_keys=False, ensure_ascii=False, indent=4))

    # リストの要素をJSONとして出力する
    def save_as_file(self, buf):
        for name, progs in buf.items():
            dirname = os.path.join(self.TIMETABLE_PATH, progs[0]['type'])
            os.makedirs(dirname, exist_ok=True)
            filename = os.path.join(dirname, '%s.json' % name)
            with open(filename, 'w') as f:
                f.write(json.dumps(progs, sort_keys=False, ensure_ascii=False, indent=4))
    
    # 文字列正規化する
    def normalize(self, text):
        if text is None: return ''
        text = re.sub('～', '〜', text)
        text = re.sub('（', '(', text)
        text = re.sub('）', ')', text)
        text = re.sub('[\r\n\t]', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub('[ ]{2,}', ' ', text)
        return text.strip()
    
    # ファイルのタイムスタンプ
    def timestamp(self, path):
        # ファイルの最終更新時刻を取得
        mtime = os.path.getmtime(path)
        # 最終更新時刻をUNIX時間に変換
        unix_time = int(time.mktime(time.gmtime(mtime)))
        return unix_time
    
    # 現在時刻
    def now(self):
        return datetime.datetime.now().timestamp()
    
    # 次の番組の開始時刻
    def next_aired(self, buf, stations=None):
        if stations is None:
            stations = buf.keys()
        # 実在する放送局名に絞る
        stations = list(filter(lambda x: buf.get(x), stations))
        # 番組終了時間を抽出する
        x = reduce(lambda a, b: a + b, [list(map(lambda x: x['end'], buf[name])) for name in stations])
        return min(x)
    


