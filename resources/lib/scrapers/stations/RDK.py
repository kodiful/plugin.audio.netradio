# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.scrapers.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'RDK'
    URL = 'http://radiko.jp/v2/station/list/%s.xml'

    def __init__(self, area):
        self.area = area
        self.URL = self.URL % area
        super().__init__(f'{self.PROTOCOL}/{area}')

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='xml').find_all('station')
        for section in sections:
            try:
                id = section.id.text
                station = section.find('name').text
                station = self.normalize(station)
                code, region, pref, _ = self.db.search_by_radiko(self.area)
                logo = section.find('logo', width='448').text
                site = section.href.text
            except Exception:
                print('[radiko] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            buf.append({
                'top': 0 if station.startswith('NHK') else 1,
                'vis': 1,
                'protocol': self.PROTOCOL,
                'key': id,
                'station': station,
                'code': code,
                'region': region,
                'pref': pref,
                'city': '',
                'logo': logo,
                'description': '',
                'site': site,
                'direct': '',
                'delay': 15
            })
        return buf


# https://radiko.jp/v2/station/list/JP13.xml

'''
<?xml version="1.0" encoding="UTF-8" ?>
<stations area_id="JP13" area_name="TOKYO JAPAN">
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
    <station>
        <id>QRR</id>
        <name>文化放送</name>
        <ascii_name>JOQR BUNKA HOSO</ascii_name>
        <href>http://www.joqr.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/QRR/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/QRR/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/QRR/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/QRR/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/QRR/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/QRR/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/QRR/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/QRR/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/QRR/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/QRR/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/QRR/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/QRR/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/QRR/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/QRR.xml</feed>
        <banner>http://radiko.jp/res/banner/QRR/20240423144553.png</banner>
    </station>
    <station>
        <id>LFR</id>
        <name>ニッポン放送</name>
        <ascii_name>JOLF NIPPON HOSO</ascii_name>
        <href>http://www.1242.com/</href>
        <logo_xsmall>http://radiko.jp/station/logo/LFR/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/LFR/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/LFR/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/LFR/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/LFR/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/LFR/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/LFR/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/LFR/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/LFR/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/LFR/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/LFR/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/LFR/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/LFR/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/LFR.xml</feed>
        <banner>http://radiko.jp/res/banner/LFR/20200423102824.jpg</banner>
    </station>
    <station>
        <id>RN1</id>
        <name>ラジオNIKKEI第1</name>
        <ascii_name>RADIONIKKEI</ascii_name>
        <href>http://www.radionikkei.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/RN1/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/RN1/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/RN1/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/RN1/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/RN1/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/RN1/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/RN1/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/RN1/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/RN1/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/RN1/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/RN1/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/RN1/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/RN1/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/RN1.xml</feed>
        <banner>http://radiko.jp/res/banner/RN1/20120802154152.png</banner>
    </station>
    <station>
        <id>RN2</id>
        <name>ラジオNIKKEI第2</name>
        <ascii_name>RADIONIKKEI2</ascii_name>
        <href>http://www.radionikkei.jp/ </href>
        <logo_xsmall>http://radiko.jp/station/logo/RN2/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/RN2/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/RN2/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/RN2/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/RN2/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/RN2/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/RN2/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/RN2/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/RN2/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/RN2/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/RN2/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/RN2/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/RN2/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/RN2.xml</feed>
        <banner>http://radiko.jp/res/banner/RN2/20190423111331.png</banner>
    </station>
    <station>
        <id>INT</id>
        <name>interfm</name>
        <ascii_name>InterFM897</ascii_name>
        <href>https://www.interfm.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/INT/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/INT/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/INT/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/INT/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/INT/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/INT/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/INT/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/INT/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/INT/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/INT/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/INT/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/INT/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/INT/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/INT.xml</feed>
        <banner>http://radiko.jp/res/banner/INT/20220401035523.jpg</banner>
    </station>
    <station>
        <id>FMT</id>
        <name>TOKYO FM</name>
        <ascii_name>TOKYO FM</ascii_name>
        <href>https://www.tfm.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/FMT/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/FMT/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/FMT/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/FMT/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/FMT/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/FMT/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/FMT/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/FMT/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/FMT/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/FMT/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/FMT/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/FMT/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/FMT/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/FMT.xml</feed>
        <banner>http://radiko.jp/res/banner/FMT/20220512162447.jpg</banner>
    </station>
    <station>
        <id>FMJ</id>
        <name>J-WAVE</name>
        <ascii_name>J-WAVE</ascii_name>
        <href>https://www.j-wave.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/FMJ/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/FMJ/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/FMJ/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/FMJ/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/FMJ/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/FMJ/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/FMJ/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/FMJ/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/FMJ/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/FMJ/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/FMJ/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/FMJ/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/FMJ/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/FMJ.xml</feed>
        <banner>http://radiko.jp/res/banner/FMJ/20250127100316.jpg</banner>
    </station>
    <station>
        <id>JORF</id>
        <name>ラジオ日本</name>
        <ascii_name>RF RADIO NIPPON</ascii_name>
        <href>http://www.jorf.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/JORF/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/JORF/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/JORF/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/JORF/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/JORF/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/JORF/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/JORF/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/JORF/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/JORF/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/JORF/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/JORF/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/JORF/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/JORF/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/JORF.xml</feed>
        <banner>http://radiko.jp/res/banner/JORF/20210226162543.png</banner>
    </station>
    <station>
        <id>BAYFM78</id>
        <name>BAYFM78</name>
        <ascii_name>bayfm78</ascii_name>
        <href>http://www.bayfm.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/BAYFM78/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/BAYFM78/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/BAYFM78/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/BAYFM78/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/BAYFM78/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/BAYFM78/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/BAYFM78/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/BAYFM78/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/BAYFM78/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/BAYFM78/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/BAYFM78/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/BAYFM78/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/BAYFM78/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/BAYFM78.xml</feed>
        <banner>http://radiko.jp/res/banner/BAYFM78/20240314013642.jpeg</banner>
    </station>
    <station>
        <id>NACK5</id>
        <name>NACK5</name>
        <ascii_name>NACK5</ascii_name>
        <href>https://www.nack5.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/NACK5/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/NACK5/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/NACK5/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/NACK5/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/NACK5/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/NACK5/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/NACK5/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/NACK5/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/NACK5/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/NACK5/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/NACK5/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/NACK5/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/NACK5/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/NACK5.xml</feed>
        <banner>http://radiko.jp/res/banner/NACK5/20160929170327.jpg</banner>
    </station>
    <station>
        <id>YFM</id>
        <name>ＦＭヨコハマ</name>
        <ascii_name>Fm yokohama 84.7</ascii_name>
        <href>https://www.fmyokohama.co.jp/</href>
        <logo_xsmall>http://radiko.jp/station/logo/YFM/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/YFM/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/YFM/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/YFM/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/YFM/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/YFM/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/YFM/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/YFM/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/YFM/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/YFM/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/YFM/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/YFM/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/YFM/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/YFM.xml</feed>
        <banner>http://radiko.jp/res/banner/YFM/20110922163525.png</banner>
    </station>
    <station>
        <id>IBS</id>
        <name>LuckyFM 茨城放送</name>
        <ascii_name>IBS RADIO</ascii_name>
        <href>https://www.ibs-radio.com/</href>
        <logo_xsmall>http://radiko.jp/station/logo/IBS/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/IBS/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/IBS/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/IBS/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/IBS/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/IBS/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/IBS/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/IBS/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/IBS/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/IBS/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/IBS/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/IBS/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/IBS/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/IBS.xml</feed>
        <banner>http://radiko.jp/res/banner/IBS/20241005145856.jpg</banner>
    </station>
    <station>
        <id>JOAK</id>
        <name>NHKラジオ第1（東京）</name>
        <ascii_name>JOAK</ascii_name>
        <href>https://www.nhk.or.jp/radio/</href>
        <logo_xsmall>http://radiko.jp/station/logo/JOAK/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/JOAK/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/JOAK/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/JOAK/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/JOAK/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/JOAK/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/JOAK/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/JOAK/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/JOAK/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/JOAK/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/JOAK/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/JOAK/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/JOAK/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/JOAK.xml</feed>
        <banner>http://radiko.jp/res/banner/JOAK/20170922183839.png</banner>
    </station>
    <station>
        <id>JOAK-FM</id>
        <name>NHK-FM（東京）</name>
        <ascii_name>JOAK-FM</ascii_name>
        <href>https://www.nhk.or.jp/radio/</href>
        <logo_xsmall>http://radiko.jp/station/logo/JOAK-FM/logo_xsmall.png</logo_xsmall>
        <logo_small>http://radiko.jp/station/logo/JOAK-FM/logo_small.png</logo_small>
        <logo_medium>http://radiko.jp/station/logo/JOAK-FM/logo_medium.png</logo_medium>
        <logo_large>http://radiko.jp/station/logo/JOAK-FM/logo_large.png</logo_large>
        <logo width="124" height="40">http://radiko.jp/v2/static/station/logo/JOAK-FM/124x40.png</logo>
        <logo width="344" height="80">http://radiko.jp/v2/static/station/logo/JOAK-FM/344x80.png</logo>
        <logo width="688" height="160">http://radiko.jp/v2/static/station/logo/JOAK-FM/688x160.png</logo>
        <logo width="172" height="40">http://radiko.jp/v2/static/station/logo/JOAK-FM/172x40.png</logo>
        <logo width="224" height="100">http://radiko.jp/v2/static/station/logo/JOAK-FM/224x100.png</logo>
        <logo width="448" height="200">http://radiko.jp/v2/static/station/logo/JOAK-FM/448x200.png</logo>
        <logo width="112" height="50">http://radiko.jp/v2/static/station/logo/JOAK-FM/112x50.png</logo>
        <logo width="168" height="75">http://radiko.jp/v2/static/station/logo/JOAK-FM/168x75.png</logo>
        <logo width="258" height="60">http://radiko.jp/v2/static/station/logo/JOAK-FM/258x60.png</logo>
        <feed>http://radiko.jp/station/feed/JOAK-FM.xml</feed>
        <banner>http://radiko.jp/res/banner/JOAK-FM/20170922184116.png</banner>
    </station>
</stations>
'''