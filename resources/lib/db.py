# -*- coding: utf-8 -*-

import os
import sqlite3
import re
import threading
import shutil
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TDRC, WPUB, TPUB, COMM
from PIL import Image
from qrcode import QRCode
from sqlite3 import dbapi2 as sqlite

from resources.lib.common import Common


# DBの共有インスタンスを格納するスレッドローカルデータ
ThreadLocal = threading.local()


class DB(Common):

    sql_contents = '''
    CREATE TABLE IF NOT EXISTS contents(
        cstatus INTEGER,
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

    # cstatus
    # -2: failed
    # -1: downloaded
    # 0: pass
    # 1: pending
    # 2: threaded
    # 3: downloading

    sql_trigger = '''
    CREATE TRIGGER IF NOT EXISTS update_modified AFTER UPDATE OF cstatus ON contents
    BEGIN
        UPDATE contents SET modified = DATETIME('now', '+9 hours') WHERE cid = NEW.cid;
    END'''

    sql_stations = '''
    CREATE TABLE IF NOT EXISTS stations(
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        top INTEGER,
        vis INTEGER,
        station TEXT,
        protocol TEXT,
        key TEXT,
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        logo TEXT,
        description TEXT,
        site TEXT,
        direct TEXT,
        delay INTEGER,
        nextaired TEXT,
        version TEXT,
        modified TEXT
    )'''

    sql_keywords = '''
    CREATE TABLE IF NOT EXISTS keywords(
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        match INTEGER,
        weekday INTEGER,
        station TEXT,
        dirname TEXT UNIQUE,
        kstatus INTEGER,
        version TEXT,
        modified TEXT
    )'''

    # kstatus
    # 0: inactive
    # 1: active

    sql_cities = '''
    CREATE TABLE IF NOT EXISTS cities(
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        area_id TEXT
    )'''

    sql_holidays = '''
    CREATE TABLE IF NOT EXISTS holidays(
        date TEXT,
        name TEXT
    )'''

    sql_master = '''
    CREATE TABLE IF NOT EXISTS master(
        mid INTEGER PRIMARY KEY AUTOINCREMENT,
        station TEXT UNIQUE,
        region TEXT,
        pref TEXT,
        city TEXT,
        code TEXT,
        site TEXT,
        SJ TEXT,
        LR TEXT,
        SR TEXT,
        SP TEXT,
        SD TEXT,
        mstatus INTEGER,
        version TEXT,
        modified TEXT
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
        front TEXT,
        refresh TEXT
    )'''

    sql_status_init = '''
    DELETE FROM status;
    INSERT INTO status VALUES('[]', '1970-01-01 09:00:00');
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
        duration = int(MP3(mp3_file).info.length) if mp3_file else 0
        # 放送局設定
        sql = 'SELECT sid, top FROM stations WHERE station = :station AND region = :region AND pref = :pref'
        self.cursor.execute(sql, {'station': data['station'], 'region': data['region'], 'pref': data['pref']})
        # !!!ここでエラー、たぶん複数地域の放送局情報が登録されているときタイマー予約で受信可能な放送局を正しく判定できていない
        sid, top = self.cursor.fetchone()
        # キーワード設定（kid, filename, cstatus）
        if kid > 0:
            if mp3_file:
                kid, filename, cstatus = kid, os.path.basename(mp3_file), -1  # ダウンロード済み
            else:
                kid, filename, cstatus = 0, '', 0
        elif kid == -1:
            if self.GET('download') == 'true' and top == 1:
                kid, filename, cstatus = kid, self.filename(data), 1  # ダウンロード予定
            else:
                kid, filename, cstatus = 0, '', 0
        else:
            if self.GET('download') == 'true' and top == 1:
                kid = self.keyword_match(data, title, description)
                if kid > 0:
                    filename, cstatus = self.filename(data), 1  # ダウンロード予定
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
            'title': data['title'],
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
        sql = '''SELECT * 
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid 
        WHERE c.cstatus = 0 AND c.end > NOW()'''
        self.cursor.execute(sql)
        for csdata in self.cursor.fetchall():
            kid = self.keyword_match(dict(csdata), csdata['title'], csdata['description'])
            filename = self.filename(dict(csdata))
            if kid > 0:
                sql = 'UPDATE contents SET kid = :kid, filename = :filename, cstatus = 1 WHERE cid = :cid'
                self.cursor.execute(sql, {'cid': csdata['cid'], 'kid': kid, 'filename': filename})

    def delete_keyword(self, kid):
        sql = 'DELETE FROM keywords WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid})
        sql = 'DELETE FROM contents WHERE kid = :kid'
        self.cursor.execute(sql, {'kid': kid})

    def write_id3(self, mp3_file, cid):
        sql = 'SELECT * FROM contents WHERE cid = :cid'
        self.cursor.execute(sql, {'cid': cid})
        data = self.cursor.fetchone()
        id3 = ID3(mp3_file)
        id3['TIT2'] = TIT2(encoding=3, text=data['title'])  # encoding=3 -> UTF-8で書き込み
        id3['TDRC'] = TDRC(encoding=3, text=data['start'])
        id3['TPUB'] = TPUB(encoding=3, text=data['station'])
        id3['COMM'] = COMM(encoding=3, text=data['description'])
        if data['site']:
            id3['WPUB'] = WPUB(url=data['site'])
        id3.save(v2_version=4)  # ID3v2.4 形式で保存

    def description(self, data):
        description = ''
        for key in ('act', 'desc', 'info'):
            value = data.get(key)
            if value:
                description += f'<p class="{key}">{value}</p>'
        return description
    
    def filename(self, cdata):
        station = cdata['station']
        start = cdata['start']  # 2025-02-04 21:24:00
        end = cdata['end']
        filename = f'{start[0:4]}-{start[5:7]}{start[8:10]}-{start[11:13]}{start[14:16]}-{end[11:13]}{end[14:16]} {station}.mp3'
        return filename
    
    def keyword_match(self, cdata, title, description):
        sql = "SELECT kid, keyword, match, weekday, station FROM keywords WHERE kstatus = 1"
        self.cursor.execute(sql)
        for kid, keyword, match, weekday, station in self.cursor.fetchall():
            #today = datetime.strptime(cdata['start'], '%Y-%m-%d %H:%M:%S')
            #today = today.weekday()
            today = self.weekday(cdata['start'])
            if weekday != 7 and weekday != today:
                continue
            if station != '' and station != cdata['station']:
                continue
            if match == 0 and title.find(keyword) < 0:
                continue
            if match == 1 and description.find(keyword) < 0:
                continue
            return kid
        else:
            return 0

    # area_idを検索する
    def search_by_pref(self, pref):
        # 神奈川県
        sql = "SELECT area_id FROM cities WHERE :pref = pref"
        self.cursor.execute(sql, {'pref': pref})
        area_id, = self.cursor.fetchone()
        return area_id
    
    # 都道府県、市区町村を検索する
    def search_by_radiko(self, area_id):
        # JP14
        sql = "SELECT code, region, pref, city FROM cities WHERE area_id = :area_id AND city = ''"
        self.cursor.execute(sql, {'area_id': area_id})
        code, region, pref, city  = self.cursor.fetchone()
        return code, region, pref, city
    
    def search_by_joined(self, place):
        # 神奈川県横浜市
        sql = "SELECT code, region, pref, city FROM cities WHERE INSTR(:place, pref) = 1 AND INSTR(:place, city) = LENGTH(pref) + 1"
        self.cursor.execute(sql, {'place': place})
        return self.cursor.fetchone()
    
    def search_by_station(self, protocol, station):
        # 放送局名の表記の揺れを解決して名寄せする
        sql = f'SELECT code, region, pref, city, station, site, SJ, LR, SR, SP FROM master WHERE {protocol} = :station'
        self.cursor.execute(sql, {'station': station})
        results = self.cursor.fetchone()
        if results:
            code, region, pref, city, station, site, SJ, LR, SR, SP = results
            # 優先するprotocolを判定する
            status = False
            if LR: status = protocol == 'LR'
            elif SJ: status = protocol == 'SJ'
            elif SP: status = protocol == 'SP'
            elif SR: status = protocol == 'SR'
            return code, region, pref, city, station, site, status
        else:
            return None

    # 祝祭日を判定する
    def is_holiday(self, date):
        sql = 'SELECT COUNT(date) FROM holidays WHERE date = :date'
        self.cursor.execute(sql, {'date': date})
        count, = self.cursor.fetchone()
        return count > 0


