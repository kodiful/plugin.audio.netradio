# -*- coding: utf-8 -*-

import os
import shutil
import datetime
import glob
import json
import binascii

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
            self.SET('id', '')
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
                self.SET('id', data['id'])
            else:
                # キーワード設定変更
                self.SET('keyword', data['keyword'])
                self.SET('search', data['search'])
                self.SET('weekday', data['weekday'])
                self.SET('limit', data['limit']) 
                self.SET('id', data['id'])
        # 共有メモリにフラグを立てる
        self.write_mmap('True')

    def add(self):
        data = {}
        for key in ('keyword', 'search', 'weekday', 'limit', 'id'):
            data[key] = self.GET(key)
        self.write_as_json(os.path.join(self.KEYWORDS_PATH, '%s.json' % data['keyword']), data)
        #Stations.load_logo(item, self.LOGO_PATH)
        xbmc.executebuiltin('Container.Refresh')

    def match(self):
        # 番組保存しない場合は何もしない
        if self.GET('download') == 'false':
            return []
        # キーワードリスト生成
        keywords = []
        for path in sorted(glob.glob(os.path.join(self.KEYWORDS_PATH, '*.json'))):  # 文字コード順に照合、複数当たった場合は後勝ち
            keywords.append(self.read_as_json(path))
        # 番組リスト生成
        programs = []
        for path in glob.glob(os.path.join(self.TIMETABLE_PATH, '*', '*.json')):
            programs = programs + self.read_as_json(path)
        # 照合
        matched = []
        for p in programs:
            # 放送局情報
            s = self._station(p)
            if s is None: continue
            # 番組urlがないときは公式urlで代替
            p['url'] = p['url'] or s['official']
            # 番組情報のハッシュファイル名
            data = json.dumps(p).encode('utf-8')
            crc = format(binascii.crc32(data), 'x')
            hash = '%s_%s_%s_%s_%s.json' % (p['START'][0:8], p['START'][8:12], p['END'][8:12], p['id'], crc)
            # radiko.jpのNHKはスキップ
            if p['type'] == 'radk' and p['station'].startswith('NHK'):
                continue
            # 処理中の番組はスキップ
            path = os.path.join(self.PROCESSING_PATH, hash)
            if os.path.isfile(path):
                continue
            # 待機中の番組はスキップ
            path = os.path.join(self.PENDING_PATH, hash)
            if os.path.isfile(path):
                continue
            title = p['title']
            description = ' '.join([title, p['info'], p['act'], p['desc']])
            for k in keywords:
                if k['weekday'] != '7' and k['weekday'] != p['weekday']:
                    continue
                if k['limit'] == 'true' and k['id'] != p['id']:
                    continue
                if k['search'] == '0' and title.find(k['keyword']) < 0:
                    continue
                if k['search'] == '1' and description.find(k['keyword']) < 0:
                    continue
                # キーワード情報を追加
                p['keyword'] = k['keyword']
                self.write_as_json(path, p)
                matched.append((p, path))
                break
        return matched
    
    def _station(self, program):
        index = self.read_as_json(os.path.join(self.INDEX_PATH, '%s.json' % program['type']))
        #station = list(filter(lambda x: x['id'] == program['id'] and x['station'] == program['station'], index))[0]
        #station = list(filter(lambda x: x['id'] == program['id'] and (x['id'][:3] != 'NHK' or x['station'] == program['station']), index))[0]
        #return station
        station = list(filter(lambda x: x['id'] == program['id'] and (x['id'][:3] != 'NHK' or x['station'] == program['station']), index))
        if len(station) > 0:
            return station[0]
        else:
            return None

