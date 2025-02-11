# -*- coding: utf-8 -*-

import sys
import json

from resources.lib.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'LR'
    URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=10005' # サイマルのみ
    #URL = 'http://listenradio.jp/service/categorychannel.aspx?categoryid=99999' # 全ての局（リッスンラジオ公式や試験放送含む）

    def __init__(self):
        super().__init__(self.PROTOCOL)

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
                station = self.normalize(station)
                results = self.db.search_by_station(self.PROTOCOL, station)
                if results:
                    code, region, pref, city, station, status = results
                    if status:
                        logo = section['ChannelLogo']
                        direct = section['ChannelHls']
                        description = section['ChannelDetail']
                    else:  # 最優先のみ採用する
                        continue
                else:
                    print('[LR] not found in master (skip):', station, file=sys.stderr)
                    continue
            except Exception:
                print('[LR] unparsable content (skip):', station, file=sys.stderr)
                continue
            if region:
                buf.append({
                    'protocol': self.PROTOCOL,
                    'key': id,
                    'station': station,
                    'code': code,
                    'region': region,
                    'pref': pref,
                    'city': city,
                    'logo': logo,
                    'description': self.normalize(description),
                    'site': '',
                    'direct': direct,
                    'delay': 0,
                    'sstatus': 0
                })
            else:
                print('[LR] invalid region:', station, direct, file=sys.stderr)
        return buf
