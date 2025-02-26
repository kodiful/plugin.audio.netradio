# -*- coding: utf-8 -*-

import os
import shutil
import urllib.request
import urllib.error
from mutagen.id3 import ID3, TIT2, TDRC, WPUB, TPUB, COMM
from PIL import Image
from sqlite3 import dbapi2 as sqlite

from resources.lib.common import Common


class Utilities():

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
    
    def filename(self, station, start, end):
        # 2025-02-04 21:24:00
        filename = f'{start[0:4]}-{start[5:7]}{start[8:10]}-{start[11:13]}{start[14:16]}-{end[11:13]}{end[14:16]} {station}.mp3'
        return filename
    
    def keyword_match(self, title, description, station, start, topvis):
        # startを曜日に変換
        start = self.weekday(start)
        # 各キーワード設定と照合
        self.cursor.execute('SELECT kid, keyword, match, weekday, station FROM keywords WHERE kstatus = 1')
        for kid, keyword, match, weekday, source in self.cursor.fetchall():
            # 曜日
            if weekday != 7 and weekday != start:
                continue
            # キーワード
            if match == 0 and title.find(keyword) < 0:
                continue
            if match == 1 and title.find(keyword) < 0 and description.find(keyword) < 0:
                continue
            # 放送局
            if source == '' and topvis == 0:
                continue
            if source != '' and source != station:
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
        sql = f'SELECT code, region, pref, city, station, site, SJ, LR, SR, SP, SD FROM master WHERE {protocol} = :station'
        self.cursor.execute(sql, {'station': station})
        results = self.cursor.fetchone()
        if results:
            code, region, pref, city, station, site, SJ, LR, SR, SP, SD = results
            # 優先するprotocolを判定する
            status = False
            if LR: status = protocol == 'LR'
            elif SJ: status = protocol == 'SJ'
            elif SP: status = protocol == 'SP'
            elif SR: status = protocol == 'SR'
            elif SD: status = protocol == 'SD'
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
