# -*- coding: utf-8 -*-

import os
import shutil
import glob
import json
from mutagen.mp3 import MP3

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.download import Download


class Transfer(Common):

    # type -> protocol変換
    PROTOCOL = {
        'nhkr': 'NHK',
        'radk': 'RDK',
        'jcba': 'SJ',
        'lsnr': 'LR',
        'csra': 'SR',
        'fmpp': 'SP',
        'user': 'USER'
    }

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db

    def import_contents(self):
        # CONTENTS_PATHが無い場合はなにもしない
        if os.path.exists(Common.CONTENTS_PATH) is False:
            return
        # データ変換関数
        def _datetime(date):
            return f'{date[0:4]}-{date[4:6]}-{date[6:8]} {date[8:10]}:{date[10:12]}:{date[12:14]}'
        def convert(data):
            return {
                'title': data['title'],
                'start': _datetime(data['START']),
                'end': _datetime(data['END']),
                'station': data['station'],
                'act': data['act'],
                'info': data['info'],
                'desc': data['desc'],
                'site': data['url'] or '',
            }
        # ダウンロードフォルダをスキャン
        for origdir in glob.glob(os.path.join(self.CONTENTS_PATH, '*')):
            if os.path.isdir(origdir) is False:
                continue
            # キーワード
            keyword = os.path.basename(origdir)
            # キーワードのkid, dirnameを取得
            sql = 'SELECT kid, dirname FROM keywords WHERE keyword = :keyword'
            self.db.cursor.execute(sql, {'keyword': keyword})
            try:
                kid, dirname = self.db.cursor.fetchone()
            except Exception:
                kid, dirname = 0, '0'
            # キーワードのmp3ファイルを検索
            for mp3file in glob.glob(os.path.join(origdir, '*.mp3')):
                # 対応するjsonファイル
                jsonfile = '%s.json' % os.path.splitext(mp3file)[0]
                if os.path.exists(jsonfile):
                    # jsonファイルを読み込む
                    with open(jsonfile, encoding='utf-8') as f:
                        data = json.loads(f.read())
                    # keyを抽出
                    basename = os.path.basename(mp3file)
                    key = basename.split('_')[-2]
                    # durationを抽出
                    duration = int(MP3(mp3file).info.length)
                    # DBに挿入
                    lastrowid = self.db.add(convert(data), kid, key, duration)
                    # DBの情報をmp3ファイルにID3タグとして書き込む
                    self.db.write_id3(mp3file, lastrowid)
                    # mp3ファイル名の移動先のファイル名を取得
                    sql = 'SELECT filename FROM contents WHERE cid = :cid'
                    self.db.cursor.execute(sql, {'cid': lastrowid})
                    filename, = self.db.cursor.fetchone()
                    # mp3ファイルをリネームして移動
                    destdir = os.path.join(Common.CONTENTS_PATH, dirname)
                    os.makedirs(destdir, exist_ok=True)
                    shutil.move(shutil.move(mp3file, filename), destdir)
            # 不要なファイルを退避
            destdir = os.path.join(Common.CONTENTS_PATH, '~backup')
            os.makedirs(destdir, exist_ok=True)
            shutil.move(origdir, destdir)
        # rss & インデクスを生成
        Download().update_rss()
        # ログ
        self.log('Downloaded files have been imported')

    def import_stations(self):
        # データ変換関数
        def convert(data):
            return {
                'station': data['station'],
                'protocol': self.PROTOCOL[data['type']],
                'key': data['id'],
                'code': data['code'],
                'region': data['region'],
                'pref': data['pref'],
                'city': data['city'],
                'logo': data['logo'],
                'description': data['description'],
                'site': data['official'],
                'direct': data['stream'],
                'delay': 0,
                'display': 1,
                'schedule': 0,
                'download': 0,
            }
        # プラグインの放送局フォルダ直下のjsonフォルダにあるjsonファイルから読み込む
        for json_file in [os.path.join(self.DATA_PATH, 'stations', 'json', f'{protocol}.json') for protocol in ('NHK', 'RDK', 'SJ', 'LR', 'SP', 'SR')]:
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                for data in json.loads(f.read()):
                    # DBに挿入
                    self.db.add_station(data)
        # ユーザデータの放送局フォルダ直下のdirectoryフォルダにあるjsonファイルから読み込む
        for json_file in glob.glob(os.path.join(self.PROFILE_PATH, 'stations', 'directory', '*.json')):
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                data = json.loads(f.read())
            # ユーザ設定の放送局はDBに挿入
            if data['type'] == 'user':
                self.db.add_station(convert(data), top=1)
        # ログ
        self.log('Station settings have been imported')

    def import_keywords(self):
        # データ変換関数
        def convert(data):
            if data['limit'] == 'true':
                sql = 'SELECT station FROM stations WHERE key = :key AND download > -1'
                self.db.cursor.execute(sql, {'key': data['id']})
                station, = self.db.cursor.fetchone()
            else:
                station = ''
            return {
                'keyword': data['keyword'],
                'match': int(data['search']),
                'weekday': int(data['weekday']),
                'station': station,
                'kstatus': 1
            }
        # キーワードフォルダをスキャン
        for image_file in glob.glob(os.path.join(self.PROFILE_PATH, 'keywords', '*.png')):
            # 古いファイルを削除
            os.remove(image_file)
        for json_file in glob.glob(os.path.join(self.PROFILE_PATH, 'keywords', '*.json')):
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                data = json.loads(f.read())
                # DBに挿入
                self.db.add_keyword(convert(data))
            # 不要なファイルを削除
            os.remove(json_file)
        # ログ
        self.log('Keyword settings have been imported')

    def preprocess(self):
        # 既存のファイルを~backupに退避
        for item in glob.glob(os.path.join(self.PROFILE_PATH, '*')):
            if os.path.isfile(item):
                shutil.copy(item, os.path.join(self.PROFILE_PATH, '~backup', os.path.basename(item)))
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(self.PROFILE_PATH, '~backup', os.path.basename(item)))

    def init_tables(self):
        # citiesテーブル作成
        json_file = os.path.join(self.DATA_PATH, 'json', 'cities.json')
        with open(json_file, encoding='utf-8') as f:
            for data in json.loads(f.read()):
                self.db.add_city(data)
        # holidaysテーブル作成
        json_file = os.path.join(self.DATA_PATH, 'json', 'holidays.json')
        with open(json_file, encoding='utf-8') as f:
            for data in json.loads(f.read()):
                self.db.add_holiday(data)
        # masterテーブル作成
        json_file = os.path.join(self.DATA_PATH, 'json', 'master.json')
        with open(json_file, encoding='utf-8') as f:
            for data in json.loads(f.read()):
                self.db.add_master(data)
        
    def postprocess(self):
        # ファイル/ディレクトリ削除
        items = [
            os.path.join(self.PROFILE_PATH, 'mmap.txt'),
            os.path.join(self.PROFILE_PATH, 'auth.json'),
            os.path.join(self.PROFILE_PATH, 'queue'),
            os.path.join(self.PROFILE_PATH, 'timetable'),
            os.path.join(self.PROFILE_PATH, 'stations', 'index'),
            os.path.join(self.PROFILE_PATH, 'stations', 'directory'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'csra'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'fmpp'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'jcba'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'lsnr'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'nhkr'),
            os.path.join(self.PROFILE_PATH, 'stations', 'logo', 'radk')
        ]
        for item in items:
            if os.path.exists(item):
                if os.path.isfile(item):
                    os.remove(item)
                if os.path.isdir(item):
                    shutil.rmtree(item)

    def run(self):
        self.preprocess()
        self.init_tables()
        self.import_stations()
        self.import_keywords()
        self.import_contents()
        self.postprocess()
