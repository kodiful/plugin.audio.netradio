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
        # 表示中の放送局リストを取得
        sql = '''SELECT s.station
        FROM status JOIN json_each(status.front) AS je ON je.value = s.sid JOIN stations AS s ON je.value = s.sid'''
        self.db.cursor.execute(sql)
        self.stations = [self.STR(30529)] + [station for station, in self.db.cursor.fetchall()]

    def prep(self):
        # テンプレート
        with open(os.path.join(self.SETTINGS_PATH, 'modules', 'timer.xml')) as f:
            self.template = f.read()
        # テンプレートのstationsを置換
        self.template = self.template.format(stations='|'.join(self.stations))
 
    def get(self, station, title, start, end):
        xbmc.sleep(1000)
        # 時刻
        if start:
            if start < self.now():
                start = datetime.now()
            else:
                start = self.datetime(start)
        else:
            start = datetime.now()
        if end:
            end = self.datetime(end)
        else:
            end = datetime.now() + timedelta(minutes=self.DURATION)
        # デフォルト設定
        self.SET('title', title or station)
        self.SET('date0', start.strftime('%Y-%m-%d'))
        self.SET('time0', start.strftime('%H:%M'))
        self.SET('date1', end.strftime('%Y-%m-%d'))
        self.SET('time1', end.strftime('%H:%M'))
        self.SET('station', station or self.stations[0])

    def set(self):
        # 設定後の値
        keys = ('title', 'date0', 'time0', 'date1', 'time1', 'station')
        settings = dict([(key, self.GET(key)) for key in keys])
        # 仮想番組データ
        station = settings['station']
        title = settings['title']
        sql = 'SELECT protocol, key, region, pref, description, site FROM stations WHERE vis = 1 AND station = :station'
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
        # !!!ここでデータのバリデーション
        # 仮想番組としてcontentsテーブルに書き込む
        result = self.db.add(data, kid=-1)
        if result == 0:
            # 既存の予約と(sid, start, kid)が競合する場合は通知
            self.notify('Conflicting with other settings')