# ロゴ画像を取得してサムネイル画像を作成
def load_logo(item, dir, force=False):
    # 画像のファイルパス
    dirname = os.path.join(dir, item['protocol'])
    os.makedirs(dirname, exist_ok=True)
    path = os.path.join(dirname, item['station'] + '.png')
    # ファイルを削除
    if force and os.path.exists(path):
        os.remove(path)
    # DBから画像のキャッシュを削除
    conn = sqlite.connect(Common.IMAGE_CACHE)
    sql = 'DELETE FROM texture WHERE url = :path'
    conn.cursor().execute(sql, {'path': path})
    conn.commit()
    conn.close()
    # 画像がある場合はなにもしない
    if os.path.exists(path):
        return
    # 画像格納用のディレクトリを用意
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # ロゴ画像を取得
    if item['logo']:
        try:
            req = urllib.request.Request(item['logo'], headers={'User-Agent': Common.USER_AGENT})
            res = urllib.request.urlopen(req)
            with open(path, 'wb') as f:
                    f.write(res.read())
        except urllib.error.HTTPError as e:
            Common.log(f'request error (code={e.code}):', item['logo'])
        except Exception as e:
            Common.log(f'request error:', item['logo'])
            Common.log(e)
    # 取得した画像をアイコン画像に加工する
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
    else:
        # 画像が取得できないときはデフォルトアイコンで代替する
        icon = os.path.join(Common.PLUGIN_PATH, 'resources', 'data', 'icons', 'audiodsp.png')
        shutil.copy(icon, path)

# QRコードのサムネイル画像を作成
def create_qrcode(url, path, force=False):
    # ファイルを削除
    if force and os.path.exists(path):
        os.remove(path)
    # DBから画像のキャッシュを削除
    conn = sqlite.connect(Common.IMAGE_CACHE)
    sql = 'DELETE FROM texture WHERE url = :path'
    conn.cursor().execute(sql, {'path': path})
    conn.commit()
    conn.close()
    # 画像がある場合はなにもしない
    if os.path.exists(path):
        return
    # 画像格納用のディレクトリを用意
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # 画像を生成
    qr = QRCode(version=1, box_size=10, border=4)
    qr.add_data(re.sub(r'^http(s?)://', r'podcast\1://', url))
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(path, 'PNG')
