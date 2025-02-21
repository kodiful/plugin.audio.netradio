# -*- coding: utf-8 -*-

import os
import sys
import json

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Stations(Common):

    KEYS = ('protocol', 'sid', 'top', 'schedule1', 'download1', 'station', 'description', 'direct', 'logo', 'site')

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db

    def open(self, sid=None):
        # アドオン設定画面から放送局設定画面を開いたとき、設定した値が以前の設定で書き換えられてしまうのを避ける
        xbmc.sleep(1000)
        # デフォルト設定
        self.SET('protocol', 'USER')
        self.SET('sid', '0')
        self.SET('top', 'true')
        self.SET('schedule1', 'false')
        self.SET('download1', 'false')
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
            self.SET('top', ['false','true'][sdata['top']])
            self.SET('schedule1', ['false','true'][sdata['schedule']])
            self.SET('download1', ['false','true'][sdata['download']])
            self.SET('station', sdata['station'])
            self.SET('description', sdata['description'])
            self.SET('direct', sdata['direct'])
            self.SET('logo', sdata['logo'])
            self.SET('site', sdata['site'])
        # 設定前の値
        before = dict([(key, self.GET(key)) for key in self.KEYS])
        # statusテーブルに書き込む
        sql = 'UPDATE status SET station = :before'
        self.db.cursor.execute(sql, {'before': json.dumps(before, ensure_ascii=False)})
        # 放送局設定画面のテンプレートを読み込む
        with open(os.path.join(self.DATA_PATH, 'settings', 'station.xml'), 'r', encoding='utf-8') as f:
            template = f.read()
        # テンプレートを書き換えて設定画面として書き出す
        with open(self.DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(template)
        # 放送局設定画面を開く
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    def save(self):
        # 設定後の値
        after = dict([(key, self.GET(key)) for key in self.KEYS])
        # 変更前の値を取得
        sid = int(after['sid'])
        if sid > 0:
            sql = 'SELECT * FROM stations WHERE sid = :sid'
            self.db.cursor.execute(sql, {'sid': sid})
            before = self.db.cursor.fetchone()
        # before/afterで変更可能なカラムを書き換える
        if after['protocol'] == 'USER':
            data = after
            data['top'] = 1 if after['top'] == 'true' else 0
            data.update({'key': ''})
        elif after['protocol'] in ('SJ', 'LR', 'SP'):
            data = dict(before)
            data['top'] = 1 if after['top'] == 'true' else 0
            data['schedule'] = 1 if after['schedule1'] == 'true' else 0
            data['download'] = 1 if after['download1'] == 'true' else 0
        else:  # NHK, RDK, SR
            data = dict(before)
            data['top'] = 1 if after['top'] == 'true' else 0
        # stationテーブルに書き込む
        self.db.set_station(data)
        # トップ画面に遷移して再描画
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    def delete(self, sid):
        # キーワード情報取得
        sql = 'SELECT station FROM stations WHERE sid = :sid'
        self.db.cursor.execute(sql, {'sid': sid})
        station, = self.db.cursor.fetchone()
        ok = xbmcgui.Dialog().yesno(self.STR(30154), self.STR(30155) % station)
        if ok:
            self.db.delete_station(sid)
            xbmc.executebuiltin('Container.Refresh')

