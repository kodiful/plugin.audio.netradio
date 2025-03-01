# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime

import xbmc
import xbmcgui

from .common import Common
from resources.lib.rss import Keywords


class Keyword(Common):
        
    def __init__(self):
        super().__init__()
        # 表示中の放送局リストを取得
        sql = '''SELECT s.station
        FROM status JOIN json_each(status.front) AS je ON je.value = s.sid JOIN stations AS s ON je.value = s.sid'''
        self.db.cursor.execute(sql)
        self.stations = [station for station, in self.db.cursor.fetchall()]
        # 表示中の放送局が無い場合はトップ画面の放送局リストを取得
        if len(self.stations) == 0:
            self.db.cursor.execute('SELECT station FROM stations WHERE top = 1 AND vis = 1')
            self.stations = [station for station, in self.db.cursor.fetchall()]
        # リストの先頭に"トップ画面の放送局"を追加
        self.stations = [self.STR(30529)] + self.stations        

    def prep(self):
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'keyword.xml')) as f:
            self.template = f.read()
        # テンプレートのstationsを置換
        self.template = self.template.format(stations='|'.join(self.stations))
 
    def get(self, kid=0, sid=0, title='', station=''):
        xbmc.sleep(1000)
        if kid > 0:
            # キーワード設定変更
            sql = 'SELECT kid, kstatus, keyword, match, weekday, station FROM keywords WHERE kid = :kid'
            self.db.cursor.execute(sql, {'kid': kid})
            kid, kstatus, keyword, match, weekday, station = self.db.cursor.fetchone()
            self.SET('kid', str(kid))
            self.SET('kstatus', ['false','true'][kstatus])
            self.SET('keyword', keyword)
            self.SET('match', str(match))
            self.SET('weekday', str(weekday))
            self.SET('station', station or self.stations[0])
        elif sid > 0:
            # 番組情報からのキーワード設定
            weekday = datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('kstatus', 'true')  # 実行中
            self.SET('keyword', title)
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        else:
            # 新規キーワード設定
            weekday = datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('kstatus', 'true')  # 実行中
            self.SET('keyword', '')
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', self.stations[0])

    def set(self):
        # 設定後の値
        keys = ('kid', 'kstatus', 'keyword', 'match', 'weekday', 'station')
        settings = dict([(key, self.GET(key)) for key in keys])
        # kstatusをDB用に型変換する
        settings['kstatus'] = 1 if settings['kstatus'] == 'true' else 0
        settings['station'] = '' if settings['station'] == self.stations[0] else settings['station']
        # 放送局を指定する場合はtop=1を設定する
        if settings['station']:
            if settings['station'].startswith('NHK'):
                sql = "UPDATE stations SET top = 1 WHERE protocol = 'NHK' AND station = :station"
                self.db.cursor.execute(sql, {'station': settings['station']})
            else:
                sql = "UPDATE stations SET top = 1 WHERE station = :station"
                self.db.cursor.execute(sql, {'station': settings['station']})
        # !!!ここでデータのバリデーション
        # keywordテーブルに書き込む
        self.db.add_keyword(settings)
        # RSSインデクス再作成
        Keywords().create_index()
        # 再描画
        self.refresh()

    def delete(self):
        # キーワード情報取得
        kid = self.GET('kid')
        sql = 'SELECT kid, keyword, dirname FROM keywords WHERE kid = :kid'
        self.db.cursor.execute(sql, {'kid': int(kid)})
        kid, keyword, dirname = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno(self.STR(30156), self.STR(30157) % keyword)
        if ok:
            # ファイル削除
            download_path = os.path.join(self.CONTENTS_PATH, dirname)
            if os.path.exists(download_path):
                shutil.rmtree(download_path)
            # キーワード削除
            self.db.delete_keyword(kid)
            # RSSインデクス再作成
            Keywords().create_index()
            # 再描画
            self.refresh()
