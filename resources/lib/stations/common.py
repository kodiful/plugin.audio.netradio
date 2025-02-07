# -*- coding: utf-8 -*-

import requests
import os
import re
import unicodedata
import shutil

from PIL import Image
from sqlite3 import dbapi2 as sqlite

import xbmcaddon
import xbmcvfs

from resources.lib.common import Common


class Common(Common):

    LOGO_PATH = os.path.join(Common.DATA_PATH, 'stations', 'logo')
    SOURCE_PATH = os.path.join(Common.DATA_PATH, 'stations', 'source')
    JSON_PATH = os.path.join(Common.DATA_PATH, 'stations', 'json')

    def __init__(self, type=None):
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
            data = requests.get(self.URL).content.decode('utf-8')
            with open(self.SOURCE_FILE, 'wb') as f:
                f.write(data.encode('utf-8'))
        with open(self.SOURCE_FILE, 'rb') as f:
            data = f.read().decode('utf-8')
        return self.parse(data)

    # ロゴ画像をダウンロードする
    @staticmethod
    def load_logo(item, dir, force=False):
        dirname = os.path.join(dir, item['type'])
        os.makedirs(dirname, exist_ok=True)
        path = os.path.join(dirname, '%s.png' % item['station'])
        if force:
            # ファイルを削除
            if os.path.exists(path):
                os.remove(path)
            # DBから画像のキャッシュを削除
            DB_PATH = xbmcvfs.translatePath('special://database')
            CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')
            conn = sqlite.connect(CACHE_DB)
            sql = 'DELETE FROM texture WHERE url = :url'
            conn.cursor().execute(sql, {'url': path})
            conn.commit()
            conn.close()
        # 画像がある場合はなにもしない
        if os.path.exists(path):
            return
        # ロゴ画像を取得
        if item['logo']:
            try:
                res = requests.get(item['logo'])
                if res.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(res.content)
            except Exception as e:
                pass
        # 画像が取得できないときはデフォルト画像で代替する
        if os.path.exists(path) is False:
            ADDON = xbmcaddon.Addon()
            PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
            icon = os.path.join(PLUGIN_PATH, 'icon.png')
            shutil.copy(icon, path)
        # アイコン画像に加工する
        if os.path.exists(path):
            img = Image.open(path)
            w, h = img.size
            a = max(w, h)
            h = h * 200 // a
            w = w * 200 // a
            img = img.resize((w, h), Image.LANCZOS)
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
