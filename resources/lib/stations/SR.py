# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'SR'
    URL = 'http://csra.fm/stationlist/'

    def __init__(self):
        super().__init__(self.PROTOCOL)

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='lxml').find_all('section')
        for section in sections:
            '''
            <section>
                <a href="/blog/author/765fm/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMアップルの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                    <div>
                        <div class="stationlogo"><img src="/logo/765fm.png" alt="FMアップル"></div>
                        <h1>FMアップル</h1>
                        <p>札幌市豊平区</p>
                        <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMアップルの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                    </div>
                </a>
                <div class="stationlink">
                    <a href="http://765fm.com/" target="_blank" class="site">ホームページ</a>
                    <a href="http://listenradio.jp/?chp=30090&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                </div>
            </section>
            '''
            try:
                if section.h1:
                    station = section.h1.string.strip()
                    station = self.normalize(station)
                    # 閉局しているものはスキップ
                    if section.prettify().find('閉局') > -1:
                        print('[SR] closed (skip):', station, file=sys.stderr)
                        continue
                    # listenradio.jpを参照しているものはスキップ
                    direct = section.find('a', class_='stm')['href'].strip()
                    if direct.startswith('http://listenradio.jp/'):
                        #print('[SR] listenradio protocol (skip):', station, file=sys.stderr)
                        continue
                    # ストリーミングURLがmms://で始まるか.asxで終わるものを採用
                    if direct.startswith('mms://') is False and direct.endswith('.asx') is False:
                        print('[SR] unsupported protocol (skip):', station, direct, file=sys.stderr)
                        continue
                    results = self.db.search_by_station(self.PROTOCOL, station)
                    if results:
                        code, region, pref, city, station, status = results
                        if status:
                            logo = 'http://csra.fm%s' % section.img['src'].strip()
                            site = section.find('a', class_='site')['href'].strip()
                        else:
                            continue  # 最優先のみ採用する
                    else:
                        print('[SR] not found in master (skip):', station, file=sys.stderr)
                        continue
                else:
                    continue
            except Exception:
                print('[SR] unparsable content (skip):', station, file=sys.stderr)
                continue
            buf.append({
                'protocol': self.PROTOCOL,
                'key': '',
                'station': station,
                'code': code,
                'region': region,
                'pref': pref,
                'city': city,
                'logo': logo,
                'description': '',
                'site': site,
                'direct': direct,
                'delay': 0,
                'sstatus': 0
            })
        return buf
