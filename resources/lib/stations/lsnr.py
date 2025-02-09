# -*- coding: utf-8 -*-

import sys
import json

from resources.lib.stations.common import Common


class Scraper(Common):

    TYPE = 'lsnr'
    URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=10005' # サイマルのみ
    #URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=99999' # 全ての局（リッスンラジオ公式や試験放送含む）

    def __init__(self):
        super().__init__(self.TYPE)

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
                id = section['ChannelId']
                station = section['ChannelName']
                code, region, pref, city = self.db.infer_place('\n'.join[station, section['ChannelDetail']])
                logo = section['ChannelImage']
                stream = section['ChannelHls']
                description = section['ChannelDetail']
            except Exception:
                print('[lsnr] unparsable content (skip):', station, sep='\t', file=sys.stderr)
                continue
            if region:
                buf.append({
                    'type': self.TYPE,
                    'abbr': str(id),
                    'station': self.normalize(station),
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': self.normalize(description),
                    'site': '',
                    'direct': stream,
                    'delay': 0,
                    'sstatus': 0
                })
            else:
                print('[lsnr] invalid region:', station, stream, sep='\t', file=sys.stderr)
        return buf
