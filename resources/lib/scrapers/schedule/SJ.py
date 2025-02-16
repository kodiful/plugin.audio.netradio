# -*- coding: utf-8 -*-

import json
from datetime import datetime, timezone, timedelta

from resources.lib.scrapers.schedule.common import Common


class Scraper(Common):

    PROTOCOL = 'SJ'
    URL = 'https://www.jcbasimul.com/api/timetable/current/%s'

    def __init__(self, sid):
        super().__init__(f'{self.PROTOCOL}/{sid}')
        self.sid = sid
        self.db.cursor.execute('SELECT station, key, region, pref, site FROM stations WHERE sid = :sid', {'sid': sid})
        self.station, self.key, self.region, self.pref, self.site = self.db.cursor.fetchone()
        self.URL = self.URL % self.key

    def parse(self, data):
        data = json.loads(data)
        # 番組情報をリスト化
        buf = []
        for item in data.values():
            prog = {
                'station': self.station,
                'protocol': self.PROTOCOL,
                'key': self.key,
                'title': self.normalize(item['title']),
                'start': self._datetime(item['air_start']),
                'end': self._datetime(item['air_end']),
                'act': item.get('performer', ''),
                'info': '',
                'desc': '',
                'site': self.site,
                'region': self.region,
                'pref': self.pref
            }
            buf.append(prog)
        return buf

    def _datetime(self, t):
        # 2025-02-10T21:30:00Z -> 2025-02-11 06:30:00
        #utc_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")  # UTCの時刻をパース
        year, month, day, h, m, s = map(int, [t[0:4], t[5:7], t[8:10], t[11:13], t[14:16], t[17:19]])
        utc_time = datetime(year, month, day, h, m, s)
        utc_time = utc_time.replace(tzinfo=timezone.utc)  # UTCのタイムゾーンを設定
        jst_time = utc_time.astimezone(timezone(timedelta(hours=9)))  # 日本時間（JST: UTC+9）に変換
        return jst_time.strftime("%Y-%m-%d %H:%M:%S")  # JSTの時刻を出力


# https://www.jcbasimul.com/api/timetable/current/radioniseko

'''
{
    "current": {
        "title": "Morning Community",
        "air_start": "2025-02-10T21:30:00Z",
        "air_end": "2025-02-10T21:55:00Z",
        "performer": "橘 しんご"
    },
    "next": {
        "title": "Weekly Recommend",
        "air_start": "2025-02-10T21:55:00Z",
        "air_end": "2025-02-10T22:00:00Z"
    }
}
'''