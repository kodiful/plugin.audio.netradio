# -*- coding: utf-8 -*-

import os
import shutil
import datetime
import json

from resources.lib.common import Common
from resources.lib.db import DB

import xbmc
import xbmcgui


class Keyword(Common):
    
    def __init__(self):
        # DBに接続
        self.db = DB()

    def __del__(self):
        # DBから切断
        self.db.conn.close()
 
    def set(self, kid, sid):
        xbmc.sleep(1000)
        if kid is None and sid is None:
            # デフォルト設定
            self.SET('kid', '0')
            self.SET('status', '0')  # 停止中
            self.SET('keyword', '')
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', '7')  # 毎日
            self.SET('station', '')  # 放送局を限定しない
        elif kid is not None:
            # キーワード設定変更
            sql = 'SELECT kid, status, keyword, match, weekday, station FROM keywords WHERE kid = :kid'
            self.db.cursor.execute(sql, {'kid': kid})
            kid, status, keyword, match, weekday, station = self.db.cursor.fetchone()
            self.SET('kid', str(kid))
            self.SET('status', status)
            self.SET('keyword', keyword)
            self.SET('match', match)
            self.SET('weekday', weekday)
            self.SET('station', station)
        elif sid is not None:
            # 番組情報からキーワード設定
            sql = 'SELECT title, station FROM contents WHERE sid = :sid AND end > NOW() ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': sid})
            data = [(title, station) for title, station in self.db.cursor.fetchall()]
            # 選択ダイアログを表示
            index = xbmcgui.Dialog().select('番組情報選択', [title for title, _ in data])
            if index == -1:
                return
            title, station = data[index]
            weekday = datetime.datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('status', '0')  # 停止中
            self.SET('keyword', title)
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        # 設定前の値
        before = dict([(key, self.GET(key)) for key in ('kid', 'status', 'keyword', 'match', 'weekday', 'station')])
        # statusテーブルに書き込む
        sql = 'UPDATE status SET keyword = :before'
        self.db.cursor.execute(sql, {'before': json.dumps(before)})
        # キーワード設定画面を開く
        shutil.copy(os.path.join(self.LIB_PATH, 'settings', 'keyword.xml'), self.DIALOG_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
    def add(self):
        # 設定後の値
        after = dict([(key, self.GET(key)) for key in ('kid', 'status', 'keyword', 'match', 'weekday', 'station')])
        # keywordテーブルに書き込む
        self.db.add_keyword(after)
        xbmc.executebuiltin('Container.Refresh')

    def delete(self, kid):
        # キーワード情報取得
        sql = 'SELECT keyword, dirname FROM keywords WHERE kid = :kid'
        self.db.cursor.execute(sql, {'kid': kid})
        keyword, dirname = self.db.cursor.fetchone()
        # 確認ダイアログを表示
        ok = xbmcgui.Dialog().yesno('削除確認', f'"{keyword}" のダウンロード済みファイルを含めて削除しますか？')
        if ok:
            # ファイル削除
            download_path = os.path.join(self.CONTENTS_PATH, dirname)
            if os.path.exists(download_path):
                shutil.rmtree(download_path)
            # キーワード削除
            self.db.delete_keyword(kid)
            xbmc.executebuiltin('Container.Refresh')


