# -*- coding: utf-8 -*-

import os
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from mutagen.mp3 import MP3

from resources.lib.common import Common
from resources.lib.db_schema import Schema
from resources.lib.db_utilities import Utilities, load_logo, create_qrcode


# DBの共有インスタンスを格納するスレッドローカルデータ
ThreadLocal = threading.local()


class DB(Common, Schema, Utilities):

    def __init__(self):
        # DBへ接続
        self.conn = sqlite3.connect(self.DB_FILE, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # テーブルを初期化
        self.cursor.execute(self.sql_contents)
        self.cursor.execute(self.sql_trigger)
        self.cursor.execute(self.sql_keywords)
        self.cursor.execute(self.sql_stations)
        self.cursor.execute(self.sql_cities)
        self.cursor.execute(self.sql_holidays)
        self.cursor.execute(self.sql_master)
        self.cursor.execute(self.sql_auth)
        self.cursor.execute(self.sql_status)
        # 現在時刻取得関数
        def now():
            jst = timezone(timedelta(hours=9))
            return datetime.now(timezone.utc).astimezone(jst).strftime("%Y-%m-%d %H:%M:%S")
        self.conn.create_function('NOW', 0, now)
        # epoch時間変換関数
        def epoch(time_str):
            dt = self.datetime(time_str)
            return int(dt.timestamp())
        self.conn.create_function('EPOCH', 1, epoch)

    def add(self, data, kid=0, mp3_file=None):
        # 終了済みだったら何もしない
        if mp3_file is None and data['end'] < self.now():
            return 0
        # データを補完
        title = data['title']
        description = self.description(data)
        station = data['station']
        start = data['start']
        end = data['end']
        filename = os.path.basename(mp3_file) if mp3_file else self.filename(station, start, end)
        duration = int(MP3(mp3_file).info.length) if mp3_file else 0
        # 放送局設定
        sql = 'SELECT sid, top, vis FROM stations WHERE station = :station AND region = :region AND pref = :pref'
        self.cursor.execute(sql, {'station': data['station'], 'region': data['region'], 'pref': data['pref']})
        sid, top, vis = self.cursor.fetchone()
        # キーワード設定（kid, filename, cstatus）
        if kid > 0:
            if mp3_file:
                kid, filename, cstatus = kid, filename, -1  # ダウンロード済み
            else:
                kid, filename, cstatus = 0, '', 0
        elif kid == -1:
            if self.GET('download') == 'true' and vis == 1:
                kid, filename, cstatus = kid, filename, 1  # ダウンロード予定
            else:
                kid, filename, cstatus = 0, '', 0
        else:
            if self.GET('download') == 'true':
                kid = self.keyword_match(title, description, station, start, top * vis)
                if kid > 0:
                    filename, cstatus = filename, 1  # ダウンロード予定
                else:
                    filename, cstatus = '', 0
            else:
                kid, filename, cstatus = 0, '', 0
        # DBに投入
        values = {
            'sid': sid,
            'kid': kid,
            'cstatus': cstatus,
            'filename': filename,
            'title': title,
            'start': start,
            'end': end,
            'station': station,
            'duration': duration,
            'act': data.get('act', ''),
            'info': data.get('info', ''),
            'desc': data.get('desc', ''),
            'description': description,
            'site': data.get('site', ''),
            'version': self.ADDON_VERSION,
            'modified': self.now()
        }
        # DBに追加
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR IGNORE INTO contents ({columns}) VALUES ({placeholders})'
        result = self.cursor.execute(sql, list(values.values()))
        return result.rowcount and self.cursor.lastrowid

    def add_master(self, values):
        values.update({
            'mstatus': 0,
            'version': self.ADDON_VERSION,
            'modified': self.now()
        })
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO master ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))

    def add_city(self, values):
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO cities ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))

    def add_holiday(self, values):
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO holidays ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
    
    def add_station(self, data, top=0, vis=1):
        values = {
            'top': data.get('top', top),
            'vis': data.get('vis', vis),
            'protocol': data.get('protocol', 'USER'),
            'key': data.get('key', ''),
            'station': data.get('station', ''),
            'code': data.get('code', ''),
            'region': data.get('region', ''),
            'pref': data.get('pref', ''),
            'city': data.get('city', ''),
            'logo': data.get('logo', ''),
            'description': data.get('description', ''),
            'site': data.get('site'),
            'direct': data.get('direct', ''),
            'delay': data.get('delay', 0),
            'nextaired': '1970-01-01 09:00:00',
            'version': self.ADDON_VERSION,
            'modified': self.now()
        }
        sid = int(data.get('sid', '0'))
        if sid > 0:
            values.update({'sid': sid})
        # DBに追加/更新
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR REPLACE INTO stations ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        # 画像作成
        dir = os.path.join(self.PROFILE_PATH, 'stations', 'logo')
        load_logo(data, dir, force=False)

    def delete_station(self, sid):
        sql = '''DELETE FROM stations WHERE sid = :sid'''
        self.cursor.execute(sql, {'sid': sid})

    def add_keyword(self, data):
        values = {
            'dirname': '',
            'keyword': data['keyword'],
            'match': int(data['match']),
            'weekday': int(data['weekday']),
            'station': data['station'],
            'kstatus': int(data['kstatus']),
            'version': self.ADDON_VERSION,
            'modified': self.now()
        }
        kid = int(data.get('kid', '0'))
        if kid > 0:
            values.update({'kid': kid})
        # DBに追加/更新
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR REPLACE INTO keywords ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        # dirnameを設定
        kid = self.cursor.lastrowid
        dirname = str(kid)
        sql = 'UPDATE keywords SET dirname = :dirname WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid, 'dirname': dirname})
        # 画像作成
        url = '/'.join([self.GET('rssurl'), dirname, 'rss.xml'])
        path = os.path.join(self.PROFILE_PATH, 'keywords', 'qr', f'{kid}.png')
        create_qrcode(url, path)
        # 既存のcontentsと照合
        sql = '''SELECT c.cid, c.title, c.description, c.station, c.start, c.end, s.top, s.vis 
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid 
        WHERE c.cstatus = 0 AND c.end > NOW()'''
        self.cursor.execute(sql)
        for cid, title, description, station, start, end, top, vis in self.cursor.fetchall():
            kid = self.keyword_match(title, description, station, start, top * vis)
            if kid > 0:
                sql = 'UPDATE contents SET kid = :kid, filename = :filename, cstatus = 1 WHERE cid = :cid'
                self.cursor.execute(sql, {'cid': cid, 'kid': kid, 'filename': self.filename(station, start, end)})

    def delete_keyword(self, kid):
        sql = 'DELETE FROM keywords WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid})
        sql = 'DELETE FROM contents WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid})
