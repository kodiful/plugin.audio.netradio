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

    TYPE = 'csra'
    URL = 'http://csra.fm/stationlist/'

    def __init__(self):
        super().__init__()

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
                code, region, pref, city = self.infer_place(section.text.replace('久米島', '久米島町'))
                logo = 'http://csra.fm%s' % section.img['src'].strip()
                stream = section.find('a', class_='stm')['href'].strip()
                official =  section.find('a', class_='site')['href'].strip()
            except Exception:
                print('[csra] unparsable content:', station, sep='\t')
                continue
            # ストリーミングURLがListenRadioを参照している場合はスキップ
            if stream.startswith('http://listenradio.jp/'):
                continue
            # ストリーミングURLがmms://で始まるか.asxで終わるものを採用
            if stream.startswith('mms://') or stream.endswith('.asx'):
                buf.append({
                    'type': self.TYPE,
                    'id': '',
                    'station': self.normalize(station),
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': '',
                    'official': official,
                    'stream': stream,
                })
            else:
                print('[csra] unsupported protocol:', station, stream, sep='\t')
        return buf


if __name__ == '__main__':
    scraper = Scraper()
    buf = scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='コミュニティラジオ')
