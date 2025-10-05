# -*- coding: utf-8 -*-

import json
from datetime import datetime

from resources.lib.scrapers.schedule.common import Common


class Scraper(Common):

    PROTOCOL = 'NHK'
    URL = 'https://api.nhk.jp/r7/pg/now/radio/{region}/now.json'

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
        station = data['r1']['following']['location']['name']
        buf = []
        for data, id, station in (
            (data['r1'], 'NHK1', f'NHKラジオ第1({station})'),
            (data['r2'], 'NHK2', f'NHKラジオ第2'),
            (data['r3'], 'NHK3', f'NHK-FM({station})')):
            buf += [
                #self.subparse(data['previous'], id, station),
                self.subparse(data['present'], id, station) if data.get('present') else self.dummy_present(data, id, station),
                self.subparse(data['following'], id, station),
            ]
        return buf

    def subparse(self, data, id, station):
        # sub-objects
        #identifierGroup = data.get('identifierGroup', {'genre': []})
        misc = data.get('misc', {'actList': []})
        about = data.get('about', {'partOfSeries': {'canonical': ''}})
        # properties
        title = data['name']
        start = data['startDate']
        end = data['endDate']
        act = ', '.join(map(lambda x: x['name'], misc['actList']))
        info = ''
        desc = data['description']
        return {
            'station': station,
            'protocol': self.PROTOCOL,
            'key': id,
            'title': self.normalize(title),
            'start': self._datetime(start),
            'end': self._datetime(end),
            'act': self.normalize(act),
            'info': self.normalize(info),
            'desc': self.normalize(desc),
            'site': about['partOfSeries'].get('canonical', ''),
            'region': self.region,
            'pref': ''
        }

    def _datetime(self, t):
        # 2023-04-20T05:00:00+09:00 -> 2023-04-20 05:00:00
        datetime_obj = datetime.fromisoformat(t)
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    def search_nextaired0(self):
        # NHK全体の直近更新時間
        sql = '''SELECT c.start FROM contents AS c JOIN stations AS s ON c.sid = s.sid
        WHERE c.end > NOW() AND s.protocol = :protocol AND s.region = :region ORDER BY c.start LIMIT 1 OFFSET 1'''
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL, 'region': self.region})
        try:
            nextaired, = self.db.cursor.fetchone()
        except TypeError:
            nextaired = '1970-01-01 09:00:00'
        return nextaired

    def set_nextaired0(self):
        # 直近更新時間を取得する
        nextaired0 = self.search_nextaired0()
        # NHK全体の直近更新時間を更新する
        sql = '''UPDATE stations
        SET nextaired0 = :nextaired0
        WHERE protocol = :protocol AND region = :region'''
        self.db.cursor.execute(sql, {'nextaired0': nextaired0, 'protocol': self.PROTOCOL, 'region': self.region})
        return nextaired0

    def dummy_present(self, data, id, station):
        start = data['previous']['endDate']
        end = data['following']['startDate']
        return {
            'station': station,
            'protocol': self.PROTOCOL,
            'key': id,
            'title': '放送休止中',
            'start': self._datetime(start),
            'end': self._datetime(end),
            'act': '',
            'info': '',
            'desc': '',
            'site': '',
            'region': self.region,
            'pref': ''
        }
    

# https://api.nhk.jp/r7/pg/now/radio/130/now.json

