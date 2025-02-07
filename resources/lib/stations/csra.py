# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common
from resources.lib.db import DB, ThreadLocal


class Scraper(Common):

    TYPE = 'csra'
    URL = 'http://csra.fm/stationlist/'

    def __init__(self):
        super().__init__()
        # DBインスタンスを共有
        self.db = ThreadLocal.db = getattr(ThreadLocal, 'db', DB())

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
                station = section.h1.string.strip()
                code, region, pref, city = self.db.infer_place(section.text.replace('久米島', '久米島町'))
                logo = 'http://csra.fm%s' % section.img['src'].strip()
                stream = section.find('a', class_='stm')['href'].strip()
                official = section.find('a', class_='site')['href'].strip()
            except Exception:
                print('[csra] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            # ストリーミングURLがListenRadioを参照している場合はスキップ
            if stream.startswith('http://listenradio.jp/'):
                print('[csra] listenradio protocol (skip):', station, sep='\t', file=sys.stderr)
                continue
            # ストリーミングURLがmms://で始まるか.asxで終わるものを採用
            if stream.startswith('mms://') or stream.endswith('.asx'):
                buf.append({
                    'type': self.TYPE,
                    'abbr': '',
                    'station': self.normalize(station),
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': '',
                    'site': official,
                    'direct': stream,
                    'match': 0
                })
            else:
                print('[csra] unsupported protocol (skip):', station, stream, sep='\t', file=sys.stderr)
        return buf
