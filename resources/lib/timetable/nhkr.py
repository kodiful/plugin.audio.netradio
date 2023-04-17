# -*- coding: utf-8 -*-

import sys
import os
import json
import datetime
import requests

if __name__ == '__main__':
    sys.path.append('..')
    from prefecture import Prefecture
    from common import Common
    class Const:
        TIMETABLE_ROOT = '.'
        TIMETABLE_PATH = 'timetable'
        SOURCE_PATH = 'source'
        JSON_PATH = 'json'
else:
    from ..prefecture import Prefecture
    from .common import Common
    from ..common import Common as Const
    Const.SOURCE_PATH = os.path.join(Const.TIMETABLE_ROOT, 'source')
    Const.JSON_PATH = os.path.join(Const.TIMETABLE_ROOT, 'json')


class Scraper(Common, Const, Prefecture):

    TYPE = 'nhkr'
    URL = 'https://api.nhk.or.jp/r5/pg2/now/4/%s/netradio.json'

    # 地域
    REGION = {
        '北海道': '010',
        '東北': '040',
        '関東': '130',
        '東海': '230',
        '近畿': '270',
        '中国': '340',
        '四国': '380',
        '九州沖縄': '400',
    }

    def __init__(self, region):
        self.URL = self.URL % self.REGION[region]
        super().__init__()

    def parse(self, data):
        data = json.loads(data)
        data = data['nowonair_list']
        station = data['n1']['following']['area']['name']
        buf1 = self.setup1(data['n1'], 'nhk1', f'NHKラジオ第1({station})')
        buf2 = self.setup1(data['n2'], 'nhk2', f'NHKラジオ第2')
        buf3 = self.setup1(data['n3'], 'nhk3', f'NHK-FM({station})')
        return {
            f'NHKラジオ第1({station})': buf1,
            f'NHKラジオ第2': buf2,
            f'NHK-FM({station})': buf3,
        }

    def setup1(self, data, type_, station):
        return [
            #self.setup2(data['previous'], type_, station),
            self.setup2(data['present'], type_, station),
            self.setup2(data['following'], type_, station),
        ]

    def setup2(self, data, type_, station):
        '''
        "title": "英会話タイムトライアル「１０月ＤＡＹ１８」",
        "subtitle": "【講師】ＢＢＴ大学教授…スティーブ・ソレイシィ，【出演】ジェニー・スキッドモア",
        "start_time": "2020-10-28T08:30:00+09:00",
        "end_time": "2020-10-28T08:40:00+09:00",
        "act": "【講師】ＢＢＴ大学　教授…スティーブ・ソレイシィ，【出演】ジェニー・スキッドモア",
        '''
        return {
            'type': type_,
            'station': station,
            'title': self.normalize(data['title']),
            'subtitle': self.normalize(data['subtitle']),
            'START': self.t2string(data['start_time']),  # 2020-10-28T08:55:00+09:00
            'END': self.t2string(data['end_time']),  # 2020-10-28T09:00:00+09:00
            'start': self.t2unixtime(data['start_time']),  # 2020-10-28T08:55:00+09:00
            'end': self.t2unixtime(data['end_time']),  # 2020-10-28T09:00:00+09:00
            'weekday': self.t2weekday(data['start_time']),
            'act': self.normalize(data['act']),
            'info': '',
            'desc': '',
        }
    
    def t2unixtime(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # UNIX時間に変換
        return int(datetime_obj.timestamp())

    def t2weekday(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # 曜日の数字に変換
        return str(datetime_obj.weekday())

    def t2string(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # 文字列に変換
        return datetime_obj.strftime('%Y%m%d%H%M%S')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='関東')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    countdown = Scraper(args.region).update(force=args.force)
    print(countdown)
