# -*- coding: utf-8 -*-

import sys
import os
import json
from bs4 import BeautifulSoup

if __name__ == '__main__':
    sys.path.append('..')
    from prefecture import Prefecture
    from common import Common
    class Const:
        DIRECTORY_ROOT = '.'
        DIRECTORY_PATH = 'directory'
        LOGO_PATH = 'logo'
        SOURCE_PATH = 'source'
        JSON_PATH = 'json'
else:
    from ..prefecture import Prefecture
    from .common import Common
    from ..common import Common as Const
    Const.SOURCE_PATH = os.path.join(Const.DIRECTORY_ROOT, 'source')
    Const.JSON_PATH = os.path.join(Const.DIRECTORY_ROOT, 'json')


class Scraper(Common, Const, Prefecture):

    TYPE = 'jcba'
    URL = 'http://www.jcbasimul.com'

    def __init__(self):
        super().__init__()

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
                    code, region, pref, city = self.infer_place(section['prefecture'] + section['description'])
                    logo = section['logoUrl']
                    description = section['description']
                    official = section['officialSiteUrl']
                except Exception:
                    print('[jcba] unparsable content:', station, sep='\t', file=sys.stderr)
                    continue
                buf.append({
                    'type': self.TYPE,
                    'id': str(id),
                    'station': self.normalize(station),
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': self.normalize(description),
                    'official': official,
                    'stream': ''
                })
        return buf


if __name__ == '__main__':
    scraper = Scraper()
    buf = scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='コミュニティラジオ')
