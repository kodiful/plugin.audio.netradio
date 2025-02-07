# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

    TYPE = 'radk'
    URL = 'http://radiko.jp/v2/station/list/%s.xml'

    def __init__(self, area):
        self.area = area
        self.URL = self.URL % area
        super().__init__(f'{self.TYPE}_{area}')

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='xml').find_all('station')
        for section in sections:
            '''
            <station>
                <id>TBS</id>
                <name>TBSラジオ</name>
                <ascii_name>TBS RADIO</ascii_name>
                <href>https://www.tbsradio.jp/</href>
                <logo_xsmall>http://radiko.jp/station/logo/TBS/logo_xsmall.png</logo_xsmall>
                <logo_small>http://radiko.jp/station/logo/TBS/logo_small.png</logo_small>
                <logo_medium>http://radiko.jp/station/logo/TBS/logo_medium.png</logo_medium>
                <logo_large>http://radiko.jp/station/logo/TBS/logo_large.png</logo_large>
                <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/TBS/124x40.png</logo>
                <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/TBS/344x80.png</logo>
                <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/TBS/688x160.png</logo>
                <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/TBS/172x40.png</logo>
                <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/TBS/224x100.png</logo>
                <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/TBS/448x200.png</logo>
                <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/TBS/112x50.png</logo>
                <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/TBS/168x75.png</logo>
                <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/TBS/258x60.png</logo>
                <feed>http://radiko.jp/station/feed/TBS.xml</feed>
                <banner>http://radiko.jp/res/banner/TBS/20200331114320.jpg</banner>
            </station>
            '''
            try:
                id = section.id.text
                station = section.find('name').text
                code, region, pref = self.db.radiko_place(self.area)
                logo = section.find('logo', width='448').text
                official = section.href.text
            except Exception:
                print('[radk] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            buf.append({
                'type': self.TYPE,
                'abbr': id,
                'station': self.normalize(station),
                'code': code,
                'region': region,
                'pref': pref,
                'city': '',
                'logo': logo,
                'description': '',
                'site': official,
                'direct': '',
                'match': 0 if self.normalize(station).startswith('NHK') else 1
            })
        return buf
