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
        return

    def set(self, path):
        # 設定画面を開く
        src = os.path.join(Common.RESOURCES_PATH, 'keyword.xml')
        dst = os.path.join(Common.RESOURCES_PATH, 'settings.xml')
        shutil.copy(src, dst)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        # 設定画面が最前面になるまで時間をおく
        xbmc.sleep(100)
        # 設定画面を書き換える
        data = Common.read_as_json(path)
        if type(data) == list:
            data = data[0]
        self.log(data)
        if data.get('name'):
            weekday = datetime.datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            Common.SET('keyword', data['title'])
            Common.SET('search', '0')  # 番組名のみ
            Common.SET('weekday', str(weekday))
            Common.SET('limit', 'true')  # 放送局を限定する
            Common.SET('station', data['name'])
        if data.get('keyword'):
            Common.SET('keyword', data['keyword'])
            Common.SET('search', data['search'])
            Common.SET('weekday', data['weekday'])
            Common.SET('limit', data['limit']) 
            Common.SET('station', data['station'])

    def add(self):
        data = {}
        for key in ('keyword', 'search', 'weekday', 'limit', 'station'):
            data[key] = Common.GET(key)
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
            # 番組情報のハッシュ
            md5 = hashlib.md5(json.dumps(p).encode('utf-8')).hexdigest()
            # 処理中の番組はスキップ
            path = os.path.join(self.PROCESSING_PATH, md5)
            if os.path.isfile(path):
                continue
            # 待機中の番組はスキップ
            path = os.path.join(self.PENDING_PATH, md5)
            if os.path.isfile(path):
                continue
            title = p['title']
            description = ' '.join([title, p['subtitle'], p['act'], p['info'], p['desc']])
            for k in keywords:
                if k['weekday'] != '7' and k['weekday'] != p['weekday']:
                    continue
                if k['limit'] == 'true' and k['station'] != p['name']:
                    continue
                if k['search'] == '0' and title.find(k['keyword']) < 0:
                    continue
                if k['search'] == '1' and description.find(k['keyword']) < 0:
                    continue
                p['matched'] = k['keyword']
                self.write_as_json(path, p)
                matched.append((p, path))
                break
        return matched

