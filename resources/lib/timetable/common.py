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

    # ファイルをパースする
    def parse(self, data):
        # to be overwritten
        return []

    # 一連の処理を実行する
    def update(self, force=False):
        # 現在時刻
        now = self.now()
        # 次の番組の開始時刻と比較する
        if force is False and os.path.isfile(self.JSON_FILE):
            buf = self.read_as_json(self.JSON_FILE)
            nextaired = self.next_aired(buf)
            if now < nextaired:
                return nextaired - now
        # ファイル更新
        data = self.load(self.URL)
        self.write(self.SOURCE_FILE, data)
        buf = self.parse(data)
        self.save_as_list(buf)
        self.save_as_file(buf)
        nextaired = self.next_aired(buf)
        return nextaired - now
    
     # リストをJSONとして出力する
    def save_as_list(self, buf):
        self.write_as_json(self.JSON_FILE, buf)

    # リストの要素を個別にJSONとして出力する
    def save_as_file(self, buf):
        for name, progs in buf.items():
            dirname = os.path.join(self.TIMETABLE_PATH, progs[0]['type'])
            os.makedirs(dirname, exist_ok=True)
            path = os.path.join(dirname, '%s.json' % name)
            self.write_as_json(path, progs)

    # 現在時刻
    @staticmethod
    def now():
        return datetime.datetime.now().timestamp()
    
    # 次の番組の開始時刻
    @staticmethod
    def next_aired(buf, stations=None):
        if stations is None:
            stations = buf.keys()
        # 実在する放送局名に絞る
        stations = list(filter(lambda x: buf.get(x), stations))
        # 番組終了時刻を抽出する
        x = reduce(lambda a, b: a + b, [list(map(lambda x: x['end'], buf[name])) for name in stations])
        # 抽出した番組終了時刻のうち最も早い時刻を返す
        return min(x)
    
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
      
    # ファイル入出力
    @staticmethod
    def load(url):
        res = requests.get(url)
        return res.content.decode('utf-8')

    @staticmethod
    def write(path, data):
        with open(path, 'wb') as f:
            f.write(data.encode('utf-8'))

    @staticmethod
    def read(path):
        with open(path, 'rb') as f:
            return f.read().decode('utf-8')

    @staticmethod
    def read_as_json(path):
        return json.loads(Common.read(path))

    @staticmethod
    def write_as_json(path, data):
        Common.write(path, json.dumps(data, ensure_ascii=False, indent=4))
