# -*- coding: utf-8 -*-

import sys
import os
import json
import datetime

if __name__ == '__main__':
    sys.path.append('..')
    from prefecture import Prefecture
    from common import Common
    class Const:
        TIMETABLE_ROOT = '.'
        TIMETABLE_PATH = 'timetable'
        SOURCE_PATH = 'source'
        JSON_PATH = 'json'
else:
    from ..prefecture import Prefecture
    from .common import Common
    from ..common import Common as Const
    Const.SOURCE_PATH = os.path.join(Const.TIMETABLE_ROOT, 'source')
    Const.JSON_PATH = os.path.join(Const.TIMETABLE_ROOT, 'json')


class Scraper(Common, Const, Prefecture):

    TYPE = 'nhkr'
    URL = 'https://api.nhk.or.jp/r5/pg2/now/4/%s/netradio.json'

    # 地域
    REGION = {
        '北海道': '010',
        '東北': '040',
        '関東': '130',
        '東海': '230',
        '近畿': '270',
        '中国': '340',
        '四国': '380',
        '九州沖縄': '400',
    }

    def __init__(self, region):
        self.URL = self.URL % self.REGION[region]
        super().__init__()

    def parse(self, data):
        data = json.loads(data)
        data = data['nowonair_list']
        station = data['n1']['following']['area']['name']
        buf1 = self.setup1(data['n1'], 'NHK1', f'NHKラジオ第1({station})')
        buf2 = self.setup1(data['n2'], 'NHK2', f'NHKラジオ第2')
        buf3 = self.setup1(data['n3'], 'NHK3', f'NHK-FM({station})')
        return {
            f'NHKラジオ第1({station})': buf1,
            f'NHKラジオ第2': buf2,
            f'NHK-FM({station})': buf3,
        }

    def setup1(self, data, id_, station):
        return [
            #self.setup2(data['previous'], id_, station),
            self.setup2(data['present'], id_, station),
            self.setup2(data['following'], id_, station),
        ]

    def setup2(self, data, id_, station):
        '''
        {
            "id": "2023042071853",
            "area": {
                "id": "130",
                "name": "東京"
            },
            "date": "2023-04-20",
            "service": {
                "id": "n3",
                "name": "ＮＨＫネットラジオＦＭ",
                "images": {
                    "logo_s": {
                        "url": "https://www.nhk.or.jp/common/img/media/fm-100x50.png",
                        "width": "100",
                        "height": "50"
                    },
                    "logo_m": {
                        "url": "https://www.nhk.or.jp/common/img/media/fm-200x100.png",
                        "width": "200",
                        "height": "100"
                    },
                    "logo_l": {
                        "url": "https://www.nhk.or.jp/common/img/media/fm-200x200.png",
                        "width": "200",
                        "height": "200"
                    }
                }
            },
            "event_id": "71853",
            "start_time": "2023-04-20T05:00:00+09:00",
            "end_time": "2023-04-20T05:55:00+09:00",
            "genre": [
                "0402",
                "1002"
            ],
            "title": "古楽の楽しみ　最近の古楽の公演から、ヘルネ古楽祭（４）",
            "subtitle": "ご案内：赤塚健太郎／コレギウム・マリアヌムによる「１８世紀の水の音楽」の演奏会からお送りします。（録音：西部ドイツ放送協会）",
            "content": "",
            "images": {
                "logo_l": {
                    "url": "https://www.nhk.or.jp/prog/img/1911/1911.jpg",
                    "width": "640",
                    "height": "640"
                },
                "thumbnail_m": {
                    "url": "https://www.nhk.or.jp/prog/img/1911/g1911.jpg",
                    "width": "640",
                    "height": "360"
                },
                "hsk_posterframe": {
                    "url": ""
                }
            },
            "info": "",
            "act": "赤塚健太郎",
            "music": "「協奏曲　ロ短調　ＴＷＶ５３：ｈ１」\nテレマン:作曲\n（合奏）コレギウム・マリアヌム\n（１０分４５秒）\n～２０２１年１１月１３日ドイツ・ヘルネ、クロイツキルヒェ～\n\n「「ベルサイユの噴水」から　シャコンヌ」\nドラランド:作曲\n（合奏）コレギウム・マリアヌム\n（２分５８秒）\n～２０２１年１１月１３日ドイツ・ヘルネ、クロイツキルヒェ～\n\n「歌劇「アルシオーヌ」の組曲から」\nマレー:作曲\n（合奏）コレギウム・マリアヌム\n（７分２３秒）\n～２０２１年１１月１３日ドイツ・ヘルネ、クロイツキルヒェ～\n\n「バイオリン協奏曲　イ長調「蛙」ＴＷＶ５１：Ａ４」\nテレマン:作曲\n（合奏）コレギウム・マリアヌム\n（１２分２１秒）\n～２０２１年１１月１３日ドイツ・ヘルネ、クロイツキルヒェ～\n\n「組曲「水上の音楽」第３番　ト長調」\nヘンデル:作曲\n（合奏）コレギウム・マリアヌム\n（８分３１秒）\n～２０２１年１１月１３日ドイツ・ヘルネ、クロイツキルヒェ～\n",
            "free": "",
            "rate": "",
            "flags": {
                "sound": "03",
                "teletext": "0",
                "databroad": "0",
                "rebroad": "0",
                "multivoice": "0",
                "interactive": "0",
                "shuwa": "0",
                "oneseg": "0",
                "subchannel": "",
                "honyo": "0",
                "hybridcastid": "0",
                "kido": "0",
                "gashitsu": "0",
                "sozai": "23",
                "eizo": "0",
                "marume": "0",
                "bantype": "01",
                "dohaishin": "0",
                "hayamodoshi": "0",
                "minogashi": "0",
                "nod": "0"
            },
            "change": [],
            "lastupdate": "2023-04-17T14:13:24+09:00",
            "site_id": "1911",
            "url": {
                "pc": "https://www.nhk.jp/p/kogaku/rs/NWYPY4N3WW/",
                "short": "https://nhk.jp/P1911",
                "nod": "",
                "nod_portal": ""
            },
            "keywords": [
                "こがくのたのしみ",
                "今谷和徳",
                "古楽",
                "古楽の楽しみ",
                "大塚直哉",
                "松川梨香",
                "礒山雅",
                "関根敏子"
            ],
            "hashtags": [],
            "codes": {
                "code": "4818211",
                "split1": [
                    "4818",
                    "211"
                ]
            },
            "ch": {
                "id": "",
                "name": "",
                "station": "首都圏"
            },
            "hsk": {
                "system_unique_id": "",
                "concurrent_delivery": "",
                "early_back_delivery": "",
                "passed_delivery": "",
                "nod_delivery": "",
                "passed_start_date_time": "",
                "passed_end_date_time": "",
                "passed_delivery_period": "",
                "passed_length": "",
                "early_back_delivery_reusable_flag": "",
                "passed_type": "",
                "genban_edit_flag": "",
                "genban_caption_flag": "",
                "news_xml_url": "",
                "posterframe_image_url": "",
                "qf_flag": "",
                "qf_program_name": "",
                "update_date_time": "",
                "passed_delivery_readyable_flag": "",
                "program_kind": "",
                "flow_code": "",
                "audio_mode1": "",
                "audio_mode2": "",
                "marume_id": "",
                "epg_disp_id": "",
                "event_share_gtv": "",
                "event_share_gtv_sub": "",
                "event_share_etv": "",
                "event_share_etv_sub": "",
                "broadcast_range": "",
                "video_descriptor": "",
                "rewritable_event_id": "",
                "variable_speed_flag": ""
            },
            "plus": {
                "stream_id": "",
                "stream_fmt": ""
            },
            "extra": {
                "pr_images": [],
                "pr_movies": []
            },
            "play_control": {
                "simul": false,
                "dvr": false,
                "vod": false,
                "multi": ""
            },
            "published_period_from": "",
            "published_period_to": ""
        }
        '''
        return {
            'type': 'nhkr',
            'id': id_,
            'station': station,
            'title': self.normalize(data['title']),
            'START': self.t2string(data['start_time']),  # 2020-10-28T08:55:00+09:00
            'END': self.t2string(data['end_time']),  # 2020-10-28T09:00:00+09:00
            'start': self.t2unixtime(data['start_time']),  # 2020-10-28T08:55:00+09:00
            'end': self.t2unixtime(data['end_time']),  # 2020-10-28T09:00:00+09:00
            'weekday': self.t2weekday(data['start_time']),
            'act': self.normalize(data['act']),
            'info': self.normalize(data['subtitle']),
            'desc': self.normalize(data['music']),
            'url': data['url']['pc']
        }
    
    def t2unixtime(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # UNIX時間に変換
        return int(datetime_obj.timestamp())

    def t2weekday(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # 曜日の数字に変換
        return str(datetime_obj.weekday())

    def t2string(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.fromisoformat(t)
        # 文字列に変換
        return datetime_obj.strftime('%Y%m%d%H%M%S')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='関東')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    countdown = Scraper(args.region).update(force=args.force)
    print(countdown)
