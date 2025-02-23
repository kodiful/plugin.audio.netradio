# -*- coding: utf-8 -*-

import os
import shutil
import glob
import json

from resources.lib.common import Common
from resources.lib.db import ThreadLocal, create_qrcode
from resources.lib.contents import Contents


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
        # ログ
        self.log('import_contents: enter')
        # CONTENTS_PATHが無い場合はなにもしない
        if os.path.exists(Common.CONTENTS_PATH) is False:
            return
        # 地域、都道府県
        auth_region = auth_pref = ''
        path = os.path.join(self.PROFILE_PATH, 'auth.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                auth = json.loads(f.read())
            sql = self.db.cursor.execute('SELECT region, pref FROM cities WHERE area_id = :area_id', {'area_id': auth['area_id']})
            auth_region, auth_pref =self.db.cursor.fetchone()
            self.log('auth results found:', 'region:', auth_region, 'pref:', auth_pref)
        # データ変換関数
        def _datetime(date):
            return f'{date[0:4]}-{date[4:6]}-{date[6:8]} {date[8:10]}:{date[10:12]}:{date[12:14]}'
        def convert(data, key, region, pref):
            protocol = self.PROTOCOL[data['type']]
            start = _datetime(data['START'])
            end = _datetime(data['END'])
            return {
                'station': data['station'],
                'protocol': protocol,
                'key': key,
                'title': data['title'],
                'start': start,
                'end': end,
                'act': data['act'],
                'info': data['info'],
                'desc': data['desc'],
                'site': data['url'] or '',
                'region': region,
                'pref': pref
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
            for mp3_file in glob.glob(os.path.join(origdir, '*.mp3')):
                # 対応するjsonファイル
                json_file = '%s.json' % os.path.splitext(mp3_file)[0]
                if os.path.exists(json_file):
                    # jsonファイルを読み込む
                    with open(json_file, encoding='utf-8') as f:
                        data = json.loads(f.read())
                    # key, region, prefを推定
                    protocol = self.PROTOCOL[data['type']]
                    sql = 'SELECT key, region, pref FROM stations WHERE protocol = :protocol AND station = :station'
                    if protocol == 'NHK' and auth_region != '':
                        sql = f'{sql} AND region = :region'
                        self.db.cursor.execute(sql, {'protocol': protocol, 'station': data['station'], 'region': auth_region})
                        key, region, pref = self.db.cursor.fetchone()
                    elif protocol == 'RDK' and auth_pref != '':
                        sql = f'{sql} AND pref = :pref'
                        self.db.cursor.execute(sql, {'protocol': protocol, 'station': data['station'], 'pref': auth_pref})                            
                        key, region, pref = self.db.cursor.fetchone()
                    else:
                        self.db.cursor.execute(sql, {'protocol': protocol, 'station': data['station']})
                        key, region, pref = self.db.cursor.fetchone()
                    # DBに挿入
                    lastrowid = self.db.add(convert(data, key, region, pref), kid, mp3_file)
                    # DBの情報をmp3ファイルにID3タグとして書き込む
                    self.db.write_id3(mp3_file, lastrowid)
                    # mp3ファイル名の移動先のファイル名を取得
                    sql = 'SELECT filename FROM contents WHERE cid = :cid'
                    self.db.cursor.execute(sql, {'cid': lastrowid})
                    filename = os.path.basename(mp3_file)
                    # mp3ファイルをリネームして移動
                    destdir = os.path.join(Common.CONTENTS_PATH, dirname)
                    os.makedirs(destdir, exist_ok=True)
                    shutil.move(mp3_file, destdir)
            # 不要なファイルを退避
            destdir = os.path.join(Common.CONTENTS_PATH, '~backup')
            os.makedirs(destdir, exist_ok=True)
            shutil.move(origdir, destdir)
        # rss & インデクスを生成
        Contents().update_rss()
        # ログ
        self.log('import_contents: exit')

    def import_stations(self):
        # ログ
        self.log('import_stations: enter')
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
            }
        # プラグインの放送局フォルダ直下のjsonフォルダにあるjsonファイルから読み込む
        for json_file in [os.path.join(self.DATA_PATH, 'stations', 'json', f'{protocol}.json') for protocol in ('NHK', 'RDK', 'LR', 'SJ', 'SP', 'SR', 'SD')]:
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
        self.log('import_stations: exit')

    def import_keywords(self):
        # ログ
        self.log('import_keywords: enter')
        # データ変換関数
        def convert(data):
            if data['limit'] == 'true':
                sql = 'SELECT station FROM stations WHERE key = :key'
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
        self.log('import_keywords: exit')

    def preprocess(self):
        # 退避先のディレクトリを確保
        destdir = os.path.join(self.PROFILE_PATH, '~backup')
        os.makedirs(destdir, exist_ok=True)
        # 不要なファイルを退避
        for item in glob.glob(os.path.join(self.PROFILE_PATH, '*')):
            if os.path.basename(item) == '~backup':
                continue
            if os.path.isfile(item):
                shutil.copy(item, os.path.join(destdir, os.path.basename(item)))
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(destdir, os.path.basename(item)))
        # 放送局のロゴ画像をコピー
        path = os.path.join(self.PROFILE_PATH, 'stations', 'logo')
        shutil.rmtree(path)
        shutil.copytree(os.path.join(self.DATA_PATH, 'stations', 'logo'), path)

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
        # keywordテーブル作成
        values = {
            'kid': -1,
            'keyword': Common.STR(30004),
            'match': 0,
            'weekday': 0,
            'station': '',
            'kstatus': 0,
            'dirname': '0',
            'version': self.db.ADDON_VERSION,
            'modified': self.now()
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO keywords ({columns}) VALUES ({placeholders})'
        self.db.cursor.execute(sql, list(values.values()))
        # QRコード画像作成
        url = '/'.join([self.GET('rssurl'), values['dirname'], 'rss.xml'])
        path = os.path.join(self.PROFILE_PATH, 'keywords', 'qr', str(values['kid']) + '.png')
        create_qrcode(url, path)

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
