# -*- coding: utf-8 -*-

import sys
import os
import datetime
import requests
from xmltodict import parse

if __name__ == '__main__':
    sys.path.append('..')
    from prefdata import PrefData
    from common import Common
    class Const:
        TIMETABLE_ROOT = '.'
        TIMETABLE_PATH = 'timetable'
        SOURCE_PATH = 'source'
        JSON_PATH = 'json'
else:
    from ..prefdata import PrefData
    from .common import Common
    from ..common import Common as Const
    Const.SOURCE_PATH = os.path.join(Const.TIMETABLE_ROOT, 'source')
    Const.JSON_PATH = os.path.join(Const.TIMETABLE_ROOT, 'json')


class Scraper(Common, Const, PrefData):

    TYPE = 'radk'
    URL = 'http://radiko.jp/v2/api/program/now?area_id=%s'

    def __init__(self, pref):
        item = self.search_by_pref(pref)
        self.URL = self.URL % item['radiko']
        super().__init__()
    
    def parse(self, data):
        data = parse(data)
        buf = {}
        for s in data['radiko']['stations']['station']:
            name = self.normalize(s['name'])
            progs = []
            for p in s['scd']['progs']['prog']:
                progs.append({
                    'type': 'radk',
                    'name': name,
                    'title': self.normalize(p['title']),
                    'subtitle': self.normalize(p['sub_title']),
                    'START': p['@ft'],  # 20201027000000
                    'END': p['@to'],  # 20201027005300
                    'start': self.t2unixtime(p['@ft']),  # 20201027000000
                    'end': self.t2unixtime(p['@to']),  # 20201027005300
                    'act': self.normalize(p['pfm']),
                    'info': self.normalize(p['info']),
                    'desc': self.normalize(p['desc']),
                })
            buf[name] = progs
        return buf

    def t2unixtime(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
        # UNIX時間に変換
        return int(datetime_obj.timestamp())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--pref', default='東京都')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    countdown = Scraper(args.pref).update()
    print(countdown)
