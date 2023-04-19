# -*- coding: utf-8 -*-

import os
import shutil
import datetime
import glob
import json
import hashlib

from resources.lib.common import Common

import xbmc


class Keyword(Common):
    
    def __init__(self):
        super().__init__()
 
    def set(self, path):
        # 設定画面を開く
        src = os.path.join(self.RESOURCES_PATH, 'keyword.xml')
        dst = os.path.join(self.RESOURCES_PATH, 'settings.xml')
        shutil.copy(src, dst)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % self.ADDON_ID)
        # 設定画面が最前面になるまで時間をおく
        xbmc.sleep(100)
        # 設定画面を書き換える
        if path is None:
            # アドオン設定から
            self.SET('keyword', '')
            self.SET('search', '0')  # 番組名のみ
            self.SET('weekday', '7')  # 毎日
            self.SET('limit', 'false')  # 放送局を限定しない
            self.SET('station', '')
        else:
            # コンテクストメニューから
            data = self.read_as_json(path)
            if type(data) == list:
                # 番組情報から
                data = data[0]
                weekday = datetime.datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
                self.SET('keyword', data['title'])
                self.SET('search', '0')  # 番組名のみ
                self.SET('weekday', str(weekday))
                self.SET('limit', 'true')  # 放送局を限定する
                self.SET('station', data['station'])
            else:
                # キーワード設定変更
                self.SET('keyword', data['keyword'])
                self.SET('search', data['search'])
                self.SET('weekday', data['weekday'])
                self.SET('limit', data['limit']) 
                self.SET('station', data['station'])
        # 共有メモリにフラグを立てる
        self.write_mmap('updated')

    def add(self):
        data = {}
        for key in ('keyword', 'search', 'weekday', 'limit', 'station'):
            data[key] = self.GET(key)
        self.write_as_json(os.path.join(self.KEYWORDS_PATH, '%s.json' % data['keyword']), data)
        #Stations.load_logo(item, self.LOGO_PATH)
        xbmc.executebuiltin('Container.Refresh')

    def match(self):
        # キーワードリスト生成
        keywords = []
        for path in glob.glob(os.path.join(self.KEYWORDS_PATH, '*.json')):
            keywords.append(self.read_as_json(path))
        # 番組リスト生成
        programs = []
        for path in glob.glob(os.path.join(self.TIMETABLE_PATH, '*', '*.json')):
            programs = programs + self.read_as_json(path)
        # 照合
        matched = []
        for p in programs:
            # 番組情報のハッシュファイル名
            hash = '%s_%s_%s.json' % (p['START'], p['type'], hashlib.md5(json.dumps(p).encode('utf-8')).hexdigest())
            # 処理中の番組はスキップ
            path = os.path.join(self.PROCESSING_PATH, hash)
            if os.path.isfile(path):
                continue
            # 待機中の番組はスキップ
            path = os.path.join(self.PENDING_PATH, hash)
            if os.path.isfile(path):
                continue
            title = p['title']
            description = ' '.join([title, p['subtitle'], p['act'], p['info'], p['desc']])
            for k in keywords:
                if k['weekday'] != '7' and k['weekday'] != p['weekday']:
                    continue
                if k['limit'] == 'true' and k['station'] != p['station']:
                    continue
                if k['search'] == '0' and title.find(k['keyword']) < 0:
                    continue
                if k['search'] == '1' and description.find(k['keyword']) < 0:
                    continue
                p['keyword'] = k['keyword']
                self.write_as_json(path, p)
                matched.append((p, path))
                break
        return matched

