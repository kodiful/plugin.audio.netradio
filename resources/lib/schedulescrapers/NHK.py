# -*- coding: utf-8 -*-

import json
from datetime import datetime

from resources.lib.schedulescrapers.common import Common


class Scraper(Common):

    PROTOCOL = 'NHK'
    URL = 'https://api.nhk.or.jp/r5/pg2/now/4/{region}/netradio.json'

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

    def __init__(self, sid):
        super().__init__(self.PROTOCOL)
        self.sid = sid
        self.db.cursor.execute('SELECT region FROM stations WHERE sid = :sid', {'sid': sid})
        self.region, = self.db.cursor.fetchone()
        self.URL = self.URL.format(region=self.REGION[self.region])

    def parse(self, data):
        data = json.loads(data)
        data = data['nowonair_list']
        station = data['n1']['following']['area']['name']
        buf = []
        for data, id, station in (
            (data['n1'], 'NHK1', f'NHKラジオ第1({station})'),
            (data['n2'], 'NHK2', f'NHKラジオ第2'),
            (data['n3'], 'NHK3', f'NHK-FM({station})')):
            buf += [
                #self.subparse(data['previous'], id, station),
                self.subparse(data['present'], id, station),
                self.subparse(data['following'], id, station),
            ]
        return buf

    def subparse(self, data, id, station):
        prog = {
            'station': station,
            'protocol': self.PROTOCOL,
            'key': id,
            'title': self.normalize(data['title']),
            'start': self._datetime(data['start_time']),
            'end': self._datetime(data['end_time']),
            'act': self.normalize(data['act']),
            'info': self.normalize(data['subtitle']),
            'desc': self.normalize(data['music']),
            'site': data['url']['pc'] or '',
            'region': self.region,
            'pref': ''
        }
        return prog

    def _datetime(self, t):
        # 2023-04-20T05:00:00+09:00 -> 2023-04-20 05:00:00
        datetime_obj = datetime.fromisoformat(t)
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_nextaired(self):
        sql = 'SELECT MIN(nextaired) FROM stations AS s WHERE s.protocol = :protocol AND s.region = :region'
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL, 'region': self.region})
        nextaired, = self.db.cursor.fetchone()
        return nextaired
    
    def _get_nextaired(self):
        sql = '''
        SELECT MIN(c.end)
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid
        WHERE c.end > NOW() AND s.protocol = :protocol AND s.region = :region
        '''
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL, 'region': self.region})
        nextaired, = self.db.cursor.fetchone()
        return nextaired

    def set_nextaired(self):
        sql = '''
        UPDATE stations
        SET nextaired = :nextaired
        WHERE protocol = :protocol AND region = :region
        '''
        nextaired = self._get_nextaired()
        self.db.cursor.execute(sql, {'nextaired': nextaired, 'protocol': self.PROTOCOL, 'region': self.region})
        return nextaired



# https://api.nhk.or.jp/r5/pg2/now/4/130/netradio.json

