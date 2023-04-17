# -*- coding: utf-8 -*-

import sys
import os
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

    TYPE = 'nhkr'
    URL = 'https://www.nhk.or.jp/radio/config/config_web.xml'

    # 地域
    AREA = {
        '東京': '東京都渋谷区',
        '札幌': '北海道札幌市',
        '仙台': '宮城県仙台市',
        '名古屋': '愛知県名古屋市',
        '大阪': '大阪府大阪市',
        '広島': '広島県広島市',
        '松山': '愛媛県松山市',
        '福岡': '福岡県福岡市',
    }

    # ロゴ
    LOGO = {
        'r1': 'https://www.nhk.or.jp/common/img/media/r1-200x200.png',
        'r2': 'https://www.nhk.or.jp/common/img/media/r2-200x200.png',
        'fm': 'https://www.nhk.or.jp/common/img/media/fm-200x200.png',
    }

    def __init__(self):
        super().__init__()

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='xml').find_all('data')
        for section in sections:
            '''
            <data>
                <areajp>札幌</areajp>
                <area>sapporo</area>
                <apikey>700</apikey>
                <areakey>010</areakey>
                <r1hls><![CDATA[https://nhkradioikr1-i.akamaihd.net/hls/live/512098/1-r1/1-r1-01.m3u8]]></r1hls>
                <r2hls><![CDATA[https://nhkradioakr2-i.akamaihd.net/hls/live/511929/1-r2/1-r2-01.m3u8]]></r2hls>
                <fmhls><![CDATA[https://nhkradioikfm-i.akamaihd.net/hls/live/512100/1-fm/1-fm-01.m3u8]]></fmhls>
            </data>
            '''
            try:
                station = section.areajp.text
                code, region, pref, city = self.infer_place(self.AREA[section.areajp.text])
            except Exception:
                print('[nhkr] unparsable content:', station, sep='\t')
                continue
            buf.append({
                'type': 'nhk1',
                'id': '',
                'station': f'NHKラジオ第1({station})',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['r1'],
                'description': '',
                'official': 'https://www.nhk.or.jp/radio/',
                'stream': section.r1hls.text
            })
            buf.append({
                'type': 'nhk2',
                'id': '',
                'station': f'NHKラジオ第2',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['r2'],
                'description': '',
                'official': 'https://www.nhk.or.jp/radio/',
                'stream': section.r2hls.text
            })
            buf.append({
                'type': 'nhk3',
                'id': '',
                'station': f'NHK-FM({station})',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['fm'],
                'description': '',
                'official': 'https://www.nhk.or.jp/radio/',
                'stream': section.fmhls.text
            })
        return buf


if __name__ == '__main__':
    scraper = Scraper()
    buf = scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='NHKラジオ')