'''
{
    "r1": {
        "previous": {
            "type": "BroadcastEvent",
            "id": "r1-130-2025100566690",
            "name": "ニュース",
            "description": "",
            "startDate": "2025-10-05T15:00:03+09:00",
            "endDate": "2025-10-05T15:05:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r1-130-2025100566690",
                "radioEpisodeId": "GPJ3N51K91",
                "radioEpisodeName": "2025年10月5日午後3:00",
                "radioSeriesId": "18439M2W42",
                "radioSeriesName": "ニュース",
                "serviceId": "r1",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66690",
                "genre": [
                    {
                        "id": "0000",
                        "name1": "ニュース/報道",
                        "name2": "定時・総合"
                    }
                ]
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "original",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r1-130-2025100566690.json",
            "about": {
                "id": "GPJ3N51K91",
                "name": "2025年10月5日午後3:00",
                "identifierGroup": {
                    "radioEpisodeId": "GPJ3N51K91",
                    "radioSeriesId": "18439M2W42",
                    "radioEpisodeName": "2025年10月5日午後3:00",
                    "radioSeriesName": "ニュース",
                    "hashtag": [],
                    "formatGenreTag": [
                        {
                            "id": "01",
                            "name": "報道"
                        }
                    ]
                },
                "keyword": [],
                "description": "",
                "partOfSeries": {
                    "id": "18439M2W42",
                    "name": "ニュース",
                    "detailedSeriesNameRuby": "にゅーす",
                    "identifierGroup": {
                        "radioSeriesId": "18439M2W42",
                        "radioSeriesPlaylistId": "series-rep-18439M2W42",
                        "radioSeriesUId": "1b7ad214-3c58-5b9d-823e-1cbb4faeb415",
                        "radioSeriesName": "ニュース",
                        "hashtag": []
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [
                        {
                            "name": "ラジオニュース",
                            "url": "https://www.nhk.or.jp/radionews/"
                        }
                    ],
                    "description": "「ニュース」の番組シリーズです",
                    "detailedCatch": "",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-logo_f3fd85b05547a8ce638c07aafda16d1e.png",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-logo_a5c82e14690bd789f8cfe7afd6c782cb.png",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-logo_25afd4d4c0aab390c131c2a9cd4e1b3c.png",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-eyecatch_c963c6bbc6954e8a56558f84785d4079.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-eyecatch_0c97620268efb78d8e63d2547b716c49.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-eyecatch_6cff57e4cf46dbf579750008620b122e.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-eyecatch_599ceb94642453f8d3038eba4dcfd357.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-hero_dc8ce87bf27cafaca943c97b35a36f17.png",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/18439M2W42/18439M2W42-hero_3757e74faf670030bd3c963e42c775da.png",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#6D7883",
                        "linkDark": "#84919E",
                        "primaryLight": "#84919E",
                        "primaryDark": "#84919E"
                    },
                    "additionalProperty": {
                        "publishLevel": "notyet",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "releasedEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/18439M2W42.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/18439M2W42.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/GPJ3N51K91.json",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r1-130-2025100566690",
                        "name": "ニュース 2025年10月5日午後3:00",
                        "description": "",
                        "url": "https://www.nhk.or.jp/radio/player/ondemand.html?p=18439M2W42_01_4274621",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r1-130-2025100566690",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "ready"
                        },
                        "detailedContent": [
                            {
                                "name": "hls_widevine",
                                "contentUrl": "https://vod-stream.nhk.jp/radioondemand/r/18439M2W42/s/stream_18439M2W42_5c96a7f00def169e630dd9c14e48195e/index.m3u8",
                                "encodingFormat": []
                            }
                        ],
                        "duration": "PT4M57S",
                        "publication": [
                            {
                                "id": "r1-130-2025100566690",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r1-130-2025100566690.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "hasPart": [],
                        "expires": "2025-10-12T15:05:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "ニュース",
                "epg80": "",
                "epgInformation": "",
                "epg200": ""
            },
            "duration": "PT4M57S",
            "posterframeList": []
        },
        "present": {
            "type": "BroadcastEvent",
            "id": "r1-130-2025100566691",
            "name": "さまよえるパパたちへ～パパだって話したい子育て話～　１０月５日",
            "description": "",
            "startDate": "2025-10-05T15:05:00+09:00",
            "endDate": "2025-10-05T15:55:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r1-130-2025100566691",
                "radioEpisodeId": "Z55R43QNL9",
                "radioEpisodeName": "〜パパだって話したい子育て話〜 10月5日",
                "radioSeriesId": "3RG2R1Y6NW",
                "radioSeriesName": "さまよえるパパたちへ",
                "serviceId": "r1",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66691",
                "genre": [
                    {
                        "id": "0504",
                        "name1": "バラエティ",
                        "name2": "音楽バラエティ"
                    }
                ],
                "siteId": "8832"
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "original",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [
                    {
                        "role": "出演",
                        "name": "ダイアモンド☆ユカイ",
                        "nameRuby": "ﾀﾞｲｱﾓﾝﾄﾞ･ﾕｶｲ"
                    },
                    {
                        "role": "出演",
                        "name": "山本博",
                        "nameRuby": "ﾔﾏﾓﾄﾋﾛｼ"
                    },
                    {
                        "role": "出演",
                        "name": "杉浦太陽",
                        "nameRuby": "ｽｷﾞｳﾗﾀｲﾖｳ"
                    }
                ],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r1-130-2025100566691.json",
            "about": {
                "id": "Z55R43QNL9",
                "name": "〜パパだって話したい子育て話〜 10月5日",
                "detailedEpisodeNameRuby": "",
                "identifierGroup": {
                    "radioEpisodeId": "Z55R43QNL9",
                    "radioSeriesId": "3RG2R1Y6NW",
                    "radioEpisodeName": "〜パパだって話したい子育て話〜 10月5日",
                    "radioSeriesName": "さまよえるパパたちへ",
                    "hashtag": [],
                    "siteId": "8832",
                    "aliasId": "samapapa",
                    "formatGenreTag": [
                        {
                            "id": "05",
                            "name": "バラエティ"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "070",
                            "name": "音楽全般"
                        }
                    ]
                },
                "keyword": [],
                "description": "ダイアモンド☆ユカイ，山本博，杉浦太陽",
                "partOfSeries": {
                    "id": "3RG2R1Y6NW",
                    "name": "さまよえるパパたちへ",
                    "detailedSeriesNameRuby": "さまよえるぱぱたちへ",
                    "identifierGroup": {
                        "radioSeriesId": "3RG2R1Y6NW",
                        "radioSeriesPlaylistId": "series-rep-3RG2R1Y6NW",
                        "radioSeriesUId": "83c2f17d-b203-5ded-bf44-e6578eccfdaf",
                        "radioSeriesName": "さまよえるパパたちへ",
                        "hashtag": [],
                        "siteId": "8832",
                        "aliasId": "samapapa",
                        "formatGenre": [
                            {
                                "id": "05",
                                "name": "バラエティ"
                            }
                        ],
                        "themeGenre": [
                            {
                                "id": "070",
                                "name": "音楽全般"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [
                        {
                            "name": "メッセージ　パパたちからのお悩みはこちらから",
                            "url": "https://forms.nhk.jp/jfe/form/SV_3QrOkYfQD1zFhzw"
                        }
                    ],
                    "canonical": "https://www.nhk.jp/p/samapapa/rs/3RG2R1Y6NW/",
                    "description": "男性が育児をすることは当たり前な時代。\nパパだって悩んでます！迷ってます！そしてパパだって語りたい！\n日々育児に奮闘するパパたちの思い、子育て体験、\nこれからの時代におけるパパこそ出来る子育てのヒントを徹底トーク！\n未来のパパたちにも捧げる、パパたちによるパパたちのための番組！\n",
                    "detailedCatch": "子育て　家庭生活　迷えるパパたち　集まれ！",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-logo_5f09731fcd6810db18f724f7ab969ac8.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-logo_d79f60de7f68f4aebe4fee353213e271.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-logo_201014f7c353bbe82dbff4b750acd772.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-eyecatch_3b842bd7c2c573381a5b925ea20255c5.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-eyecatch_148de96b5f36a39edbc28e7b904232e8.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-eyecatch_e17ae6083508dd0fc42cf1fc8be7c22b.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-eyecatch_02be06096fe7c16256b18de99551485b.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-hero_2ec421274a7d9f94f265ca0dc5f7a799.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/3RG2R1Y6NW/3RG2R1Y6NW-hero_4b5a78f8b09da761fbc3cb1ad4a24da7.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#990099",
                        "linkDark": "#C46BC4",
                        "primaryLight": "#990099",
                        "primaryDark": "#B13CB1"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "releasedEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/3RG2R1Y6NW.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/3RG2R1Y6NW.json?order=desc&offset=0&size=10"
                },
                "eyecatch": {
                    "large": {
                        "url": "https://img.nhk.jp/static/assets/images/radioepisode/re/Z55R43QNL9/Z55R43QNL9-eyecatch_f207c10eb2983f79e64cce9d4b6029d2.jpg",
                        "width": 3840,
                        "height": 2160
                    },
                    "main": {
                        "url": "https://img.nhk.jp/static/assets/images/radioepisode/re/Z55R43QNL9/Z55R43QNL9-eyecatch_8de16947f7a89a9f096969e866108556.jpg",
                        "width": 1920,
                        "height": 1080
                    },
                    "medium": {
                        "url": "https://img.nhk.jp/static/assets/images/radioepisode/re/Z55R43QNL9/Z55R43QNL9-eyecatch_76a922af1962b7a0b9c95379e95363b6.jpg",
                        "width": 1280,
                        "height": 720
                    },
                    "small": {
                        "url": "https://img.nhk.jp/static/assets/images/radioepisode/re/Z55R43QNL9/Z55R43QNL9-eyecatch_adf59eb3a66cb7d33e96c3e6aacf8cd4.jpg",
                        "width": 640,
                        "height": 360
                    }
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/Z55R43QNL9.json",
                "canonical": "https://www.nhk.jp/p/samapapa/rs/3RG2R1Y6NW/episode/re/Z55R43QNL9/",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r1-130-2025100566691",
                        "name": "さまよえるパパたちへ 〜パパだって話したい子育て話〜 10月5日",
                        "description": "",
                        "url": "",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r1-130-2025100566691",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "notyet"
                        },
                        "detailedContent": [],
                        "duration": "PT50M",
                        "publication": [
                            {
                                "id": "r1-130-2025100566691",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r1-130-2025100566691.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "expires": "2025-10-12T15:55:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "さまよえるパパたちへ～パパだって話したい子育て話～　１０月５日",
                "epg80": "ダイアモンド☆ユカイ，山本博，杉浦太陽",
                "epgInformation": "",
                "epg200": ""
            },
            "duration": "PT50M",
            "posterframeList": []
        },
        "following": {
            "type": "BroadcastEvent",
            "id": "r1-130-2025100566692",
            "name": "全国気象情報・全国交通情報",
            "description": "",
            "startDate": "2025-10-05T15:55:00+09:00",
            "endDate": "2025-10-05T16:00:03+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r1-130-2025100566692",
                "serviceId": "r1",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66692",
                "genre": [
                    {
                        "id": "0000",
                        "name1": "ニュース/報道",
                        "name2": "定時・総合"
                    }
                ]
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "original",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r1-130-2025100566692.json",
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "全国気象情報・全国交通情報",
                "epg80": "",
                "epgInformation": "",
                "epg200": ""
            },
            "duration": "PT5M3S",
            "posterframeList": []
        },
        "publishedOn": {
            "type": "BroadcastService",
            "id": "bs-r1-130",
            "name": "NHKラジオ第1放送",
            "url": "https://api.nhk.jp/r7/t/broadcastservice/bs/r1-130.json",
            "broadcastDisplayName": "NHKラジオ第1・東京",
            "videoFormat": [],
            "encodingFormat": [
                "audio/aac"
            ],
            "identifierGroup": {
                "serviceId": "r1",
                "serviceName": "NHKラジオ第1",
                "areaId": "130",
                "areaName": "東京",
                "channelId": null,
                "channelKey": null,
                "channelAreaName": "東京",
                "channelStationName": "首都圏",
                "shortenedName": "NHKラジオ第1",
                "shortenedDisplayName": "ラジオ第1",
                "multiChannelDisplayName": null
            },
            "logo": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-logo.svg",
                    "width": 1080,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-logo.svg",
                    "width": 640,
                    "height": 640
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-logo.svg",
                    "width": 200,
                    "height": 200
                }
            },
            "eyecatch": {
                "large": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-eyecatch.svg",
                    "width": 3840,
                    "height": 2160
                },
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-eyecatch.svg",
                    "width": 1920,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-eyecatch.svg",
                    "width": 640,
                    "height": 360
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-eyecatch.svg",
                    "width": 320,
                    "height": 180
                }
            },
            "hero": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-hero.svg",
                    "width": 1920,
                    "height": 640
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-hero.svg",
                    "width": 1080,
                    "height": 360
                }
            },
            "badge9x4": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-badge9x4.svg",
                    "width": 180,
                    "height": 80
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r1/r1-badge9x4.svg",
                    "width": 90,
                    "height": 40
                }
            }
        }
    },
    "r2": {
        "previous": {
            "type": "BroadcastEvent",
            "id": "r2-130-2025100566774",
            "name": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（３）",
            "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
            "startDate": "2025-10-05T14:45:00+09:00",
            "endDate": "2025-10-05T15:00:03+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r2-130-2025100566774",
                "radioEpisodeId": "7Y55628X7L",
                "radioEpisodeName": "ラップ de チャレッソYO! (3)",
                "radioSeriesId": "LR47WW9K14",
                "radioSeriesName": "まいにちハングル講座",
                "serviceId": "r2",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66774",
                "genre": [
                    {
                        "id": "1007",
                        "name1": "趣味/教育",
                        "name2": "会話・語学"
                    },
                    {
                        "id": "1011",
                        "name1": "趣味/教育",
                        "name2": "生涯教育・資格"
                    },
                    {
                        "id": "1010",
                        "name1": "趣味/教育",
                        "name2": "大学生・受験"
                    }
                ],
                "siteId": "0951"
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "normal",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [
                    {
                        "role": "講師",
                        "title": "近畿大学准教授",
                        "name": "小島大輝",
                        "nameRuby": "ｺｼﾞﾏﾀﾞｲｷ"
                    },
                    {
                        "role": "出演",
                        "name": "イ・ユンジョン",
                        "nameRuby": "ｲ･ﾕﾝｼﾞｮﾝ"
                    },
                    {
                        "role": "出演",
                        "name": "ユン・チャンビン",
                        "nameRuby": "ﾕﾝ･ﾁｬﾝﾋﾞﾝ"
                    }
                ],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100566774.json",
            "about": {
                "id": "7Y55628X7L",
                "name": "ラップ de チャレッソYO! (3)",
                "identifierGroup": {
                    "radioEpisodeId": "7Y55628X7L",
                    "radioSeriesId": "LR47WW9K14",
                    "radioEpisodeName": "ラップ de チャレッソYO! (3)",
                    "radioSeriesName": "まいにちハングル講座",
                    "hashtag": [],
                    "siteId": "0951",
                    "formatGenreTag": [
                        {
                            "id": "09",
                            "name": "講座"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "101",
                            "name": "語学"
                        }
                    ]
                },
                "keyword": [],
                "description": "ナ行、マ行、ラ行の子音が読めて書けるようになりましょう！",
                "partOfSeries": {
                    "id": "LR47WW9K14",
                    "name": "まいにちハングル講座",
                    "detailedSeriesNameRuby": "まいにちはんぐるこうざ",
                    "identifierGroup": {
                        "radioSeriesId": "LR47WW9K14",
                        "radioSeriesPlaylistId": "series-rep-LR47WW9K14",
                        "radioSeriesUId": "361cdaf6-b789-58dd-aa22-1838a8d776f3",
                        "radioSeriesName": "まいにちハングル講座",
                        "hashtag": [],
                        "siteId": "0951",
                        "formatGenre": [
                            {
                                "id": "09",
                                "name": "講座"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/",
                    "description": "わかりやすく・親しみやすく、ゼロから文字・発音・文法などの基礎を積み上げていく講座です。リズムにのってラップ風に声を出す練習法で、単語や活用を楽しく身につけていきましょう。（２０２４年４～９月の再放送）",
                    "detailedCatch": "ラップ de チャレッソYO！",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f54a67be8c4eb9a642e8a722580a905.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_1a25b4ed1f1c4c9064947548bbdadc8a.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f9764c76ddd240ed7c7afe8c8e6be81.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_fe4336a18e2d7f9f0ecdc13f01371d58.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_50e84774111735ee01fd76615592b07e.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_1efebe0b1a9ab024d087988e273d1a8c.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_91bd6d43742becdcaf4be3e9b91e7772.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_9ab657182854b161722998cea6382313.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_7c1235030e5420a42af73e9861309b52.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#7B7700",
                        "linkDark": "#FAF100",
                        "primaryLight": "#9B9500",
                        "primaryDark": "#FAF100"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "recentEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/LR47WW9K14.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/LR47WW9K14.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/7Y55628X7L.json",
                "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/episode/re/7Y55628X7L/",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r2-130-2025100175669",
                        "name": "まいにちハングル講座 ラップ de チャレッソYO! (3)",
                        "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
                        "url": "https://www.nhk.or.jp/radio/player/ondemand.html?p=LR47WW9K14_01_4273803",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r2-130-2025100175669",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "ready"
                        },
                        "detailedContent": [
                            {
                                "name": "hls_widevine",
                                "contentUrl": "https://vod-stream.nhk.jp/radioondemand/r/LR47WW9K14/s/stream_LR47WW9K14_e46f97b05e2e1e7c93ce5d86ee33af8b/index.m3u8",
                                "encodingFormat": []
                            }
                        ],
                        "duration": "PT14M57S",
                        "publication": [
                            {
                                "id": "r2-130-2025100175669",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100175669.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "hasPart": [],
                        "expires": "2025-10-08T08:15:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（３）",
                "epg80": "ナ行、マ行、ラ行の子音が読めて書けるようになりましょう！",
                "epgInformation": "",
                "epg200": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン"
            },
            "duration": "PT15M3S",
            "posterframeList": []
        },
        "present": {
            "type": "BroadcastEvent",
            "id": "r2-130-2025100566776",
            "name": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（４）",
            "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
            "startDate": "2025-10-05T15:00:03+09:00",
            "endDate": "2025-10-05T15:15:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r2-130-2025100566776",
                "radioEpisodeId": "99364V18WW",
                "radioEpisodeName": "ラップ de チャレッソYO! (4)",
                "radioSeriesId": "LR47WW9K14",
                "radioSeriesName": "まいにちハングル講座",
                "serviceId": "r2",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66776",
                "genre": [
                    {
                        "id": "1007",
                        "name1": "趣味/教育",
                        "name2": "会話・語学"
                    },
                    {
                        "id": "1011",
                        "name1": "趣味/教育",
                        "name2": "生涯教育・資格"
                    },
                    {
                        "id": "1010",
                        "name1": "趣味/教育",
                        "name2": "大学生・受験"
                    }
                ],
                "siteId": "0951"
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "normal",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [
                    {
                        "role": "講師",
                        "title": "近畿大学准教授",
                        "name": "小島大輝",
                        "nameRuby": "ｺｼﾞﾏﾀﾞｲｷ"
                    },
                    {
                        "role": "出演",
                        "name": "イ・ユンジョン",
                        "nameRuby": "ｲ･ﾕﾝｼﾞｮﾝ"
                    },
                    {
                        "role": "出演",
                        "name": "ユン・チャンビン",
                        "nameRuby": "ﾕﾝ･ﾁｬﾝﾋﾞﾝ"
                    }
                ],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100566776.json",
            "about": {
                "id": "99364V18WW",
                "name": "ラップ de チャレッソYO! (4)",
                "identifierGroup": {
                    "radioEpisodeId": "99364V18WW",
                    "radioSeriesId": "LR47WW9K14",
                    "radioEpisodeName": "ラップ de チャレッソYO! (4)",
                    "radioSeriesName": "まいにちハングル講座",
                    "hashtag": [],
                    "siteId": "0951",
                    "formatGenreTag": [
                        {
                            "id": "09",
                            "name": "講座"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "101",
                            "name": "語学"
                        }
                    ]
                },
                "keyword": [],
                "description": "ヤ行が読めて書けるようになりましょう！",
                "partOfSeries": {
                    "id": "LR47WW9K14",
                    "name": "まいにちハングル講座",
                    "detailedSeriesNameRuby": "まいにちはんぐるこうざ",
                    "identifierGroup": {
                        "radioSeriesId": "LR47WW9K14",
                        "radioSeriesPlaylistId": "series-rep-LR47WW9K14",
                        "radioSeriesUId": "361cdaf6-b789-58dd-aa22-1838a8d776f3",
                        "radioSeriesName": "まいにちハングル講座",
                        "hashtag": [],
                        "siteId": "0951",
                        "formatGenre": [
                            {
                                "id": "09",
                                "name": "講座"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/",
                    "description": "わかりやすく・親しみやすく、ゼロから文字・発音・文法などの基礎を積み上げていく講座です。リズムにのってラップ風に声を出す練習法で、単語や活用を楽しく身につけていきましょう。（２０２４年４～９月の再放送）",
                    "detailedCatch": "ラップ de チャレッソYO！",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f54a67be8c4eb9a642e8a722580a905.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_1a25b4ed1f1c4c9064947548bbdadc8a.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f9764c76ddd240ed7c7afe8c8e6be81.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_fe4336a18e2d7f9f0ecdc13f01371d58.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_50e84774111735ee01fd76615592b07e.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_1efebe0b1a9ab024d087988e273d1a8c.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_91bd6d43742becdcaf4be3e9b91e7772.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_9ab657182854b161722998cea6382313.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_7c1235030e5420a42af73e9861309b52.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#7B7700",
                        "linkDark": "#FAF100",
                        "primaryLight": "#9B9500",
                        "primaryDark": "#FAF100"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "recentEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/LR47WW9K14.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/LR47WW9K14.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/99364V18WW.json",
                "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/episode/re/99364V18WW/",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r2-130-2025100275939",
                        "name": "まいにちハングル講座 ラップ de チャレッソYO! (4)",
                        "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
                        "url": "https://www.nhk.or.jp/radio/player/ondemand.html?p=LR47WW9K14_01_4274005",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r2-130-2025100275939",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "ready"
                        },
                        "detailedContent": [
                            {
                                "name": "hls_widevine",
                                "contentUrl": "https://vod-stream.nhk.jp/radioondemand/r/LR47WW9K14/s/stream_LR47WW9K14_27b348934c9b0e54c30cd6d4fb4d964c/index.m3u8",
                                "encodingFormat": []
                            }
                        ],
                        "duration": "PT14M57S",
                        "publication": [
                            {
                                "id": "r2-130-2025100275939",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100275939.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "hasPart": [],
                        "expires": "2025-10-09T08:15:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（４）",
                "epg80": "ヤ行が読めて書けるようになりましょう！",
                "epgInformation": "",
                "epg200": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン"
            },
            "duration": "PT14M57S",
            "posterframeList": []
        },
        "following": {
            "type": "BroadcastEvent",
            "id": "r2-130-2025100566777",
            "name": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（５）",
            "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
            "startDate": "2025-10-05T15:15:00+09:00",
            "endDate": "2025-10-05T15:30:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r2-130-2025100566777",
                "radioEpisodeId": "GP5GNNXRRP",
                "radioEpisodeName": "ラップ de チャレッソYO! (5)",
                "radioSeriesId": "LR47WW9K14",
                "radioSeriesName": "まいにちハングル講座",
                "serviceId": "r2",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66777",
                "genre": [
                    {
                        "id": "1007",
                        "name1": "趣味/教育",
                        "name2": "会話・語学"
                    },
                    {
                        "id": "1011",
                        "name1": "趣味/教育",
                        "name2": "生涯教育・資格"
                    },
                    {
                        "id": "1010",
                        "name1": "趣味/教育",
                        "name2": "大学生・受験"
                    }
                ],
                "siteId": "0951"
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "normal",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [
                    {
                        "role": "講師",
                        "title": "近畿大学准教授",
                        "name": "小島大輝",
                        "nameRuby": "ｺｼﾞﾏﾀﾞｲｷ"
                    },
                    {
                        "role": "出演",
                        "name": "イ・ユンジョン",
                        "nameRuby": "ｲ･ﾕﾝｼﾞｮﾝ"
                    },
                    {
                        "role": "出演",
                        "name": "ユン・チャンビン",
                        "nameRuby": "ﾕﾝ･ﾁｬﾝﾋﾞﾝ"
                    }
                ],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100566777.json",
            "about": {
                "id": "GP5GNNXRRP",
                "name": "ラップ de チャレッソYO! (5)",
                "identifierGroup": {
                    "radioEpisodeId": "GP5GNNXRRP",
                    "radioSeriesId": "LR47WW9K14",
                    "radioEpisodeName": "ラップ de チャレッソYO! (5)",
                    "radioSeriesName": "まいにちハングル講座",
                    "hashtag": [],
                    "siteId": "0951",
                    "formatGenreTag": [
                        {
                            "id": "09",
                            "name": "講座"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "101",
                            "name": "語学"
                        }
                    ]
                },
                "keyword": [],
                "description": "今週のハンぐるり",
                "partOfSeries": {
                    "id": "LR47WW9K14",
                    "name": "まいにちハングル講座",
                    "detailedSeriesNameRuby": "まいにちはんぐるこうざ",
                    "identifierGroup": {
                        "radioSeriesId": "LR47WW9K14",
                        "radioSeriesPlaylistId": "series-rep-LR47WW9K14",
                        "radioSeriesUId": "361cdaf6-b789-58dd-aa22-1838a8d776f3",
                        "radioSeriesName": "まいにちハングル講座",
                        "hashtag": [],
                        "siteId": "0951",
                        "formatGenre": [
                            {
                                "id": "09",
                                "name": "講座"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/",
                    "description": "わかりやすく・親しみやすく、ゼロから文字・発音・文法などの基礎を積み上げていく講座です。リズムにのってラップ風に声を出す練習法で、単語や活用を楽しく身につけていきましょう。（２０２４年４～９月の再放送）",
                    "detailedCatch": "ラップ de チャレッソYO！",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f54a67be8c4eb9a642e8a722580a905.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_1a25b4ed1f1c4c9064947548bbdadc8a.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-logo_5f9764c76ddd240ed7c7afe8c8e6be81.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_fe4336a18e2d7f9f0ecdc13f01371d58.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_50e84774111735ee01fd76615592b07e.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_1efebe0b1a9ab024d087988e273d1a8c.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-eyecatch_91bd6d43742becdcaf4be3e9b91e7772.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_9ab657182854b161722998cea6382313.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/LR47WW9K14/LR47WW9K14-hero_7c1235030e5420a42af73e9861309b52.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#7B7700",
                        "linkDark": "#FAF100",
                        "primaryLight": "#9B9500",
                        "primaryDark": "#FAF100"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "recentEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/LR47WW9K14.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/LR47WW9K14.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/GP5GNNXRRP.json",
                "canonical": "https://www.nhk.jp/p/rs/LR47WW9K14/episode/re/GP5GNNXRRP/",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r2-130-2025100366214",
                        "name": "まいにちハングル講座 ラップ de チャレッソYO! (5)",
                        "description": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン",
                        "url": "https://www.nhk.or.jp/radio/player/ondemand.html?p=LR47WW9K14_01_4274321",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r2-130-2025100366214",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "ready"
                        },
                        "detailedContent": [
                            {
                                "name": "hls_widevine",
                                "contentUrl": "https://vod-stream.nhk.jp/radioondemand/r/LR47WW9K14/s/stream_LR47WW9K14_242c362693fa7c33fa55bc79d30d14cf/index.m3u8",
                                "encodingFormat": []
                            }
                        ],
                        "duration": "PT14M57S",
                        "publication": [
                            {
                                "id": "r2-130-2025100366214",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r2-130-2025100366214.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "hasPart": [],
                        "expires": "2025-10-10T08:15:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "まいにちハングル講座　ラップ　ｄｅ　チャレッソＹＯ！（５）",
                "epg80": "今週のハンぐるり",
                "epgInformation": "",
                "epg200": "【講師】近畿大学准教授…小島大輝，【出演】イ・ユンジョン，ユン・チャンビン"
            },
            "duration": "PT15M",
            "posterframeList": []
        },
        "publishedOn": {
            "type": "BroadcastService",
            "id": "bs-r2-130",
            "name": "NHKラジオ第2放送",
            "url": "https://api.nhk.jp/r7/t/broadcastservice/bs/r2-130.json",
            "broadcastDisplayName": "NHKラジオ第2",
            "videoFormat": [],
            "encodingFormat": [
                "audio/aac"
            ],
            "identifierGroup": {
                "serviceId": "r2",
                "serviceName": "NHKラジオ第2",
                "areaId": "130",
                "areaName": "東京",
                "channelId": null,
                "channelKey": null,
                "channelAreaName": "東京",
                "channelStationName": "首都圏",
                "shortenedName": "NHKラジオ第2",
                "shortenedDisplayName": "ラジオ第2",
                "multiChannelDisplayName": null
            },
            "logo": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-logo.svg",
                    "width": 1080,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-logo.svg",
                    "width": 640,
                    "height": 640
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-logo.svg",
                    "width": 200,
                    "height": 200
                }
            },
            "eyecatch": {
                "large": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-eyecatch.svg",
                    "width": 3840,
                    "height": 2160
                },
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-eyecatch.svg",
                    "width": 1920,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-eyecatch.svg",
                    "width": 640,
                    "height": 360
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-eyecatch.svg",
                    "width": 320,
                    "height": 180
                }
            },
            "hero": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-hero.svg",
                    "width": 1920,
                    "height": 640
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-hero.svg",
                    "width": 1080,
                    "height": 360
                }
            },
            "badge9x4": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-badge9x4.svg",
                    "width": 180,
                    "height": 80
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r2/r2-badge9x4.svg",
                    "width": 90,
                    "height": 40
                }
            }
        }
    },
    "r3": {
        "previous": {
            "type": "BroadcastEvent",
            "id": "r3-130-2025100566858",
            "name": "みんなのうた「青空とオスカー・ピーターソン」／「ハナ」",
            "description": "",
            "startDate": "2025-10-05T13:55:00+09:00",
            "endDate": "2025-10-05T14:00:03+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r3-130-2025100566858",
                "radioEpisodeId": "BQ7JQYMMYJ",
                "radioEpisodeName": "「青空とオスカー・ピーターソン」/「ハナ」",
                "radioSeriesId": "GPVXV8GJ9V",
                "radioSeriesName": "みんなのうた （R1 R2 FM）",
                "serviceId": "r3",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66858",
                "genre": [
                    {
                        "id": "0400",
                        "name1": "音楽",
                        "name2": "国内ロック・ポップス"
                    },
                    {
                        "id": "0409",
                        "name1": "音楽",
                        "name2": "童謡・キッズ"
                    },
                    {
                        "id": "0504",
                        "name1": "バラエティ",
                        "name2": "音楽バラエティ"
                    }
                ]
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "normal",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r3-130-2025100566858.json",
            "about": {
                "id": "BQ7JQYMMYJ",
                "name": "「青空とオスカー・ピーターソン」/「ハナ」",
                "identifierGroup": {
                    "radioEpisodeId": "BQ7JQYMMYJ",
                    "radioSeriesId": "GPVXV8GJ9V",
                    "radioEpisodeName": "「青空とオスカー・ピーターソン」/「ハナ」",
                    "radioSeriesName": "みんなのうた （R1 R2 FM）",
                    "hashtag": [],
                    "formatGenreTag": [
                        {
                            "id": "05",
                            "name": "バラエティ"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "071",
                            "name": "国内ポップス"
                        },
                        {
                            "id": "077",
                            "name": "キッズ音楽"
                        },
                        {
                            "id": "070",
                            "name": "音楽全般"
                        }
                    ]
                },
                "keyword": [],
                "description": "",
                "partOfSeries": {
                    "id": "GPVXV8GJ9V",
                    "name": "みんなのうた （R1 R2 FM）",
                    "detailedSeriesNameRuby": "みんなのうた　あーるわん　あーるつー　えふえむ",
                    "identifierGroup": {
                        "radioSeriesId": "GPVXV8GJ9V",
                        "radioSeriesPlaylistId": "series-rep-GPVXV8GJ9V",
                        "radioSeriesUId": "7c78079e-d869-5dcd-9621-69f4bc0f3127",
                        "radioSeriesName": "みんなのうた （R1 R2 FM）",
                        "hashtag": [],
                        "themeGenre": [
                            {
                                "id": "070",
                                "name": "音楽全般"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/rs/GPVXV8GJ9V/",
                    "description": "「みんなのうた」はNHKのテレビ・ラジオで放送されている5分間の音楽番組。「こどもたちに明るい健康な歌をとどけたい」というコンセプトで、１９６１年４月３日に放送をスタートしました。昭和、平成、令和・・・時代とともに、これまでお送りしてきた楽曲（うた）は、およそ１６００曲。\nこれからも２ヶ月ごとに４曲ほどの新たな楽曲、さらに懐かしい名曲たちもたっぷりお届けします。",
                    "detailedCatch": "ラジオ（ラジオ第１・第２、NHK-FM）の放送情報をお届けします",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_57226883daf0c7cc5b940da5330d0420.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_dfd3cb138345821ffdffb6e2591f2898.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_d697ff3a73ca93916e7fe31d5ec5b261.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_df8aa9b18845de8661ef6fe911696c0e.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_83d3405716a8acd1518794b80dccbc47.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_5fed05c55b50c98f53cd7e9a972bddf2.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_4e045f1fe08e57beb7212b6474f14e48.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-hero_3c1181bd7c8e3792abe6bb7a9bfe653d.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-hero_6cfce4be1bf01cddfa01c5933e5cc477.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#990099",
                        "linkDark": "#C062C0",
                        "primaryLight": "#990099",
                        "primaryDark": "#AD32AD"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "releasedEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/GPVXV8GJ9V.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/GPVXV8GJ9V.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/BQ7JQYMMYJ.json",
                "canonical": "https://www.nhk.jp/p/rs/GPVXV8GJ9V/episode/re/BQ7JQYMMYJ/",
                "additionalProperty": {},
                "audio": []
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "みんなのうた「青空とオスカー・ピーターソン」／「ハナ」",
                "epg80": "",
                "epgInformation": "",
                "epg200": ""
            },
            "duration": "PT5M3S",
            "posterframeList": []
        },
        "present": {
            "type": "BroadcastEvent",
            "id": "r3-130-2025100566860",
            "name": "×（かける）クラシック▽第２５２駅　クラシック×変（１）",
            "description": "▽涼しくなったかと思えば、真夏日が続いたり…変な気候だなぁと感じることが多い昨今。そこで１０月は「変」をテーマにクラシック音楽の世界を巡ります▽今週はリスナーが感じる「風変わりな作品や音楽家」が目白押し▽「今週の○○節」は映画音楽の巨匠モリコーネ。モリコーネ節のラスト月間突入ということで“シャレオツモリコーネ”と“美メロモリコーネ”の２曲紹介▽かけクラ川柳も通常運行中！久々の「献呈」コーナーも！",
            "startDate": "2025-10-05T14:00:03+09:00",
            "endDate": "2025-10-05T15:50:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r3-130-2025100566860",
                "radioEpisodeId": "Y6XKJY2W1W",
                "radioEpisodeName": "▽第252駅 クラシック×変(1)",
                "radioSeriesId": "QM16JZPN81",
                "radioSeriesName": "×(かける)クラシック",
                "serviceId": "r3",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66860",
                "genre": [
                    {
                        "id": "0402",
                        "name1": "音楽",
                        "name2": "クラシック・オペラ"
                    }
                ],
                "siteId": "5945"
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "original",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [
                    {
                        "name": "市川紗椰",
                        "nameRuby": "ｲﾁｶﾜｻﾔ"
                    },
                    {
                        "name": "上野耕平",
                        "nameRuby": "ｳｴﾉｺｳﾍｲ"
                    }
                ],
                "musicList": [
                    {
                        "name": "バレエ音楽「ロメオとジュリエット」から「モンタギュー家とキャピュレット家」",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "プロコフィエフ",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "ＳＯＮＹ",
                        "duration": "PT5M17S",
                        "code": "SICC2082",
                        "byArtist": [
                            {
                                "name": "ニューヨーク・フィルハーモニック",
                                "role": "",
                                "part": "管弦楽"
                            },
                            {
                                "name": "ディミトリ・ミトロプーロス",
                                "role": "",
                                "part": "指揮"
                            }
                        ]
                    },
                    {
                        "name": "ロンド・ア・カプリッチョ「なくしたた小銭への怒り」",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "ベートーベン",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "Ｄｅｕｔｓｃｈｅ　Ｇｒａｍｍｏｐｈｏｎ",
                        "duration": "PT6M15S",
                        "code": "UCCG1518",
                        "byArtist": [
                            {
                                "name": "アリス・紗良・オット",
                                "role": "",
                                "part": "ピアノ"
                            }
                        ]
                    },
                    {
                        "name": "口琴とマンドーラのための協奏曲　ホ長調　から　第１楽章",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "アルブレヒツベルガー",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "ＯＲＦＥＯ　ＩＮＴＥＲＮＡＴＩＯＮＡＬ",
                        "duration": "PT6M30S",
                        "code": "32CD10046",
                        "byArtist": [
                            {
                                "name": "フリッツ・マイア",
                                "role": "",
                                "part": "口琴"
                            },
                            {
                                "name": "ディーター・キルシュ",
                                "role": "",
                                "part": "マンドーラ"
                            },
                            {
                                "name": "ミュンヘン室内管弦楽団",
                                "role": "",
                                "part": "管弦楽"
                            },
                            {
                                "name": "ハンス・シュタートルマイア",
                                "role": "",
                                "part": "指揮"
                            }
                        ]
                    },
                    {
                        "name": "変",
                        "nameruby": "",
                        "lyricist": "ドリアン助川",
                        "composer": "寺嶋陸也",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "フォンテック",
                        "duration": "PT2M15S",
                        "code": "EFCD25133",
                        "byArtist": [
                            {
                                "name": "熊本大学教育学部附属中学校",
                                "role": "",
                                "part": "合唱"
                            }
                        ]
                    },
                    {
                        "name": "マドリガーレ集第３巻から「私の心はため息をついた～ああ，悲惨な，悪意にみちた知らせよ」",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "カルロ・ジェズアルド",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "ＨＡＲＭＯＮＩＡ　ＭＵＮＤＩ",
                        "duration": "PT3M40S",
                        "code": "ANF197",
                        "byArtist": [
                            {
                                "name": "レザール・フロリサン・アンサンブル",
                                "role": "",
                                "part": "演奏"
                            },
                            {
                                "name": "ウィリアム・クリスティ",
                                "role": "",
                                "part": "指揮"
                            }
                        ]
                    },
                    {
                        "name": "映画「ある夕食のテーブル」メインテーマ",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "モリコーネ",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "Ｋｉｎｇ",
                        "duration": "PT4M31S",
                        "code": "KICP843",
                        "byArtist": [
                            {
                                "name": "オリジナル・サウンドトラック",
                                "role": "",
                                "part": ""
                            }
                        ]
                    },
                    {
                        "name": "映画「ウエスタン」テーマ",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "モリコーネ",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "ＢＭＧビクター",
                        "duration": "PT3M31S",
                        "code": "BVCP1038",
                        "byArtist": [
                            {
                                "name": "オリジナル・サウンドトラック",
                                "role": "",
                                "part": ""
                            }
                        ]
                    },
                    {
                        "name": "見上げてごらん夜の星を",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "いずみたく",
                        "arranger": "小原孝",
                        "location": "",
                        "provider": "",
                        "label": "Ｋｉｎｇ",
                        "duration": "PT3M51S",
                        "code": "KICS1885",
                        "byArtist": [
                            {
                                "name": "小原孝",
                                "role": "",
                                "part": "ピアノ"
                            }
                        ]
                    },
                    {
                        "name": "「Ｔｈｅ　Ｅｎｄ　ｏｆ　ｔｈｅ　Ｗｏｒｌｄ」から「Ｂｅｙｏｎｄ　ｔｈｅ　Ｗｏｒｌｄ」",
                        "nameruby": "",
                        "lyricist": "",
                        "composer": "久石譲",
                        "arranger": "",
                        "location": "",
                        "provider": "",
                        "label": "ＵＮＩＶＥＲＳＡＬ",
                        "duration": "PT7M11S",
                        "code": "UMCK1321",
                        "byArtist": [
                            {
                                "name": "ロンドン・ヴォイセズ",
                                "role": "",
                                "part": "合唱"
                            },
                            {
                                "name": "ロンドン交響楽団",
                                "role": "",
                                "part": "管弦楽"
                            },
                            {
                                "name": "久石譲",
                                "role": "",
                                "part": "指揮"
                            }
                        ]
                    }
                ],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r3-130-2025100566860.json",
            "about": {
                "id": "Y6XKJY2W1W",
                "name": "▽第252駅 クラシック×変(1)",
                "identifierGroup": {
                    "radioEpisodeId": "Y6XKJY2W1W",
                    "radioSeriesId": "QM16JZPN81",
                    "radioEpisodeName": "▽第252駅 クラシック×変(1)",
                    "radioSeriesName": "×(かける)クラシック",
                    "hashtag": [],
                    "siteId": "5945",
                    "aliasId": "kakecla",
                    "themeGenreTag": [
                        {
                            "id": "073",
                            "name": "クラシック"
                        }
                    ]
                },
                "keyword": [],
                "description": "▽涼しくなったかと思えば、真夏日が続いたり…変な気候だなぁと感じることが多い昨今。そこで１０月は「変」をテーマにクラシック音楽の世界を巡ります▽今週はリスナーが感じる「風変わりな作品や音楽家」が目白押し▽「今週の○○節」は映画音楽の巨匠モリコーネ。モリコーネ節のラスト月間突入ということで“シャレオツモリコーネ”と“美メロモリコーネ”の２曲紹介▽かけクラ川柳も通常運行中！久々の「献呈」コーナーも！",
                "partOfSeries": {
                    "id": "QM16JZPN81",
                    "name": "×(かける)クラシック",
                    "detailedSeriesNameRuby": "かけるくらしっく",
                    "identifierGroup": {
                        "radioSeriesId": "QM16JZPN81",
                        "radioSeriesPlaylistId": "series-rep-QM16JZPN81",
                        "radioSeriesUId": "23cdc288-bb23-51b2-a660-33d9d0403911",
                        "radioSeriesName": "×(かける)クラシック",
                        "hashtag": [],
                        "siteId": "5945",
                        "aliasId": "kakecla"
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/kakecla/rs/QM16JZPN81/",
                    "description": "番組のキーワードは、ずばり、「○○○×（かける）クラシック」。モデルの市川紗椰＆サクソフォーン奏者の上野耕平が、クラシックとそれ以外の様々なジャンルを掛け合わせてご紹介！\nテーマとして○○○に入るのは、鉄道・小説・アニメ・旅行・ファッションといった趣味のジャンルから、恋愛・季節の話題まで様々。気軽なトークと音楽を“クロスオーバー”に楽しむ、クラシック・バラエティです。",
                    "detailedCatch": "日常と音が出会うターミナル",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-logo_8a07849d8a4ce8747187f5dc989392b4.png",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-logo_b492cb6ebf37bae0370a7475b06deff5.png",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-logo_80afddba801451597bbd9b75837d4c7b.png",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-eyecatch_8bfbe7f42cd3b78df3e5cb3122401448.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-eyecatch_b4a3853077a29cf3631c43e270212c99.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-eyecatch_907bef2811d561b5d8296b357ea683e4.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-eyecatch_6d6be8d0523dfdc95212e70be444866b.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-hero_ce7b6ce0d3990b369c40da7243d99f4f.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/QM16JZPN81/QM16JZPN81-hero_32f1918b842028875c6de3a9a1702c1f.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#005AFF",
                        "linkDark": "#4788FF",
                        "primaryLight": "#005AFF",
                        "primaryDark": "#0B61FF"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "releasedEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/QM16JZPN81.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/QM16JZPN81.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/Y6XKJY2W1W.json",
                "canonical": "https://www.nhk.jp/p/kakecla/rs/QM16JZPN81/episode/re/Y6XKJY2W1W/",
                "additionalProperty": {},
                "audio": [
                    {
                        "id": "radiruOriginal-r3-130-2025100566860",
                        "name": "×(かける)クラシック ▽第252駅 クラシック×変(1)",
                        "description": "▽涼しくなったかと思えば、真夏日が続いたり…変な気候だなぁと感じることが多い昨今。そこで１０月は「変」をテーマにクラシック音楽の世界を巡ります▽今週はリスナーが感じる「風変わりな作品や音楽家」が目白押し▽「今週の○○節」は映画音楽の巨匠モリコーネ。モリコーネ節のラスト月間突入ということで“シャレオツモリコーネ”と“美メロモリコーネ”の２曲紹介▽かけクラ川柳も通常運行中！久々の「献呈」コーナーも！",
                        "url": "",
                        "identifierGroup": {
                            "environmentId": "radiruOriginal",
                            "broadcastEventId": "r3-130-2025100566860",
                            "streamType": "vod"
                        },
                        "detailedContentStatus": {
                            "environmentId": "radiruOriginal",
                            "streamType": "vod",
                            "contentStatus": "notyet"
                        },
                        "detailedContent": [],
                        "duration": "PT1H49M57S",
                        "publication": [
                            {
                                "id": "r3-130-2025100566860",
                                "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r3-130-2025100566860.json",
                                "isLiveBroadcast": false
                            }
                        ],
                        "expires": "2025-10-12T15:50:00+09:00"
                    }
                ]
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "×（かける）クラシック▽第２５２駅　クラシック×変（１）",
                "epg80": "×（かける）クラシック第２５２駅▽１０月のテーマ「変×クラシック」【ＭＣ】市川紗椰（モデル）、上野耕平（サクソフォーン奏者）",
                "epgInformation": "",
                "epg200": "▽涼しくなったかと思えば、真夏日が続いたり…変な気候だなぁと感じることが多い昨今。そこで１０月は「変」をテーマにクラシック音楽の世界を巡ります▽今週はリスナーが感じる「風変わりな作品や音楽家」が目白押し▽「今週の○○節」は映画音楽の巨匠モリコーネ。モリコーネ節のラスト月間突入ということで“シャレオツモリコーネ”と“美メロモリコーネ”の２曲紹介▽かけクラ川柳も通常運行中！久々の「献呈」コーナーも！"
            },
            "duration": "PT1H49M57S",
            "posterframeList": []
        },
        "following": {
            "type": "BroadcastEvent",
            "id": "r3-130-2025100566861",
            "name": "みんなのうた「おったまげったん」／「かくれんぼの達人」",
            "description": "",
            "startDate": "2025-10-05T15:50:00+09:00",
            "endDate": "2025-10-05T15:55:00+09:00",
            "location": {
                "id": "001",
                "name": "東京"
            },
            "identifierGroup": {
                "broadcastEventId": "r3-130-2025100566861",
                "radioEpisodeId": "ZZRW3Q4LP9",
                "radioEpisodeName": "「おったまげったん」/「かくれんぼの達人」",
                "radioSeriesId": "GPVXV8GJ9V",
                "radioSeriesName": "みんなのうた （R1 R2 FM）",
                "serviceId": "r3",
                "areaId": "130",
                "stationId": "001",
                "date": "2025-10-05",
                "eventId": "66861",
                "genre": [
                    {
                        "id": "0400",
                        "name1": "音楽",
                        "name2": "国内ロック・ポップス"
                    },
                    {
                        "id": "0409",
                        "name1": "音楽",
                        "name2": "童謡・キッズ"
                    },
                    {
                        "id": "0504",
                        "name1": "バラエティ",
                        "name2": "音楽バラエティ"
                    }
                ]
            },
            "misc": {
                "displayVideoMode": "none",
                "displayVideoRange": "sdr",
                "displayAudioMode": [],
                "audioMode": [],
                "supportCaption": false,
                "supportSign": false,
                "supportHybridcast": false,
                "supportDataBroadcast": false,
                "isInteractive": false,
                "isChangeable": false,
                "releaseLevel": "normal",
                "programType": "program",
                "coverage": "nationwide",
                "actList": [],
                "musicList": [],
                "eventShareStatus": "single",
                "playControlSimul": true
            },
            "url": "https://api.nhk.jp/r7/t/broadcastevent/be/r3-130-2025100566861.json",
            "about": {
                "id": "ZZRW3Q4LP9",
                "name": "「おったまげったん」/「かくれんぼの達人」",
                "identifierGroup": {
                    "radioEpisodeId": "ZZRW3Q4LP9",
                    "radioSeriesId": "GPVXV8GJ9V",
                    "radioEpisodeName": "「おったまげったん」/「かくれんぼの達人」",
                    "radioSeriesName": "みんなのうた （R1 R2 FM）",
                    "hashtag": [],
                    "formatGenreTag": [
                        {
                            "id": "05",
                            "name": "バラエティ"
                        }
                    ],
                    "themeGenreTag": [
                        {
                            "id": "071",
                            "name": "国内ポップス"
                        },
                        {
                            "id": "077",
                            "name": "キッズ音楽"
                        },
                        {
                            "id": "070",
                            "name": "音楽全般"
                        }
                    ]
                },
                "keyword": [],
                "description": "",
                "partOfSeries": {
                    "id": "GPVXV8GJ9V",
                    "name": "みんなのうた （R1 R2 FM）",
                    "detailedSeriesNameRuby": "みんなのうた　あーるわん　あーるつー　えふえむ",
                    "identifierGroup": {
                        "radioSeriesId": "GPVXV8GJ9V",
                        "radioSeriesPlaylistId": "series-rep-GPVXV8GJ9V",
                        "radioSeriesUId": "7c78079e-d869-5dcd-9621-69f4bc0f3127",
                        "radioSeriesName": "みんなのうた （R1 R2 FM）",
                        "hashtag": [],
                        "themeGenre": [
                            {
                                "id": "070",
                                "name": "音楽全般"
                            }
                        ]
                    },
                    "keyword": [],
                    "detailedSynonym": [],
                    "sameAs": [],
                    "canonical": "https://www.nhk.jp/p/rs/GPVXV8GJ9V/",
                    "description": "「みんなのうた」はNHKのテレビ・ラジオで放送されている5分間の音楽番組。「こどもたちに明るい健康な歌をとどけたい」というコンセプトで、１９６１年４月３日に放送をスタートしました。昭和、平成、令和・・・時代とともに、これまでお送りしてきた楽曲（うた）は、およそ１６００曲。\nこれからも２ヶ月ごとに４曲ほどの新たな楽曲、さらに懐かしい名曲たちもたっぷりお届けします。",
                    "detailedCatch": "ラジオ（ラジオ第１・第２、NHK-FM）の放送情報をお届けします",
                    "logo": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_57226883daf0c7cc5b940da5330d0420.jpg",
                            "width": 1080,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_dfd3cb138345821ffdffb6e2591f2898.jpg",
                            "width": 640,
                            "height": 640
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-logo_d697ff3a73ca93916e7fe31d5ec5b261.jpg",
                            "width": 200,
                            "height": 200
                        }
                    },
                    "eyecatch": {
                        "large": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_df8aa9b18845de8661ef6fe911696c0e.jpg",
                            "width": 3840,
                            "height": 2160
                        },
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_83d3405716a8acd1518794b80dccbc47.jpg",
                            "width": 1920,
                            "height": 1080
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_5fed05c55b50c98f53cd7e9a972bddf2.jpg",
                            "width": 1280,
                            "height": 720
                        },
                        "small": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-eyecatch_4e045f1fe08e57beb7212b6474f14e48.jpg",
                            "width": 640,
                            "height": 360
                        }
                    },
                    "hero": {
                        "main": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-hero_3c1181bd7c8e3792abe6bb7a9bfe653d.jpg",
                            "width": 1920,
                            "height": 640
                        },
                        "medium": {
                            "url": "https://img.nhk.jp/static/assets/images/radioseries/rs/GPVXV8GJ9V/GPVXV8GJ9V-hero_6cfce4be1bf01cddfa01c5933e5cc477.jpg",
                            "width": 1080,
                            "height": 360
                        }
                    },
                    "style": {
                        "textLight": "#000000",
                        "textDark": "#FFFFFF",
                        "linkLight": "#990099",
                        "linkDark": "#C062C0",
                        "primaryLight": "#990099",
                        "primaryDark": "#AD32AD"
                    },
                    "additionalProperty": {
                        "publishLevel": "full",
                        "layoutPattern": "summary",
                        "episodeOrderBy": "releasedEvent",
                        "availableOnPlus": false,
                        "enableVariablePlayBackSpeedControl": false,
                        "optional": [],
                        "seriesPackStatus": "notPacked",
                        "supportMedia": [
                            "@screen"
                        ],
                        "supportMusicList": true,
                        "supportPlusEmbed": true
                    },
                    "url": "https://api.nhk.jp/r7/t/radioseries/rs/GPVXV8GJ9V.json",
                    "itemUrl": "https://api.nhk.jp/r7/l/radioepisode/rs/GPVXV8GJ9V.json?order=desc&offset=0&size=10"
                },
                "eyecatchList": [],
                "url": "https://api.nhk.jp/r7/t/radioepisode/re/ZZRW3Q4LP9.json",
                "canonical": "https://www.nhk.jp/p/rs/GPVXV8GJ9V/episode/re/ZZRW3Q4LP9/",
                "additionalProperty": {},
                "audio": []
            },
            "isLiveBroadcast": false,
            "detailedDescription": {
                "epg40": "みんなのうた「おったまげったん」／「かくれんぼの達人」",
                "epg80": "",
                "epgInformation": "",
                "epg200": ""
            },
            "duration": "PT5M",
            "posterframeList": []
        },
        "publishedOn": {
            "type": "BroadcastService",
            "id": "bs-r3-130",
            "name": "NHK FM放送",
            "url": "https://api.nhk.jp/r7/t/broadcastservice/bs/r3-130.json",
            "broadcastDisplayName": "NHK FM・東京",
            "videoFormat": [],
            "encodingFormat": [
                "audio/aac"
            ],
            "identifierGroup": {
                "serviceId": "r3",
                "serviceName": "NHK FM",
                "areaId": "130",
                "areaName": "東京",
                "channelId": null,
                "channelKey": null,
                "channelAreaName": "東京",
                "channelStationName": "首都圏",
                "shortenedName": "NHK FM",
                "shortenedDisplayName": "NHK FM",
                "multiChannelDisplayName": null
            },
            "logo": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-logo.svg",
                    "width": 1080,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-logo.svg",
                    "width": 640,
                    "height": 640
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-logo.svg",
                    "width": 200,
                    "height": 200
                }
            },
            "eyecatch": {
                "large": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-eyecatch.svg",
                    "width": 3840,
                    "height": 2160
                },
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-eyecatch.svg",
                    "width": 1920,
                    "height": 1080
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-eyecatch.svg",
                    "width": 640,
                    "height": 360
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-eyecatch.svg",
                    "width": 320,
                    "height": 180
                }
            },
            "hero": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-hero.svg",
                    "width": 1920,
                    "height": 640
                },
                "medium": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-hero.svg",
                    "width": 1080,
                    "height": 360
                }
            },
            "badge9x4": {
                "main": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-badge9x4.svg",
                    "width": 180,
                    "height": 80
                },
                "small": {
                    "url": "https://img.nhk.jp/common/broadcastservice/bs/r3/r3-badge9x4.svg",
                    "width": 90,
                    "height": 40
                }
            }
        }
    }
}
'''