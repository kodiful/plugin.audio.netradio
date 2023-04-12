# -*- coding: utf-8 -*-

import sys
import os
import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    sys.path.append('..')
    from prefdata import PrefData
    from common import Common
    class Const:
        DIRECTORY_ROOT = '.'
        DIRECTORY_PATH = 'directory'
        SOURCE_PATH = 'source'
        JSON_PATH = 'json'
else:
    from ..prefdata import PrefData
    from .common import Common
    from ..common import Common as Const
    Const.SOURCE_PATH = os.path.join(Const.DIRECTORY_ROOT, 'source')
    Const.JSON_PATH = os.path.join(Const.DIRECTORY_ROOT, 'json')


class Scraper(Common, Const, PrefData):

    TYPE = 'radk'
    URL = 'http://radiko.jp/v2/station/list/%s.xml'

    def __init__(self, area):
        self.area = area
        self.URL = self.URL % area
        super().__init__(f'{self.TYPE}_{area}')

    def load(self):
        res = requests.get(self.URL)
        data = res.content.decode('utf-8')
        return data

    def parse(self, data):
        buf = []
        stations = BeautifulSoup(data, features='xml').find_all('station')
        for station in stations:
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
                id = station.id.text
                name = station.find('name').text
                code, region, pref = self.radiko_place(self.area)
                logo = station.find('logo', width='448').text
                official = station.href.text
            except Exception:
                print('[radk] unparsable content:', name, sep='\t')
                continue
            buf.append({
                'type': self.TYPE,
                'id': id,
                'name': self.normalize(name),
                'code': code,
                'region': region,
                'pref': pref,
                'city': '',
                'logo': logo,
                'description': '',
                'official': official,
                'stream': ''
            })
        return buf


if __name__ == '__main__':
    buf = []
    for i in range(1, 48):
        scraper = Scraper(f'JP{i}')
        buf = buf + scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='民放ラジオ(radiko)')
