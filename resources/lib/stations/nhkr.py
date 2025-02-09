# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

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
                code, region, pref, city = self.db.infer_place(self.AREA[section.areajp.text])
            except Exception:
                print('[nhkr] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            buf.append({
                'type': 'nhkr',
                'abbr': 'NHK1',
                'station': f'NHKラジオ第1({station})',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['r1'],
                'description': '',
                'site': 'https://www.nhk.or.jp/radio/',
                'direct': section.r1hls.text,
                'delay': 35,
                'sstatus': 1
            })
            buf.append({
                'type': 'nhkr',
                'abbr': 'NHK2',
                'station': f'NHKラジオ第2',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['r2'],
                'description': '',
                'site': 'https://www.nhk.or.jp/radio/',
                'direct': section.r2hls.text,
                'delay': 35,
                'sstatus': 1
            })
            buf.append({
                'type': 'nhkr',
                'abbr': 'NHK3',
                'station': f'NHK-FM({station})',
                'code': code,
                'region': region,
                'pref': '',  # ディレクトリに都道府県の階層を作成しない
                'city': city,
                'logo': self.LOGO['fm'],
                'description': '',
                'site': 'https://www.nhk.or.jp/radio/',
                'direct': section.fmhls.text,
                'delay': 35,
                'sstatus': 1
            })
        return buf
