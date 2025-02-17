# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
from datetime import datetime
from resources.lib.common import Common
from resources.lib.db import ThreadLocal

import xbmc
import xbmcgui


class Keywords(Common):
    
    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
 
    def set(self, kid, sid):
        xbmc.sleep(1000)
        if kid is None and sid is None:
            # デフォルト設定
            self.SET('kid', '0')
            self.SET('kstatus', '0')  # 停止中
            self.SET('keyword', '')
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', '7')  # 毎日
            self.SET('station', '')  # 放送局を限定しない
        elif kid is not None:
            # キーワード設定変更
            sql = 'SELECT kid, kstatus, keyword, match, weekday, station FROM keywords WHERE kid = :kid'
            self.db.cursor.execute(sql, {'kid': kid})
            kid, kstatus, keyword, match, weekday, station = self.db.cursor.fetchone()
            self.SET('kid', str(kid))
            self.SET('kstatus', str(kstatus))
            self.SET('keyword', keyword)
            self.SET('match', str(match))
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        elif sid is not None:
            # 番組情報からキーワード設定
            sql = 'SELECT title, station FROM contents WHERE sid = :sid AND end > NOW() ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': sid})
            choices = [(title, station) for title, station in self.db.cursor.fetchall()]
            # 選択ダイアログを表示
            index = xbmcgui.Dialog().select(self.STR(30528), [title for title, _ in choices])
            if index == -1:
                return
            title, station = choices[index]
            weekday = datetime.today().weekday()  # 今日の曜日を月(0)-日(6)で返す
            self.SET('kid', '0')
            self.SET('kstatus', '0')  # 停止中
            self.SET('keyword', title)
            self.SET('match', '0')  # 番組名のみ
            self.SET('weekday', str(weekday))
            self.SET('station', station)
        # 設定前の値
        before = dict([(key, self.GET(key)) for key in ('kid', 'kstatus', 'keyword', 'match', 'weekday', 'station')])
        # statusテーブルに書き込む
        sql = 'UPDATE status SET keyword = :before'
        self.db.cursor.execute(sql, {'before': json.dumps(before)})
        # キーワード設定画面のテンプレートを読み込む
        with open(os.path.join(self.DATA_PATH, 'settings', 'keyword.xml'), 'r', encoding='utf-8') as f:
            template = f.read()
        # ダウンロード可能な放送局リストを取得
        self.db.cursor.execute('SELECT station FROM stations WHERE download = 1 ORDER BY sid')
        stations = [''] + [station for station, in self.db.cursor.fetchall()]
        # テンプレートを書き換えて設定画面として書き出す
        with open(self.DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(template.format(stations='|'.join(stations)))
        # キーワード設定画面を開く
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    def add(self):
        # 設定後の値
        after = dict([(key, self.GET(key)) for key in ('kid', 'kstatus', 'keyword', 'match', 'weekday', 'station')])
        # keywordテーブルに書き込む
        self.db.add_keyword(after)
        # トップ画面に遷移して再描画
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

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
            xbmc.executebuiltin('Container.Refresh')
