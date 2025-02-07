# -*- coding: utf-8 -*-

import os
import sqlite3
import re
import threading
from datetime import datetime, timezone, timedelta
from mutagen.id3 import ID3, TIT2, TDRC, WPUB, TPUB, COMM

from resources.lib.common import Common
from resources.lib.stations.common import load_logo


ThreadLocal = threading.local()


class DB(Common):

    sql_contents = '''
    CREATE TABLE IF NOT EXISTS contents(
        status INTEGER,
        station TEXT,
        title TEXT,
        start TEXT,
        end TEXT,
        filename TEXT,
        duration INTEGER,
        act TEXT,
        info TEXT,
        desc TEXT,
        description TEXT,
        site TEXT,
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        sid INTEGER,
        kid INTEGER,
        version TEXT,
        modified TEXT,
        UNIQUE(sid, start)
    )'''

    # status
    # -2: failed
    # -1: downloaded
    # 0: pass
    # 1: pending
    # 2: threaded
    # 3: downloading

    sql_trigger = '''
    CREATE TRIGGER IF NOT EXISTS update_modified AFTER UPDATE OF status ON contents
    BEGIN
        UPDATE contents SET modified = DATETIME('now', '+9 hours') WHERE cid = NEW.cid;
    END'''

    sql_stations = '''
    CREATE TABLE IF NOT EXISTS stations(
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        top INTEGER,
        station TEXT,
        type TEXT,
        abbr TEXT,
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        logo TEXT,
        description TEXT,
        site TEXT,
        direct TEXT,
        match INTEGER,
        version TEXT,
        modified TEXT
    )'''

    sql_keywords = '''
    CREATE TABLE IF NOT EXISTS keywords(
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        keyword TEXT,
        match TEXT,
        weekday TEXT,
        station TEXT,
        dirname TEXT UNIQUE,
        version TEXT,
        modified TEXT
    )'''

    sql_codes = '''
    CREATE TABLE IF NOT EXISTS codes(
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        radiko TEXT
    )'''

    sql_auth = '''
    CREATE TABLE IF NOT EXISTS auth(
        auth_key TEXT,
        auth_token TEXT,
        area_id TEXT,
        authed INTEGER,
        key_offset INTEGER,
        key_length INTEGER,
        partial_key TEXT
    )'''

    sql_auth_init = '''
    DELETE FROM auth;
    INSERT INTO auth VALUES ('', '', '', 0, 0, 0, '');
    '''

    sql_status = '''
    CREATE TABLE IF NOT EXISTS status(
        timetable INTEGER,
        keyword TEXT,
        station TEXT
    )'''

    sql_status_init = '''
    DELETE FROM status;
    INSERT INTO status VALUES(0, '', '');
    '''

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
        self.cursor.execute(self.sql_codes)
        self.cursor.execute(self.sql_auth)
        self.cursor.execute(self.sql_status)
        # 現在時刻取得関数
        def now():
            jst = timezone(timedelta(hours=9))
            return datetime.now(timezone.utc).astimezone(jst).strftime("%Y-%m-%d %H:%M:%S")
        self.now = now()  # 2025-02-06 07:13:58
        self.conn.create_function('NOW', 0, now)
        # epoch時間変換関数
        def epoch(time_str):
            return int(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timestamp())
        self.conn.create_function('EPOCH', 1, epoch)
        # 古い番組情報を削除
        self.cursor.execute('DELETE FROM contents WHERE status = 0 and end < NOW()')

    def add(self, data, kid=0, abbr='', duration=0):
        # title
        title = data['title']
        # description
        description = self._description(data)
        # sid, match, filename
        sid, match, filename = self._station(data, abbr)
        # kid, duration, status
        if kid > 0:
            if duration > 0:
                kid, filename, status = kid, filename, -1
            else:
                kid, filename, status = 0, '', 0
        else:
            if self.GET('download') == 'true' and match == 1:
                kid, filename, status = self._keyword_match(data, title, description)
            else:
                kid, filename, status = 0, '', 0
        # DBに投入
        values = {
            'sid': sid,
            'kid': kid,
            'status': status,
            'filename': filename,
            'title': title,
            'start': data['start'],
            'end': data['end'],
            'station': data['station'],
            'duration': duration,
            'act': data['act'],
            'info': data['info'],
            'desc': data['desc'],
            'description': description,
            'site': data['site'],
            'version': self.ADDON_VERSION,
            'modified': self.now
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR IGNORE INTO contents ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        return self.cursor.lastrowid

    def add_code(self, values):
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO codes ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        return self.cursor.lastrowid

    def add_station(self, data, top=0):
        values = {
            'top': top,
            'type': data['type'],
            'abbr': data['abbr'],
            'station': data['station'],
            'code': data.get('code', ''),
            'region': data.get('region', ''),
            'pref': data.get('pref', ''),
            'city': data.get('city', ''),
            'logo': data['logo'],
            'description': data['description'],
            'site': data['site'],
            'direct': data['direct'],
            'match': data.get('match', 0),
            'version': self.ADDON_VERSION,
            'modified': self.now
        }
        sid = data.get('sid', '0')
        if int(sid) > 0:
            values.update({'sid': sid})
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR REPLACE INTO stations ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        # ロゴ
        load_logo(data, os.path.join(self.PROFILE_PATH, 'stations', 'logo'), force=False)
        return self.cursor.lastrowid

    def delete_station(self, sid):
        sql = '''DELETE FROM stations WHERE sid = :sid'''
        self.cursor.execute(sql, {'sid': sid})

    def add_keyword(self, data):
        values = {
            'status': data['status'],
            'dirname': '',
            'keyword': data['keyword'],
            'match': data['match'],
            'weekday': data['weekday'],
            'station': data['station'],
            'version': self.ADDON_VERSION,
            'modified': self.now
        }
        kid = data.get('kid', '0')
        if int(kid) > 0:
            values.update({'kid': kid})
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR REPLACE INTO keywords ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
        # dirnameを設定
        sql = 'UPDATE keywords SET dirname = :dirname WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': self.cursor.lastrowid, 'dirname': str(self.cursor.lastrowid)})
        # 既存のcontentsと照合
        sql = 'SELECT * FROM contents c JOIN stations s ON c.sid = s.sid WHERE c.status = 0 AND c.end > NOW()'
        self.cursor.execute(sql)
        for csdata in self.cursor.fetchall():
            kid, filename, status = self._keyword_match(dict(csdata), csdata['title'], csdata['description'], abbr=csdata['abbr'])
            if status > 0:
                sql = 'UPDATE contents SET kid = :kid, filename = :filename, status = 1 WHERE cid = :cid'
                self.cursor.execute(sql, {'cid': csdata['cid'], 'kid': kid, 'filename': filename})
        return self.cursor.lastrowid

    def delete_keyword(self, kid):
        sql = 'DELETE FROM keywords WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid})

    def write_id3(self, mp3file, cid):
        sql = 'SELECT * FROM contents WHERE cid = :cid'
        self.cursor.execute(sql, {'cid': cid})
        data = self.cursor.fetchone()
        id3 = ID3(mp3file)
        id3['TIT2'] = TIT2(encoding=3, text=data['title'])  # encoding=3 -> UTF-8で書き込み
        id3['TDRC'] = TDRC(encoding=3, text=data['start'])
        id3['TPUB'] = TPUB(encoding=3, text=data['station'])
        id3['COMM'] = COMM(encoding=3, text=data['description'])
        if data['site']:
            id3['WPUB'] = WPUB(url=data['site'])
        id3.save(v2_version=4)  # ID3v2.4 形式で保存

    def _description(self, data):
        description = ''
        for key in ('act', 'desc', 'info'):
            value = data.get(key)
            if value:
                description += f'<p class="{key}">{value}</p>'
        return description

    def _station(self, cdata, abbr=''):
        if cdata.get('region'):
            sql = 'SELECT sid, abbr, match FROM stations WHERE station = :station and region = :region AND pref = :pref'
            self.cursor.execute(sql, {'station': cdata['station'], 'region': cdata['region'], 'pref': cdata['pref']})
            sid, abbr, match = self.cursor.fetchone()
        elif abbr:
            sql = 'SELECT sid FROM stations WHERE abbr = :abbr'
            self.cursor.execute(sql, {'abbr': abbr})
            sid, = self.cursor.fetchone()  # ダウンロードのアイコン画像用にsidを付与
            match = 0
        else:
            sid, abbr, match = 0, 'unknown', 0
        start = cdata['start']  # 2025-02-04 21:24:00
        end = cdata['end']
        filename = f'{abbr}-{start[0:4]}{start[5:7]}{start[8:10]}-{start[11:13]}{start[14:16]}-{end[11:13]}{end[14:16]}.mp3'
        return sid, match, filename
    
    def _keyword_match(self, cdata, title, description, abbr=''):
        sql = "SELECT kid, keyword, match, weekday, station FROM keywords WHERE status = '1'"
        self.cursor.execute(sql)
        for kid, keyword, match, weekday, station in self.cursor.fetchall():
            today = datetime.strptime(cdata['start'], '%Y-%m-%d %H:%M:%S').weekday()
            if weekday != '7' and weekday != str(today):
                continue
            if station != '' and station != cdata['station']:
                continue
            if match == '0' and title.find(keyword) < 0:
                continue
            if match == '1' and description.find(keyword) < 0:
                continue
            _, _, filename = self._station(cdata, abbr)
            return kid, filename, 1
        else:
            return 0, '', 0

    # 都道府県、市区町村を検索する
    def search_by_pref(self, pref):
        sql = "SELECT * FROM codes WHERE pref = :pref AND city = ''"
        self.cursor.execute(sql, {'pref': pref})
        result = self.cursor.fetchone()
        return dict(result)

    def search_by_city(self, city):
        sql = "SELECT * FROM codes WHERE city = :city"
        self.cursor.execute(sql, {'city': city})
        result = self.cursor.fetchone()
        return dict(result)

    def search_by_radiko(self, radiko):
        sql = "SELECT * FROM codes WHERE radiko = :radiko AND city = ''"
        self.cursor.execute(sql, {'radiko': radiko})
        result = self.cursor.fetchone()
        return dict(result)

    # 都道府県、市区町村を推定する
    def infer_place(self, text):
        # 正規表現
        self.cursor.execute("SELECT DISTINCT(pref) FROM codes WHERE pref != ''")
        REGEX_PREFS = '(%s)' % '|'.join([pref for pref, in self.cursor.fetchall()])
        self.cursor.execute("SELECT DISTINCT(city) FROM codes WHERE city != ''")
        REGEX_CITIES = '(%s)' % '|'.join([city for city, in self.cursor.fetchall()])
        # マッチング
        code = ''
        region = ''
        pref = ''
        city = ''
        # 都道府県
        match = re.search(REGEX_PREFS, text)
        if match:
            pref = match.group(1)
            item = self.search_by_pref(pref)
            code = item['code']
            region = item['region']
        # 市町村
        match = re.search(REGEX_CITIES, text)
        if match:
            city = match.group(1)
            item = self.search_by_city(city)
            code = item['code']
            pref = item['pref']
            region = item['region']
        return code, region, pref, city

    def radiko_place(self, code):
        item = self.search_by_radiko(code)
        code = item['code']
        pref = item['pref']
        region = item['region']
        return code, region, pref
