# -*- coding: utf-8 -*-

import sys
import os
import json

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

    TYPE = 'lsnr'
    URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=10005' # サイマルのみ
    #URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=99999' # 全ての局（リッスンラジオ公式や試験放送含む）

    def __init__(self):
        super().__init__()

    def parse(self, data):
        buf = []
        data = json.loads(data)
        for section in data['Channel']:
            '''
            {
                "ChannelId": 30120,
                "ChannelName": "Heart FM",
                "ChannelDetail": "愛知県名古屋市中区にあるインターネットラジオ局です。",
                "ChannelImage": "http://listenradio.jp/img/rslogo/30120s.png",
                "ChannelType": 2,
                "ChannelRtmp": "rtmp://mtist.as.smartstream.ne.jp/30120/livestream",
                "ChannelHls": "https://mtist.as.smartstream.ne.jp/30120/livestream/playlist.m3u8",
                "ChannelHds": "http://mtist.as.smartstream.ne.jp/30120/livestream/manifest.f4m",
                "AdFlg": true,
                "PublisherId": "a1502e22bc156c6",
                "SortNo": 29,
                "AreaId": 11,
                "ChannelLogo": "http://listenradio.jp/img/rslogo/30120r.png"
            }
            '''
            try:
                id_ = section['ChannelId']
                station = section['ChannelName']
                code, region, pref, city = self.infer_place(section['ChannelDetail'])
                logo = section['ChannelImage']
                stream = section['ChannelHls']
                description = section['ChannelDetail']
            except Exception:
                print('[lsnr] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            if region:
                buf.append({
                    'type': self.TYPE,
                    'id': str(id_),
                    'station': self.normalize(station),
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': self.normalize(description),
                    'official': '',
                    'stream': stream,
                })
            else:
                print('[lsnr] invalid region:', station, stream, sep='\t', file=sys.stderr)
        return buf


if __name__ == '__main__':
    scraper = Scraper()
    buf = scraper.run()
    scraper.save_as_list(buf)
    scraper.save_as_file(buf, category='コミュニティラジオ')
