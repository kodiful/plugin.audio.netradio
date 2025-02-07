# -*- coding: utf-8 -*-

import os
import shutil
import glob
import json
from mutagen.mp3 import MP3

from resources.lib.common import Common
from resources.lib.db import DB


class Transfer(Common):

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
                'site': data['url'],
            }
        # DBに接続
        db = DB()
        # ダウンロードフォルダをスキャン
        for origdir in glob.glob(os.path.join(db.CONTENTS_PATH, '*')):
            if os.path.isdir(origdir) is False:
                continue
            # キーワード
            keyword = os.path.basename(origdir)
            # キーワードのkid, dirnameを取得
            sql = 'SELECT kid, dirname FROM keywords WHERE keyword = :keyword'
            db.cursor.execute(sql, {'keyword': keyword})
            try:
                kid, dirname = db.cursor.fetchone()
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
                    # abbrを抽出
                    basename = os.path.basename(mp3file)
                    abbr = basename.split('_')[-2]
                    # durationを抽出
                    duration = int(MP3(mp3file).info.length)
                    # DBに挿入
                    lastrowid = db.add(convert(data), kid, abbr, duration)
                    # DBの情報をmp3ファイルにID3タグとして書き込む
                    db.write_id3(mp3file, lastrowid)
                    # mp3ファイル名の移動先のファイル名を取得
                    sql = 'SELECT filename FROM contents WHERE cid = :cid'
                    db.cursor.execute(sql, {'cid': lastrowid})
                    filename, = db.cursor.fetchone()
                    # mp3ファイルをリネームして移動
                    destdir = os.path.join(Common.CONTENTS_PATH, dirname)
                    os.makedirs(destdir, exist_ok=True)
                    shutil.move(shutil.move(mp3file, filename), destdir)
            # 不要なファイルを退避
            destdir = os.path.join(Common.CONTENTS_PATH, '~backup')
            os.makedirs(destdir, exist_ok=True)
            shutil.move(origdir, destdir)
            # rssを生成
            if kid > 0: db.create_rss(kid, keyword, dirname)
        # rss（インデクス）を生成
        db.create_index()
        # DBから切断
        db.conn.close()
        # ログ
        db.log('Downloaded files have been imported')

    def import_stations(self):
        # データ変換関数
        def convert(data):
            return {
                'station': data['station'],
                'type': data['type'],
                'abbr': data['id'],
                'code': data['code'],
                'region': data['region'],
                'pref': data['pref'],
                'city': data['city'],
                'logo': data['logo'],
                'description': data['description'],
                'site': data['official'],
                'direct': data['stream']
            }
        # DBに接続
        db = DB()
        # dataフォルダ直下のcodes.jsonから読み込む
        json_file = os.path.join(db.DATA_PATH, 'codes.json')
        with open(json_file, encoding='utf-8') as f:
            for data in json.loads(f.read()):
                db.add_code(data)
        # プラグインの放送局フォルダ直下のjsonフォルダにあるjsonファイルから読み込む
        for json_file in glob.glob(os.path.join(db.DATA_PATH, 'stations', 'json', '*.json')):
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                for data in json.loads(f.read()):
                    # DBに挿入
                    db.add_station(data)
        # ユーザデータの放送局フォルダ直下のdirectoryフォルダにあるjsonファイルから読み込む
        for json_file in glob.glob(os.path.join(db.PROFILE_PATH, 'stations', 'directory', '*.json')):
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                data = json.loads(f.read())
            # ユーザ設定の放送局はDBに挿入
            if data['type'] == 'user':
                db.add_station(convert(data), top=1)
        # 不要なファイルを削除
        shutil.rmtree(os.path.join(db.PROFILE_PATH, 'stations', 'index'))
        shutil.rmtree(os.path.join(db.PROFILE_PATH, 'stations', 'directory'))
        # DBから切断
        db.conn.close()
        # ログ
        db.log('Station settings have been imported')

    def import_keywords(self):
        # データ変換関数
        def convert(data):
            if data['limit'] == 'true':
                sql = 'SELECT station FROM stations WHERE abbr = :abbr'
                db.cursor.execute(sql, {'abbr': data['id']})
                station, = db.cursor.fetchone()
            else:
                station = ''
            return {
                'status': '1',
                'keyword': data['keyword'],
                'match': data['search'],
                'weekday': data['weekday'],
                'station': station,
            }
        # DBに接続
        db = DB()
        # キーワードフォルダをスキャン
        for image_file in glob.glob(os.path.join(db.PROFILE_PATH, 'keywords', '*.png')):
            # 古いファイルを削除
            os.remove(image_file)
        for json_file in glob.glob(os.path.join(db.PROFILE_PATH, 'keywords', '*.json')):
            with open(json_file, encoding='utf-8') as f:
                # jsonファイルを読み込む
                data = json.loads(f.read())
                # DBに挿入
                db.add_keyword(convert(data))
            # 不要なファイルを削除
            os.remove(json_file)
        # DBから切断
        db.conn.close()
        # ログ
        db.log('Keyword settings have been imported')

    def backup_files(self):
        for item in glob.glob(os.path.join(self.PROFILE_PATH, '*')):
            if os.path.isfile(item):
                shutil.copy(item, os.path.join(self.PROFILE_PATH, '~backup', os.path.basename(item)))
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(self.PROFILE_PATH, '~backup', os.path.basename(item)))
        
    def cleanup_files(self):
        try:
            os.remove(os.path.join(self.PROFILE_PATH, 'mmap.txt'))
            os.remove(os.path.join(self.PROFILE_PATH, 'auth.json'))
            shutil.rmtree(os.path.join(self.PROFILE_PATH, 'queue'))
            shutil.rmtree(os.path.join(self.PROFILE_PATH, 'timetable', 'timetable'))
        except Exception:
            pass

    def run(self):
        self.backup_files()
        self.import_stations()
        self.import_keywords()
        self.import_contents()
        self.cleanup_files()