'''
{
    "nowonair_list": {
        "n1": {
            "previous": {
                "id": "2025021266583",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n1",
                    "name": "NHKネットラジオ第1",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66583",
                "start_time": "2025-02-12T14:00:00+09:00",
                "end_time": "2025-02-12T14:05:00+09:00",
                "genre": [
                    "0000"
                ],
                "title": "ニュース",
                "subtitle": "",
                "content": "",
                "images": {
                    "logo_l": {
                        "url": ""
                    },
                    "thumbnail_m": {
                        "url": ""
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "",
                "music": "",
                "free": "",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                    "sozai": "11",
                    "eizo": "0",
                    "marume": "0",
                    "bantype": "01",
                    "dohaishin": "0",
                    "hayamodoshi": "0",
                    "minogashi": "0",
                    "nod": "0"
                },
                "change": [],
                "lastupdate": "2025-02-04T10:29:39+09:00",
                "site_id": "1336",
                "url": {
                    "pc": "https://www.nhk.or.jp/radionews/",
                    "short": "https://nhk.jp/P1336",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [],
                "hashtags": [],
                "codes": {
                    "code": "3331453",
                    "split1": [
                        "3331",
                        "453"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "present": {
                "id": "2025021266584",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n1",
                    "name": "NHKネットラジオ第1",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66584",
                "start_time": "2025-02-12T14:05:00+09:00",
                "end_time": "2025-02-12T14:55:00+09:00",
                "genre": [
                    "0202"
                ],
                "title": "まんまる　午後２時台　まちのわ",
                "subtitle": "２時台は【まちのわ】列島リレーニュースなど、各地の話題をお送りする時間。水曜日は「ラジオの処方箋」。東京藝術大学が中心になった取り組みとの連携企画をお届け！",
                "content": "２時台は、各地の話題をお送りする時間、題して【まちのわ】。前半は「音の処方箋」。東京藝術大学が中心に取り組んでいる連携企画をお届け。様々な音をきっかけによりよい毎日のヒントを探ります。きょうは、ＮＨＫラジオの番組「音の風景」から、厳寒のこの季節にしか聞くことのできない音を紹介します。さらに後半は、各地の放送局を結んでお伝えする「列島リレーニュース」です。",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/GNWPP74MG4/GNWPP74MG4-logo_914966dc8043e920cf2ba69370cfbcef.png",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/GNWPP74MG4/GNWPP74MG4-eyecatch_0a8f524786306c83b8e4d1cc4532962a.png",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "浜島直子，高山哲哉，伊藤達矢",
                "music": "",
                "free": "",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                    "sozai": "11",
                    "eizo": "0",
                    "marume": "0",
                    "bantype": "01",
                    "dohaishin": "0",
                    "hayamodoshi": "0",
                    "minogashi": "0",
                    "nod": "0"
                },
                "change": [],
                "lastupdate": "2025-02-05T11:57:00+09:00",
                "site_id": "8863",
                "url": {
                    "pc": "https://www.nhk.jp/p/manmaru/rs/GNWPP74MG4/",
                    "short": "https://nhk.jp/P8863",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "まんまる"
                ],
                "hashtags": [],
                "codes": {
                    "code": "3851908",
                    "split1": [
                        "3851",
                        "908"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "following": {
                "id": "2025021266585",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n1",
                    "name": "NHKネットラジオ第1",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r1-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r1/r1-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66585",
                "start_time": "2025-02-12T14:55:00+09:00",
                "end_time": "2025-02-12T15:00:00+09:00",
                "genre": [
                    "0009",
                    "0000"
                ],
                "title": "ニュース・気象情報・交通情報",
                "subtitle": "",
                "content": "",
                "images": {
                    "logo_l": {
                        "url": ""
                    },
                    "thumbnail_m": {
                        "url": ""
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "",
                "music": "",
                "free": "　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                    "sozai": "11",
                    "eizo": "0",
                    "marume": "0",
                    "bantype": "01",
                    "dohaishin": "0",
                    "hayamodoshi": "0",
                    "minogashi": "0",
                    "nod": "0"
                },
                "change": [],
                "lastupdate": "2025-02-04T10:29:39+09:00",
                "site_id": "1336",
                "url": {
                    "pc": "https://www.nhk.or.jp/radionews/",
                    "short": "https://nhk.jp/P1336",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [],
                "hashtags": [],
                "codes": {
                    "code": "3301764",
                    "split1": [
                        "3301",
                        "764"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
        },
        "n2": {
            "previous": {
                "id": "2025021266676",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n2",
                    "name": "NHKネットラジオ第2",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66676",
                "start_time": "2025-02-12T14:10:00+09:00",
                "end_time": "2025-02-12T14:20:00+09:00",
                "genre": [
                    "0000"
                ],
                "title": "ロシア語ニュース",
                "subtitle": "",
                "content": "",
                "images": {
                    "logo_l": {
                        "url": ""
                    },
                    "thumbnail_m": {
                        "url": ""
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "",
                "music": "",
                "free": "",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                    "sozai": "09",
                    "eizo": "0",
                    "marume": "0",
                    "bantype": "01",
                    "dohaishin": "0",
                    "hayamodoshi": "0",
                    "minogashi": "0",
                    "nod": "0"
                },
                "change": [],
                "lastupdate": "2025-02-04T16:33:42+09:00",
                "site_id": "6415",
                "url": {
                    "pc": "https://www3.nhk.or.jp/nhkworld/ru/news/",
                    "short": "https://nhk.jp/P6415",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [],
                "hashtags": [],
                "codes": {
                    "code": "3380000",
                    "split1": [
                        "3380",
                        "000"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "present": {
                "id": "2025021266677",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n2",
                    "name": "NHKネットラジオ第2",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66677",
                "start_time": "2025-02-12T14:20:00+09:00",
                "end_time": "2025-02-12T14:25:00+09:00",
                "genre": [
                    "0807"
                ],
                "title": "音の風景「里山のぬくもり・菊炭～大阪～」",
                "subtitle": "【２０１３年３月９日初回放送のアーカイブ】【語り】阿部陽子　▽大阪府能勢町。多くの茶人に愛された菊炭（きくすみ）。姿も音も美しいその魅力を伝えます。",
                "content": "断面が菊の花のように見える菊炭。茶人・千利休も愛した菊炭の産地で炭職人を追いました。過酷な作業とは裏腹に、菊炭の燃える音は繊細。透き通る美しい響きをお届けします。",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/5P6KW7QL6X/5P6KW7QL6X-logo_402d922d20af19ae02763803ce5a8a7c.jpg",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/5P6KW7QL6X/5P6KW7QL6X-eyecatch_9c102476bbb1380d3118d64cdba4bc9e.jpg",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "【語り】阿部陽子",
                "music": "",
                "free": "",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                "lastupdate": "2025-02-04T16:33:42+09:00",
                "site_id": "442",
                "url": {
                    "pc": "https://www.nhk.jp/p/oto/rs/5P6KW7QL6X/",
                    "short": "https://nhk.jp/P442",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "音の風景",
                    "おとのふうけい",
                    "5分間",
                    "録音機",
                    "音響デザイナー"
                ],
                "hashtags": [],
                "codes": {
                    "code": "3506575",
                    "split1": [
                        "3506",
                        "575"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "following": {
                "id": "2025021266678",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n2",
                    "name": "NHKネットラジオ第2",
                    "images": {
                        "logo_s": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-100x50.png",
                            "width": "100",
                            "height": "50"
                        },
                        "logo_m": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x100.png",
                            "width": "200",
                            "height": "100"
                        },
                        "logo_l": {
                            "url": "https://www.nhk.or.jp/common/img/media/r2-200x200.png",
                            "width": "200",
                            "height": "200"
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r2/r2-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66678",
                "start_time": "2025-02-12T14:25:00+09:00",
                "end_time": "2025-02-12T14:30:00+09:00",
                "genre": [
                    "0402"
                ],
                "title": "名曲の小箱「バイオリン協奏曲　ホ短調」",
                "subtitle": "",
                "content": "　メンデルスゾーン作曲　（バイオリン）篠崎史紀　（管弦楽）ＮＨＫ交響楽団　（指揮）飯守泰次郎",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/JVNLM8WZGJ/JVNLM8WZGJ-logo_b92722efad9cc4de2e532fb38e780093.png",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/JVNLM8WZGJ/JVNLM8WZGJ-eyecatch_e636d527f0ce163ebf3e23615fe5a21e.png",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "篠崎史紀，飯守泰次郎",
                "music": "",
                "free": "「バイオリン協奏曲　ホ短調」　　　　　　　　　　　　　　　　\n　　　　　　　　　　　　　　　　　　　　メンデルスゾーン作曲\n　　　　　　　　　　　　　　　　　　　（バイオリン）篠崎史紀\n　　　　　　　　　　　　　　　　　　（管弦楽）ＮＨＫ交響楽団\n　　　　　　　　　　　　　　　　　　　　　（指揮）飯守泰次郎",
                "rate": "",
                "flags": {
                    "sound": "01",
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
                "lastupdate": "2025-02-04T16:33:42+09:00",
                "site_id": "309",
                "url": {
                    "pc": "https://www.nhk.jp/p/kobako/rs/JVNLM8WZGJ/",
                    "short": "https://nhk.jp/P309",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "名曲の小箱",
                    "めいきょくのこばこ"
                ],
                "hashtags": [],
                "codes": {
                    "code": "3815087",
                    "split1": [
                        "3815",
                        "087"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
        },
        "n3": {
            "previous": {
                "id": "2025021267778",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n3",
                    "name": "NHKネットラジオFM",
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
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "67778",
                "start_time": "2025-02-12T12:30:00+09:00",
                "end_time": "2025-02-12T14:00:00+09:00",
                "genre": [
                    "0404",
                    "0400"
                ],
                "title": "歌謡スクランブル　選▽都倉俊一作品集",
                "subtitle": "逢地真理子",
                "content": "",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/N8M9ZPVK4L/N8M9ZPVK4L-logo_0141e360b27dfefcfbe5df80ccd3c259.jpg",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/N8M9ZPVK4L/N8M9ZPVK4L-eyecatch_049b29ee9ae48f357fe55d8e6d21988b.jpg",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "逢地真理子",
                "music": "「あなたの心に」\n中山千夏\n（３分０２秒）\n＜ビクター　ＶＩＣＬ６１０１５＞\n\n「昨日・今日・明日」\n井上順\n（２分４１秒）\n＜ＥＭＩ　ＴＯＣＴ１０７２１－２＞\n\n「天使になれない」\n和田アキ子\n（３分１３秒）\n＜ワーナー　ＷＰＣＬ７４５＞\n\n「地球はひとつ」\nフォーリーブス\n（２分４８秒）\n＜ソニー　ＭＨＣＬ６５＞\n\n「どうにも　とまらない」\n山本リンダ\n（２分４９秒）\n＜ポニーキャニオン　ＰＣＣＳ０００８１＞\n\n「個人授業」\nフィンガー５\n（３分０１秒）\n＜ユニバーサル　ＵＰＣＹ９２７８＞\n\n「今日もどこかでデビルマン」\n十田敬三\n（２分５４秒）\n＜コロムビア　ＣＯＣＣ１０８０３＞\n\n「ひと夏の経験」\n山口百恵\n（２分３８秒）\n＜ソニー　ＭＨＣＬ１０９－１０＞\n\n「ジョニィへの伝言」\nペドロ＆カプリシャス\n（３分３４秒）\n＜ワーナー　ＷＰＣＬ１３１９２＞\n\n「青春時代」\nアリス\n（２分４６秒）\n＜ユニバーサル　ＵＩＣＺ６００４＞\n\n「同棲時代」\n大信田礼子\n（３分０９秒）\n＜ソニー　ＳＲＣＬ３９１９＞\n\n「逃避行」\n麻生よう子\n（３分４５秒）\n＜ソニー　ＳＲＣＬ３９１９＞\n\n「ペッパー警部」\nピンク・レディー\n（３分１３秒）\n＜ビクター　ＶＩＣＬ５２３６＞\n\n「渚のシンドバッド」\nピンク・レディー\n（２分３３秒）\n＜ビクター　ＶＩＣＬ５２３６＞\n\n「ウォンテッド（指名手配）」\nピンク・レディー\n（３分２２秒）\n＜ビクター　ＶＩＣＬ５２３６＞\n\n「ＵＦＯ」\nピンク・レディー\n（３分１２秒）\n＜ビクター　ＶＩＣＬ５２３６＞\n\n「あずさ２号」\n狩人\n（４分５６秒）\n＜ビクター　ＶＩＣＬ６１０１７＞\n\n「Ｌｕｉ－Ｌｕｉ（ルイ・ルイ）」\n太川陽介\n（３分３５秒）\n＜ビクター　ＶＩＣＬ７０１５５＞\n\n「ハリウッド・スキャンダル」\n郷ひろみ\n（３分５３秒）\n＜ソニー　ＳＲＣＬ３９２１＞\n\n「パープル・シャドウ」\n高田みづえ\n（３分１８秒）\n＜テイチク　ＴＥＣＮ１５２５２＞\n\n「赤頭巾ちゃん御用心」\nレイジー\n（２分４９秒）\n＜ＢＭＧファンハウス　ＢＶＣＫ３７０１７＞\n\n「私のハートはストップモーション」\n桑江知子\n（３分３７秒）\n＜ソニー　ＳＲＣＬ４９０８－９＞\n\n「君はマグノリアの花の如く」\n大地真央\n（３分２８秒）\n＜コロムビア　ＣＯＣＰ４０２５６＞\n\n「メッセージ」\n都倉俊一\n（４分０６秒）\n＜キング　ＫＩＣＳ１４０９＞\n\n「五番街のマリーへ」\nペドロ＆カプリシャス\n（３分５４秒）\n＜ワーナー　ＷＰＣＬ１３１９２＞\n",
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
                    "honyo": "1",
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
                "lastupdate": "2025-02-04T16:33:18+09:00",
                "site_id": "444",
                "url": {
                    "pc": "https://www.nhk.jp/p/kayou/rs/N8M9ZPVK4L/",
                    "short": "https://nhk.jp/P444",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "歌謡スクランブル",
                    "かようすくらんぶる"
                ],
                "hashtags": [],
                "codes": {
                    "code": "4776924",
                    "split1": [
                        "4776",
                        "924"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "present": {
                "id": "2025021266750",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n3",
                    "name": "NHKネットラジオFM",
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
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66750",
                "start_time": "2025-02-12T14:00:00+09:00",
                "end_time": "2025-02-12T15:50:00+09:00",
                "genre": [
                    "0402"
                ],
                "title": "クラシックの庭　選　アルヴェーンの交響曲第４番",
                "subtitle": "登レイナ",
                "content": "",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/LG96ZW5KZ4/LG96ZW5KZ4-logo_1b338ad05d63663074f2c1a3479c8627.jpg",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/LG96ZW5KZ4/LG96ZW5KZ4-eyecatch_a67c6e949325016c0724f2ed3eec8a2f.jpg",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "登レイナ",
                "music": "「リチェルカーレ」\nウィラールト:作曲\n（演奏）ピッファロ\n（４分２４秒）\n＜Ｕｎｉｖｅｒｓａｌ　Ｍｕｓｉｃ　ＰＯＣＡ１１１９＞\n\n「歌劇「セビリアの理髪師」から「今の歌声は」」\nロッシーニ:作曲\n（ソプラノ）マリア・カラス、（管弦楽）フィルハーモニア管弦楽団、（指揮）トゥルリオ・セラフィン\n（６分４８秒）\n＜ＥＭＩ　ＣＣ３３－３４７６＞\n\n「ハバネラ形式のヴォカリーズ」\nラヴェル:作曲\n（ソプラノ）ナタリー・デセイ、（管弦楽）ベルリン交響楽団、（指揮）ミヒャエル・シェーンヴァント\n（３分２０秒）\n＜ＥＭＩ　ＴＯＣＥ９７２５＞\n\n「交響曲第３番「広がり」」\nニルセン:作曲\n（管弦楽）デンマーク王立管弦楽団、（指揮）パーヴォ・ベルグルンド\n（３５分２０秒）\n＜ＢＭＧビクター　ＢＶＣＣ－１０７４＞\n\n「交響曲　第４番」\nアルヴェーン:作曲\n（管弦楽）ストックホルム・フィルハーモニー管弦楽団、（指揮）ネーメ・ヤルヴィ\n（４７分２１秒）\n＜ＢＩＳ　ＫＫＣＣ－２０６３＞\n",
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
                    "honyo": "1",
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
                "lastupdate": "2025-02-04T16:33:18+09:00",
                "site_id": "8917",
                "url": {
                    "pc": "https://www.nhk.jp/p/rs/LG96ZW5KZ4/",
                    "short": "https://nhk.jp/P8917",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "クラシックの庭",
                    "くらしっくのにわ"
                ],
                "hashtags": [],
                "codes": {
                    "code": "3848055",
                    "split1": [
                        "3848",
                        "055"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
            },
            "following": {
                "id": "2025021266751",
                "area": {
                    "id": "130",
                    "name": "東京"
                },
                "date": "2025-02-12",
                "service": {
                    "id": "n3",
                    "name": "NHKネットラジオFM",
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
                        },
                        "badgeSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "100",
                            "height": "50"
                        },
                        "badge": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge.svg",
                            "width": "200",
                            "height": "100"
                        },
                        "logoSmall": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-icon.svg",
                            "width": "200",
                            "height": "200"
                        },
                        "badge9x4": {
                            "url": "https://www.nhk.jp/assets/images/broadcastservice/bs/r3/r3-badge9x4.svg",
                            "width": "180",
                            "height": "80"
                        }
                    }
                },
                "event_id": "66751",
                "start_time": "2025-02-12T15:50:00+09:00",
                "end_time": "2025-02-12T15:55:00+09:00",
                "genre": [
                    "0807"
                ],
                "title": "音の風景「軽井沢の夜～長野」",
                "subtitle": "【初回放送】２０２５年２月３日【語り】荒木　さくら▽　長野県軽井沢町。早春、森の小さな池のほとりで夜を待つと現れたのは…。",
                "content": "生きものたちが躍動する早春の軽井沢。森の小さな池のほとりで夜を待つと聴こえてきたのは…。キツネやフクロウなど、生きものたちの知られざる姿を音で楽しむ５分間です。",
                "images": {
                    "logo_l": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/5P6KW7QL6X/5P6KW7QL6X-logo_402d922d20af19ae02763803ce5a8a7c.jpg",
                        "width": "640",
                        "height": "640"
                    },
                    "thumbnail_m": {
                        "url": "https://www.nhk.jp/static/assets/images/radioseries/rs/5P6KW7QL6X/5P6KW7QL6X-eyecatch_9c102476bbb1380d3118d64cdba4bc9e.jpg",
                        "width": "640",
                        "height": "360"
                    },
                    "hsk_posterframe": {
                        "url": ""
                    }
                },
                "info": "",
                "act": "【語り】荒木さくら",
                "music": "",
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
                "lastupdate": "2025-02-04T16:33:18+09:00",
                "site_id": "442",
                "url": {
                    "pc": "https://www.nhk.jp/p/oto/rs/5P6KW7QL6X/",
                    "short": "https://nhk.jp/P442",
                    "nod": "",
                    "nod_portal": ""
                },
                "keywords": [
                    "音の風景",
                    "おとのふうけい",
                    "5分間",
                    "録音機",
                    "音響デザイナー"
                ],
                "hashtags": [],
                "codes": {
                    "code": "3506181",
                    "split1": [
                        "3506",
                        "181"
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
                    "event_share_bs": "",
                    "event_share_bs_sub": "",
                    "kido": "",
                    "kidofuyo": "",
                    "shikiiki": "",
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
        }
    }
}
'''