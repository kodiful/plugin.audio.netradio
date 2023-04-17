# -*- coding: utf-8 -*-

import requests
import os
import re
import json
import unicodedata
import shutil
from PIL import Image


class Common:

    def __init__(self, type=None):
        os.makedirs(self.DIRECTORY_PATH, exist_ok=True)
        os.makedirs(self.SOURCE_PATH, exist_ok=True)
        os.makedirs(self.JSON_PATH, exist_ok=True)
        os.makedirs(self.LOGO_PATH, exist_ok=True)
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{type or self.TYPE}.txt')
        self.JSON_FILE = os.path.join(self.JSON_PATH, f'{self.TYPE}.json')

    # ファイルをパースする
    def parse(self, data):  # to be overwritten
        return []

    # 一連の処理を実行する
    def run(self):
        if not os.path.isfile(self.SOURCE_FILE):
            data = self.load(self.URL)
            self.write(self.SOURCE_FILE, data)
        data = self.read(self.SOURCE_FILE)
        return self.parse(data)
    
    # リストをJSONとして出力する
    def save_as_list(self, buf):
        self.write_as_json(self.JSON_FILE, buf)

    # リストの要素を個別にJSONとして出力する
    def save_as_file(self, buf, category):
        for item in buf:
            region = item['region']
            pref = item['pref']
            dir = os.path.join(self.DIRECTORY_PATH, category, region, pref)
            os.makedirs(dir, exist_ok=True)
            path = os.path.join(dir, '%s.json' % item['station'])
            if os.path.exists(path) is False:
                self.write_as_json(path, item)
            else:
                print('[%s] ignore existing file:' % self.TYPE, path, sep='\t')
            # ロゴ画像をダウンロードする
            self.load_logo(item, self.LOGO_PATH)

    # ロゴ画像をダウンロードする
    @staticmethod
    def load_logo(item, dir):
        dirname = os.path.join(dir, item['type'])
        os.makedirs(dirname, exist_ok=True)
        path = os.path.join(dirname, '%s.png' % item['station'])
        if os.path.exists(path) is False:
            if item['logo']:
                res = requests.get(item['logo'])
                if res.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(res.content)
            if os.path.exists(path) is False:
                # ロゴ画像のダウンロードに失敗したときはfavicon.icoで代用する
                protocol, _, hostname, _ = item['logo'].split('/', 3)
                res = requests.get(f'{protocol}//{hostname}/favicon.ico')
                if res.status_code == 200:
                    iconame = os.path.join(dirname, '%s.ico' % item['station'])
                    with open(iconame, 'wb') as f:
                        f.write(res.content)
                    img = Image.open(iconame)  # icoファイルを開く
                    img.save(path)  # pngに変換して保存する
                else:
                    # favicon.icoのダウンロードに失敗したときは既定の画像で代用する
                    shutil.copy('icon.png', path)
            # アイコン化
            img = Image.open(path)
            w, h = img.size
            if w > 216:
                h = 216 * h // w
                w = 216
                img = img.resize((216, h), Image.ANTIALIAS)
            background = Image.new('RGB', (216, 216), (255, 255, 255))
            try:
                background.paste(img, ((216 - w) // 2, (216 - h) // 2), img)
            except Exception:
                background.paste(img, ((216 - w) // 2, (216 - h) // 2))
            background.save(path)
    
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
