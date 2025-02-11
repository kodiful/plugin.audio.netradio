# -*- coding: utf-8 -*-

import sys
import json
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'SJ'
    URL = 'http://www.jcbasimul.com'

    def __init__(self):
        super().__init__(self.PROTOCOL)

    def parse(self, data):
        buf = []
        data = BeautifulSoup(data, features='lxml').find('script', id='__NEXT_DATA__')
        data = json.loads(data.decode_contents())
        for sections in data['props']['pageProps']['stations']:
            for section in sections['list']:
                '''
                {
                    "id": "fmhana",
                    "googleTrackingId": "UA-31017506-54",
                    "name": "ＦＭはな",
                    "region": "北海道",
                    "prefecture": "北海道",
                    "sortOrder": 101,
                    "latitude": 43.55118924098481,
                    "longitude": 144.97850221398156,
                    "logoUrl": "https://radimo.s3.amazonaws.com/logo/7a004aebb67bb29f01708fdd34c7ed065754e7b7eda76e63cc6f51b1c000a94d.png",
                    "browserPlayer": true,
                    "description": "宇宙から見える格子状防風林の中心空とみどりの交流拠点中標津町から繋がる、ひろがる地域情報を発信中",
                    "officialSiteUrl": "http://fmhana.jp/"
                }
                '''
                try:
                    id = section['id']
                    station = section['name']
                    station = self.normalize(station)
                    results = self.db.search_by_station(self.PROTOCOL, station)
                    if results:
                        code, region, pref, city, station, status = results
                        if status:
                            logo = section['logoUrl']
                            description = section['description']
                            site = section['officialSiteUrl']
                        else:
                            continue  # 最優先のみ採用する
                    else:
                        print('[SJ] not found in master (skip):', station, file=sys.stderr)
                        continue
                except Exception:
                    print('[SJ] unparsable content (skip):', station, file=sys.stderr)
                    continue
                buf.append({
                    'protocol': self.PROTOCOL,
                    'key': id,
                    'station': station,
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': self.normalize(description),
                    'site': site,
                    'direct': '',
                    'delay': 0,
                    'sstatus': 1
                })
        return buf
