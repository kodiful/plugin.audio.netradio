# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'NHK'
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
        super().__init__(self.PROTOCOL)

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='xml').find_all('data')
        for section in sections:
            try:
                station = section.areajp.text
                code, region, pref, city = self.db.search_by_joined(self.AREA[section.areajp.text])
            except Exception:
                print('[nhk] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            buf.append({
                'protocol': self.PROTOCOL,
                'key': 'NHK1',
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
                'display': 1,
                'schedule': 1,
                'download': 1
            })
            buf.append({
                'protocol': self.PROTOCOL,
                'key': 'NHK2',
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
                'display': 1,
                'schedule': 1,
                'download': 1
            })
            buf.append({
                'protocol': self.PROTOCOL,
                'key': 'NHK3',
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
                'display': 1,
                'schedule': 1,
                'download': 1
            })
        return buf


# https://www.nhk.or.jp/radio/config/config_web.xml

'''
<?xml version="1.0" encoding="UTF-8"?>
<radiru_config>

	<!-- お知らせ -->
	<info><![CDATA[/radio/include/oshirase.txt]]></info>
	
	<!-- 各地域のストリームURL -->
	<stream_url>
		<data>
			<areajp>札幌</areajp>
			<area>sapporo</area>
			<apikey>700</apikey>
			<areakey>010</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023545/nhkradiruikr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023546/nhkradiruikfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>仙台</areajp>
			<area>sendai</area>
			<apikey>600</apikey>
			<areakey>040</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023543/nhkradiruhkr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023544/nhkradiruhkfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>東京</areajp>
			<area>tokyo</area>
			<apikey>001</apikey>
			<areakey>130</areakey>

			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023229/nhkradiruakr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023507/nhkradiruakfm/master.m3u8]]></fmhls>
		</data>
		<data>
			<areajp>名古屋</areajp>
			<area>nagoya</area>
			<apikey>300</apikey>
			<areakey>230</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023510/nhkradiruckr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023511/nhkradiruckfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>大阪</areajp>
			<area>osaka</area>
			<apikey>200</apikey>
			<areakey>270</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023508/nhkradirubkr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023509/nhkradirubkfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>広島</areajp>
			<area>hiroshima</area>
			<apikey>400</apikey>
			<areakey>340</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023512/nhkradirufkr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023513/nhkradirufkfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>松山</areajp>
			<area>matsuyama</area>
			<apikey>800</apikey>
			<areakey>380</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023547/nhkradiruzkr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023548/nhkradiruzkfm/master.m3u8]]></fmhls>
			
		</data>
		<data>
			<areajp>福岡</areajp>
			<area>fukuoka</area>
			<apikey>501</apikey>
			<areakey>400</areakey>
			
			<r1hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023541/nhkradirulkr1/master.m3u8]]></r1hls>
			<r2hls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8]]></r2hls>
			<fmhls><![CDATA[https://radio-stream.nhk.jp/hls/live/2023542/nhkradirulkfm/master.m3u8]]></fmhls>
			
		</data>
	</stream_url>
	
	<!-- noa api -->
	<url_program_noa><![CDATA[//api.nhk.or.jp/r5/pg2/now/4/{area}/netradio.json]]></url_program_noa>

	<!-- program detail api -->
	<url_program_day><![CDATA[//api.nhk.or.jp/r5/pg2/list/4/{area}/{service}/[YYYY-MM-DD].json]]></url_program_day>

	<!-- program info api -->
	<url_program_detail><![CDATA[//api.nhk.or.jp/r5/pg2/info/4/{area}/{service}/{dateid}.json]]></url_program_detail>

	<!-- tweet cgi @radiru -->
	<radiru_twitter_timeline><![CDATA[//cgi4.nhk.or.jp/tweet/api/tweet.cgi?twname=nhk_radiru]]></radiru_twitter_timeline>

</radiru_config>
'''