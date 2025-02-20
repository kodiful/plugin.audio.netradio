# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from resources.lib.db import ThreadLocal
from resources.lib.contents import Contents
from resources.lib.settings.common import Common

import xbmc


class Timer(Common):
    
    DURATION = 5

    def __init__(self):
        super().__init__()

    def prep(self):
        # トップ画面の放送局リストを取得
        self.db.cursor.execute('SELECT station FROM stations WHERE download = 1 OR top = 1 ORDER BY sid')
        stations = [station for station, in self.db.cursor.fetchall()]
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'timer.xml')) as f:
            self.template = f.read()
        # テンプレートのstationsを置換
        self.template = self.template.format(stations='|'.join(stations))
 
    def get(self, station):
        xbmc.sleep(1000)
        # 現在時刻
        start = datetime.now()
        end = datetime.now() + timedelta(minutes=self.DURATION)
        # デフォルト設定
        self.SET('date0', start.strftime('%Y-%m-%d'))
        self.SET('time0', start.strftime('%H:%M'))
        self.SET('date1', end.strftime('%Y-%m-%d'))
        self.SET('time1', end.strftime('%H:%M'))
        self.SET('station', station)

    def set(self):
        # 設定後の値
        keys = ('date0', 'time0', 'date1', 'time1', 'station')
        settings = dict([(key, self.GET(key)) for key in keys])
        # 仮想番組データ
        station = settings['station']
        title = station
        sql = 'SELECT protocol, key, region, pref, description, site FROM stations WHERE station = :station'
        self.db.cursor.execute(sql, {'station': station})
        protocol, key, region, pref, description, site = self.db.cursor.fetchone()
        start = f"{settings['date0']} {settings['time0']}:00"
        end = f"{settings['date1']} {settings['time1']}:00"
        data = {
            'station': station,
            'protocol': protocol,
            'key': key,
            'title': title,
            'start': start,
            'end': end,
            'act': '',
            'info': '',
            'desc': description,
            'site': site,
            'region': region,
            'pref': pref
        }
        # 仮想番組としてcontentsテーブルに書き込む
        self.db.add(data, kid=-1)
        # RSSインデクス再作成
        Contents().create_index()
        # 再描画
        xbmc.executebuiltin('Container.Refresh')
