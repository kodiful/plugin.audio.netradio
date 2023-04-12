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

    TYPE = 'siml'
    URL = 'http://www.simulradio.info/'

    def __init__(self):
        super().__init__()

    def load(self):
        res = requests.get(self.URL)
        data = res.content.decode('utf-8')
        return data

    def parse(self, data):
        buf = []
        divs = BeautifulSoup(data, features='lxml').find_all('div', class_='radiobox')
        for div in divs:
            '''
            <div class="radiobox">
                <table>
                    <tr valign="top">
                        <td>
                            <p>
                                <img src="data/1.jpg" width="90" height="60" class="left" />
                            </p>
                        </td>
                        <td width="90" align="center" valign="middle" style="font-size: x-small;">
                            <p>
                                <a href="http://listenradio.jp/?chp=30005&cap=10005&arp=1" target="_blank" onClick="javascript: pageTracker._trackPageview('http://listenradio.jp/?chp=30005&cap=10005&arp=1');" >
                                    <img src="images/btn_radio.jpg" alt="放送を聴く" width="70" height="32" border="0" />
                                </a><br />
                                音声 (24K)
                            </p>
                        </td>
                    </tr>
                    <tr valign="top">
                        <td colspan="2" valign="top">
                            <p style="clear:both;  margin-top: 0px;">
                                <strong><a href="http://www.sankakuyama.co.jp/" target="_blank">三角山放送局</a></strong><br />
                                札幌市西区
                            </p>
                            <p style="font-size: 70%; line-height: 140%; margin-top: 0px; clear: both;">
                                月-木 0:00-19:00/21:00-24:00<br />
                                金 0:00-20:00/21:00-24:00<br />
                                土 0:00-18:00/21:00-24:00<br />
                                日 0:00-6:00<br />
                                ※コンサドーレ札幌のアウェイ戦の中継を除く<br />
                                ※ネット休止時間<br />
                                毎週月曜日～金曜日の18時から19時<br />
                                毎週日曜日の8時～12時、20時～22時
                            </p>
                        </td>
                    </tr>
                </table>
            </div>            
            '''
            try:
                name = div.strong.a.text.strip()
                code, region, pref, city = self.infer_place(div.text.replace('久米島', '久米島町'))
                logo = 'http://www.simulradio.info/%s' % div.img['src'].strip()
                stream = div.a['href'].strip()
                official = div.strong.a['href'].strip()
            except Exception:
                print('[siml] unparsable content:', name, sep='\t')
                continue
            # ストリーミングURLがListenRadioを参照している場合はスキップ
            if stream.startswith('http://listenradio.jp/'):
                continue
            # ストリーミングURLがmms://で始まるか.asxで終わるものを採用
            if stream.startswith('mms://') or stream.endswith('.asx'):
                buf.append({
                    'type': self.TYPE,
                    'id': '',
                    'name': self.normalize(name),
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
                print('[siml] unsupported protocol:', name, stream, sep='\t')
        return buf


if __name__ == '__main__':
    scraper = Scraper()
    buf = scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='コミュニティラジオ')
