# -*- coding: utf-8 -*-

import os
import shutil

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Stations(Common):

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db

    def get(self, sid=None):
        # アドオン設定画面から放送局設定画面を開いたとき、設定した値が以前の設定で書き換えられてしまうのを避ける
        xbmc.sleep(1000)
        # デフォルト設定
        self.SET('protocol', 'USER')
        self.SET('sid', '0')
        self.SET('station', '')
        self.SET('description', '')
        self.SET('direct', '')
        self.SET('logo', '')
        self.SET('site', '')
        if sid:
            # 放送局設定変更
            sql = 'SELECT * FROM stations WHERE sid = :sid'
            self.db.cursor.execute(sql, {'sid': sid})
            sdata = self.db.cursor.fetchone()
            self.SET('protocol', sdata['protocol'])
            self.SET('sid', str(sid))
            self.SET('station', sdata['station'])
            self.SET('description', sdata['description'])
            self.SET('direct', sdata['direct'])
            self.SET('logo', sdata['logo'])
            self.SET('site', sdata['site'])
        # 放送局設定画面のテンプレートを読み込む
        with open(os.path.join(self.DATA_PATH, 'settings', 'station.xml'), 'r', encoding='utf-8') as f:
            template = f.read()
        # 設定画面として書き出す
        with open(self.DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(template)
        # 設定画面を開く
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % self.ADDON_ID)
        # 1秒待って設定画面をデフォルトに戻す
        xbmc.sleep(1000)
        shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'default.xml'), self.DIALOG_FILE)

    def set(self):
        # 設定後の値
        settings = dict([(key, self.GET(key)) for key in ('protocol', 'sid', 'station', 'description', 'direct', 'logo', 'site')])
        if settings['protocol'] == 'USER':
            # 不足している値を補完
            settings.update({'key': ''})
            # !!!ここでデータのバリデーション
            # stationテーブルに書き込む
            self.db.add_station(settings, top=1, vis=1)
            # トップ画面に遷移して再描画
            self.refresh(True)  # 放送局を新規作成したのでトップ画面へ

    def delete(self, sid):
        # 放送局情報取得
        sql = 'SELECT protocol, station FROM stations WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        protocol, station = self.db.cursor.fetchone()
        ok = xbmcgui.Dialog().yesno(self.STR(30154), self.STR(30155) % station)
        if ok:
            # ファイル検索
            sql = '''SELECT DISTINCT k.dirname
            FROM contents AS c
            JOIN keywords AS k ON c.kid = k.kid
            WHERE c.sid = :sid'''
            self.db.cursor.execute(sql, {'sid': sid})
            # ファイル削除
            for dirname, in self.db.cursor.fetchall():
                download_path = os.path.join(self.CONTENTS_PATH, dirname, protocol, station)
                if os.path.exists(download_path):
                    shutil.rmtree(download_path)
            # 放送局削除
            self.db.delete_station(sid)
            # 再描画
            self.refresh()
