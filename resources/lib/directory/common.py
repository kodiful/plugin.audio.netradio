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
        self.SOURCE_FILE = os.path.join(self.SOURCE_PATH, f'{type or self.TYPE}.txt')
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
    def parse(self, data):  # to be overwritten
        return []

    # 一連の処理を実行する
    def run(self):
        if not os.path.isfile(self.SOURCE_FILE):
            data = self.load()
            self.write(data)
        data = self.read()
        return self.parse(data)
    
    # リストをJSONとして出力する
    def save_as_list(self, buf):
        with open(self.JSON_FILE, 'w') as f:
            f.write(json.dumps(buf, sort_keys=False, ensure_ascii=False, indent=4))

    # リストの要素をJSONとして出力する
    def save_as_file(self, buf, category):
        for item in buf:
            region = item['region']
            pref = item['pref']
            dirname = os.path.join(self.DIRECTORY_PATH, category, region, pref)
            os.makedirs(dirname, exist_ok=True)
            filename = os.path.join(dirname, '%s.json' % item['name'])
            if os.path.exists(filename) is False:
                with open(filename, 'w') as f:
                    f.write(json.dumps(item, sort_keys=False, ensure_ascii=False, indent=4))
            else:
                print('[%s] ignore existing file:' % self.TYPE, filename, sep='\t')
                continue
            # ロゴ画像をダウンロードする
            dirname = os.path.join('logo', item['type'])
            os.makedirs(dirname, exist_ok=True)
            filename = os.path.join(dirname, '%s.png' % item['name'])
            if os.path.exists(filename) is False:
                res = requests.get(item['logo'])
                if res.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(res.content)
                else:
                    # ロゴ画像のダウンロードに失敗したときはfavicon.icoで代用する
                    protocol, _, hostname, _ = item['logo'].split('/', 3)
                    res = requests.get(f'{protocol}//{hostname}/favicon.ico')
                    if res.status_code == 200:
                        iconame = os.path.join(dirname, '%s.ico' % item['name'])
                        with open(iconame, 'wb') as f:
                            f.write(res.content)
                        img = Image.open(iconame)  # icoファイルを開く
                        img.save(filename)  # pngに変換して保存する
                    else:
                        # favicon.icoのダウンロードに失敗したときは既定の画像で代用する
                        shutil.copy('icon.png', filename)
    
    # 文字列正規化する
    def normalize(self, text):
        text = re.sub('～', '〜', text)
        text = re.sub('（', '(', text)
        text = re.sub('）', ')', text)
        text = re.sub('[\r\n\t]', ' ', text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub('[ ]{2,}', ' ', text)
        return text.strip()
    