# -*- coding: utf-8 -*-

import requests
import sys
import os
import re
import json
import unicodedata
import shutil

from PIL import Image
from sqlite3 import dbapi2 as sqlite


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
                status = True
            else:
                print('[%s] file exists (skip):' % self.TYPE, path, sep='\t', file=sys.stderr)
                status = False
            # ロゴ画像をダウンロードする
            self.load_logo(item, self.LOGO_PATH)
            # リスト出力
            print('%s\t[%s]\t%s\t%s\t%s\t%s\t%s\t%s' % (status, item['type'], item['station'], item['official'] or 'n/a', item['region'], item['pref'], item['city'] or 'n/a', item['code']), file=sys.stdout)

    # ロゴ画像をダウンロードする
    @staticmethod
    def load_logo(item, dir, force=False):
        dirname = os.path.join(dir, item['type'])
        os.makedirs(dirname, exist_ok=True)
        path = os.path.join(dirname, '%s.png' % item['station'])
        if force:
            import xbmcaddon
            import xbmcvfs
            # ファイルを削除
            if os.path.exists(path):
                os.remove(path)
            # DBから画像のキャッシュを削除
            DB_PATH = xbmcvfs.translatePath('special://database')
            CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')
            conn = sqlite.connect(CACHE_DB)
            conn.cursor().execute(f"DELETE FROM texture WHERE url = '{path}';")
            conn.commit()
            conn.close()
            # デフォルトアイコンを設定
            ADDON = xbmcaddon.Addon()
            PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
            icon = os.path.join(PLUGIN_PATH, 'icon.png')
        else:
            icon = None
        icon = os.path.join('icon.png')
        if os.path.exists(path):
            return
        else:
            if item['logo']:
                try:
                    res = requests.get(item['logo'])
                    if res.status_code == 200:
                        with open(path, 'wb') as f:
                            f.write(res.content)
                except Exception as e:
                    pass
        if os.path.exists(path) is False and icon:
            shutil.copy(icon, path)
        if os.path.exists(path):
            # アイコン化
            img = Image.open(path)
            w, h = img.size
            a = max(w, h)
            h = h * 200 // a
            w = w * 200 // a
            img = img.resize((w, h), Image.ANTIALIAS)
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
