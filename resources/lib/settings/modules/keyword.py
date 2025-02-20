# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
from datetime import datetime
from resources.lib.settings.common import Common
from resources.lib.settings.modules.timer import Timer
from resources.lib.contents import Contents

import xbmc
import xbmcgui


class Keyword(Common):
        
    def __init__(self):
        super().__init__()

    def prep(self):
        # トップ画面の放送局リストを取得
        self.db.cursor.execute('SELECT station FROM stations WHERE download = 1 OR top = 1 ORDER BY sid')
        stations = [''] + [station for station, in self.db.cursor.fetchall()]
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'keyword.xml')) as f:
            self.template = f.read()
        # テンプレートのstationsを置換
        self.template = self.template.format(stations='|'.join(stations))
 
    def get(self, kid=0, sid=0, title='', station=''):
        xbmc.sleep(1000)
        if kid > 0 and sid > 0:
            # デフォルト設定
            self.SET('kid', '0')
            self.SET('kstatus', 'true')  # 実行中
            self.SET('keyword', '')
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', '7')  # 毎日
            self.SET('station', '')  # 放送局を限定しない
        elif kid > 0:
            # キーワード設定変更
            sql = 'SELECT kid, kstatus, keyword, match, weekday, station FROM keywords WHERE kid = :kid'
            self.db.cursor.execute(sql, {'kid': kid})
            kid, kstatus, keyword, match, weekday, station = self.db.cursor.fetchone()
            self.SET('kid', str(kid))
            self.SET('kstatus', ['false','true'][kstatus])
            self.SET('keyword', keyword)
            self.SET('match', str(match))
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        elif sid > 0:
            weekday = datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('kstatus', 'true')  # 実行中
            self.SET('keyword', title)
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        else:
            weekday = datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('kstatus', 'true')  # 実行中
            self.SET('keyword', '')
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', '')

    def set(self):
        # 設定後の値
        keys = ('kid', 'kstatus', 'keyword', 'match', 'weekday', 'station')
        settings = dict([(key, self.GET(key)) for key in keys])
        # DB用に書き換える
        settings['kstatus'] = 1 if settings['kstatus'] == 'true' else 0
        # keywordテーブルに書き込む
        self.db.set_keyword(settings)
        # RSSインデクス再作成
        Contents().create_index()
        # 再描画
        xbmc.executebuiltin('Container.Refresh')

    def delete(self, kid):
        # キーワード情報取得
        sql = 'SELECT keyword, dirname FROM keywords WHERE kid = :kid'
        self.db.cursor.execute(sql, {'kid': kid})
        keyword, dirname = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno(self.STR(30529), self.STR(30530) % keyword)
        if ok:
            # ファイル削除
            download_path = os.path.join(self.CONTENTS_PATH, dirname)
            if os.path.exists(download_path):
                shutil.rmtree(download_path)
            # キーワード削除
            self.db.delete_keyword(kid)
            # RSSインデクス再作成
            Contents().create_index()
            # 再描画
            xbmc.executebuiltin('Container.Refresh')
