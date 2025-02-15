# -*- coding: utf-8 -*-

import json

from resources.lib.schedulescrapers.common import Common


class Scraper(Common):

    PROTOCOL = 'SP'
    URL = 'https://%s.fmplapla.com/api/timetable'

    def __init__(self, sid):
        super().__init__(f'{self.PROTOCOL}/{sid}')
        self.sid = sid
        self.db.cursor.execute('SELECT station, key, region, pref, site FROM stations WHERE sid = :sid', {'sid': sid})
        self.station, self.key, self.region, self.pref, self.site = self.db.cursor.fetchone()
        self.URL = self.URL % self.key

    def parse(self, data):
        data = json.loads(data)
        buf = []
        for item in data:
            prog = {
                'station': self.station,
                'protocol': self.PROTOCOL,
                'key': self.key,
                'title': self.normalize(item['title']),
                'start': self._datetime(item['start']),
                'end': self._datetime(item['end']),
                'act': item.get('performer', ''),
                'info': item.get('sub_title', ''),
                'desc': '',
                'site': self.site,
                'region': self.region,
                'pref': self.pref
            }
            buf.append(prog)
        return buf

    def _datetime(self, t):
        # 2025-02-11T13:00:00+09:00 -> 2025-02-11 13:00:00
        return t[0:10] + ' ' + t[11:19]  # タイムゾーン情報を除外してフォーマット


# https://kanazawaseasidefm.fmplapla.com/api/schedule

'''
[{
    "id": 83579,
    "title": "カナラジ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-12T09:00:00+09:00",
    "end": "2025-02-12T11:00:00+09:00"
}, {
    "id": 83580,
    "title": "ひるカナ！！",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-12T11:00:00+09:00",
    "end": "2025-02-12T13:00:00+09:00"
}, {
    "id": 83581,
    "title": "MEDICAL CENTER Dr.鳥居の心とカラダのSDGs",
    "sub_title": "提供:医療法人社団　湘南太陽会",
    "performer": "",
    "start": "2025-02-12T13:00:00+09:00",
    "end": "2025-02-12T14:00:00+09:00"
}, {
    "id": 83582,
    "title": "やまだようじの横浜金沢いきもの図鑑",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-12T14:00:00+09:00",
    "end": "2025-02-12T15:00:00+09:00"
}, {
    "id": 83583,
    "title": "Love＆Peace by BlooMee",
    "sub_title": "提供:有限会社オートトレーディングロック",
    "performer": "",
    "start": "2025-02-12T15:00:00+09:00",
    "end": "2025-02-12T16:00:00+09:00"
}, {
    "id": 83584,
    "title": "第3週：横高ナビ",
    "sub_title": "提供：横浜高校",
    "performer": "他シーサイドカフェ",
    "start": "2025-02-12T16:00:00+09:00",
    "end": "2025-02-12T17:00:00+09:00"
}, {
    "id": 83585,
    "title": "第２週：パラスポーツをもっと身近に！パラステ",
    "sub_title": "他シーサイドSHOW",
    "performer": "",
    "start": "2025-02-12T17:00:00+09:00",
    "end": "2025-02-12T18:00:00+09:00"
}, {
    "id": 83586,
    "title": "話のネタになるラジオ ネタラジ委員会",
    "sub_title": "関東学院大学伊藤ゼミ",
    "performer": "",
    "start": "2025-02-12T18:00:00+09:00",
    "end": "2025-02-12T19:00:00+09:00"
}, {
    "id": 83587,
    "title": "第３週:Umiの湯ラジオ、提供:よこはまの森洗剤",
    "sub_title": "他よるかな",
    "performer": "",
    "start": "2025-02-12T19:00:00+09:00",
    "end": "2025-02-12T20:00:00+09:00"
}, {
    "id": 83588,
    "title": "カナラジ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-13T09:00:00+09:00",
    "end": "2025-02-13T11:00:00+09:00"
}, {
    "id": 83589,
    "title": "ひるカナ！！",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-13T11:00:00+09:00",
    "end": "2025-02-13T12:00:00+09:00"
}, {
    "id": 83590,
    "title": "第４週：ネクストステップナビ～社会保険の基礎知識～",
    "sub_title": "他ひるかな",
    "performer": "",
    "start": "2025-02-13T12:00:00+09:00",
    "end": "2025-02-13T13:00:00+09:00"
}, {
    "id": 83591,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-13T13:00:00+09:00",
    "end": "2025-02-13T14:00:00+09:00"
}, {
    "id": 83592,
    "title": "第４週：文化の懸け橋、提供:相鉄企業株式会社",
    "sub_title": "他シーサイド・カフェ",
    "performer": "",
    "start": "2025-02-13T14:00:00+09:00",
    "end": "2025-02-13T16:00:00+09:00"
}, {
    "id": 83593,
    "title": "未来を紡ぐ「Unsung Hero」",
    "sub_title": "提供:ヨコオペ株式会社",
    "performer": "",
    "start": "2025-02-13T16:00:00+09:00",
    "end": "2025-02-13T17:00:00+09:00"
}, {
    "id": 83594,
    "title": "シーサイドSHOW",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-13T17:00:00+09:00",
    "end": "2025-02-13T18:00:00+09:00"
}, {
    "id": 83595,
    "title": "サムライクルーザーの人生やったもん勝ち！",
    "sub_title": "提供:SAMURAI CRUISER project",
    "performer": "",
    "start": "2025-02-13T18:00:00+09:00",
    "end": "2025-02-13T19:00:00+09:00"
}, {
    "id": 83596,
    "title": "野口総業presents 俺のガレージ",
    "sub_title": "提供:株式会社野口総業",
    "performer": "",
    "start": "2025-02-13T19:00:00+09:00",
    "end": "2025-02-13T20:00:00+09:00"
}, {
    "id": 83597,
    "title": "カナラジ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T09:00:00+09:00",
    "end": "2025-02-14T11:00:00+09:00"
}, {
    "id": 83598,
    "title": "ひるカナ！！",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T11:00:00+09:00",
    "end": "2025-02-14T12:00:00+09:00"
}, {
    "id": 83599,
    "title": "整体師コタローのためになる話",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T12:00:00+09:00",
    "end": "2025-02-14T13:00:00+09:00"
}, {
    "id": 83600,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T13:00:00+09:00",
    "end": "2025-02-14T17:00:00+09:00"
}, {
    "id": 83601,
    "title": "自助カナ!!",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T17:00:00+09:00",
    "end": "2025-02-14T18:00:00+09:00"
}, {
    "id": 83602,
    "title": "シーサイドSHOW",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-14T18:00:00+09:00",
    "end": "2025-02-14T19:00:00+09:00"
}, {
    "id": 83603,
    "title": "第３週Treasure Gardenの華金RADIO",
    "sub_title": "第４週：トライな企画",
    "performer": "他よるかな",
    "start": "2025-02-14T19:00:00+09:00",
    "end": "2025-02-14T20:00:00+09:00"
}, {
    "id": 83604,
    "title": "「食」のストーリー",
    "sub_title": "提供:横浜テクノタワーホテル",
    "performer": "",
    "start": "2025-02-15T09:00:00+09:00",
    "end": "2025-02-15T10:00:00+09:00"
}, {
    "id": 83605,
    "title": "サタカナ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T10:00:00+09:00",
    "end": "2025-02-15T11:00:00+09:00"
}, {
    "id": 83606,
    "title": "ひるカナSaturday",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T11:00:00+09:00",
    "end": "2025-02-15T12:00:00+09:00"
}, {
    "id": 83607,
    "title": "こころのチカラ",
    "sub_title": "提供:株式会社こころ・焼肉 韓太樓",
    "performer": "",
    "start": "2025-02-15T12:00:00+09:00",
    "end": "2025-02-15T13:00:00+09:00"
}, {
    "id": 83608,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T13:00:00+09:00",
    "end": "2025-02-15T14:00:00+09:00"
}, {
    "id": 83609,
    "title": "∼Kakuchino（各地の）∼ presented by 岡本裕二",
    "sub_title": "提供:有限会社大藤工業/株式会社ツチヤ工業/AI GOLF.TOKYO/TAMATEBOX",
    "performer": "",
    "start": "2025-02-15T14:00:00+09:00",
    "end": "2025-02-15T15:00:00+09:00"
}, {
    "id": 83610,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T15:00:00+09:00",
    "end": "2025-02-15T16:00:00+09:00"
}, {
    "id": 83611,
    "title": "株式会社HAMONIプレゼンツ、金沢シーサイドグルメジャーニー",
    "sub_title": "提供:株式会社HAMONI",
    "performer": "",
    "start": "2025-02-15T16:00:00+09:00",
    "end": "2025-02-15T17:00:00+09:00"
}, {
    "id": 83612,
    "title": "かなざワイド",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T17:00:00+09:00",
    "end": "2025-02-15T18:00:00+09:00"
}, {
    "id": 83613,
    "title": "歌謡曲だよ、人生は。",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T18:00:00+09:00",
    "end": "2025-02-15T19:00:00+09:00"
}, {
    "id": 83614,
    "title": "よるかな",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-15T19:00:00+09:00",
    "end": "2025-02-15T20:00:00+09:00"
}, {
    "id": 83615,
    "title": "9:00～9:10 安保先生のワンポイント健康講座",
    "sub_title": "提供:有限会社アンポ接骨院",
    "performer": "9:11∼シーサイドサンデー",
    "start": "2025-02-16T09:00:00+09:00",
    "end": "2025-02-16T10:00:00+09:00"
}, {
    "id": 83616,
    "title": "KANAZAWA SEASIDE LIVE SHOW",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-16T10:00:00+09:00",
    "end": "2025-02-16T11:00:00+09:00"
}, {
    "id": 83617,
    "title": "ひるカナSunday",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-16T11:00:00+09:00",
    "end": "2025-02-16T13:00:00+09:00"
}, {
    "id": 83618,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-16T13:00:00+09:00",
    "end": "2025-02-16T16:00:00+09:00"
}, {
    "id": 83619,
    "title": "株式会社HAMONIプレゼンツ、金沢シーサイドグルメジャーニー",
    "sub_title": "提供:株式会社HAMONI",
    "performer": "",
    "start": "2025-02-16T16:00:00+09:00",
    "end": "2025-02-16T17:00:00+09:00"
}, {
    "id": 83620,
    "title": "かなざワイド",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-16T17:00:00+09:00",
    "end": "2025-02-16T18:00:00+09:00"
}, {
    "id": 83621,
    "title": "リクエストナイト",
    "sub_title": "提供:micグループ株式会社三春情報センター",
    "performer": "",
    "start": "2025-02-16T18:00:00+09:00",
    "end": "2025-02-16T20:00:00+09:00"
}, {
    "id": 83622,
    "title": "カナラジ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-17T09:00:00+09:00",
    "end": "2025-02-17T10:00:00+09:00"
}, {
    "id": 83623,
    "title": "第２週：ママ夢ラジオ横浜金沢",
    "sub_title": "提供:一般社団法人日本婚活支援支援機構・他：カナラジ",
    "performer": "",
    "start": "2025-02-17T10:00:00+09:00",
    "end": "2025-02-17T11:00:00+09:00"
}, {
    "id": 83624,
    "title": "横浜金沢魅力発信～石川の金沢じゃない、横浜金沢！～",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-17T11:00:00+09:00",
    "end": "2025-02-17T12:00:00+09:00"
}, {
    "id": 83625,
    "title": "油原興業presentsやらない善より、やる偽善",
    "sub_title": "∼こどものためにできること∼",
    "performer": "提供:株式会社油原興業",
    "start": "2025-02-17T12:00:00+09:00",
    "end": "2025-02-17T13:00:00+09:00"
}, {
    "id": 83626,
    "title": "かなうら",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-17T13:00:00+09:00",
    "end": "2025-02-17T14:00:00+09:00"
}, {
    "id": 83627,
    "title": "第２週：元気なうちに！始める終活",
    "sub_title": "提供:横浜セレモ株式会社",
    "performer": "他シーサイドカフェ",
    "start": "2025-02-17T14:00:00+09:00",
    "end": "2025-02-17T15:00:00+09:00"
}, {
    "id": 83628,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-17T15:00:00+09:00",
    "end": "2025-02-17T17:00:00+09:00"
}, {
    "id": 83629,
    "title": "新・明日も笑和で‼︎",
    "sub_title": "提供:はまかぜ新聞社",
    "performer": "",
    "start": "2025-02-17T17:00:00+09:00",
    "end": "2025-02-17T18:00:00+09:00"
}, {
    "id": 83630,
    "title": "シーサイドSHOW",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-17T18:00:00+09:00",
    "end": "2025-02-17T19:00:00+09:00"
}, {
    "id": 83631,
    "title": "第２週：パパ夢ラジオ横浜",
    "sub_title": "提供:株式会社わたしたち",
    "performer": "他よるかな",
    "start": "2025-02-17T19:00:00+09:00",
    "end": "2025-02-17T20:00:00+09:00"
}, {
    "id": 83632,
    "title": "カナラジ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-18T09:00:00+09:00",
    "end": "2025-02-18T11:00:00+09:00"
}, {
    "id": 83633,
    "title": "ひるカナ！！",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-18T11:00:00+09:00",
    "end": "2025-02-18T13:00:00+09:00"
}, {
    "id": 83634,
    "title": "シーサイド・カフェ",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-18T13:00:00+09:00",
    "end": "2025-02-18T14:00:00+09:00"
}, {
    "id": 83635,
    "title": "第２週：ビューティーアワー提供: hair salon Rich",
    "sub_title": "他シーサイド・カフェ",
    "performer": "",
    "start": "2025-02-18T14:00:00+09:00",
    "end": "2025-02-18T15:00:00+09:00"
}, {
    "id": 83636,
    "title": "スポットライト",
    "sub_title": "提供:Reinvent health株式会社",
    "performer": "",
    "start": "2025-02-18T15:00:00+09:00",
    "end": "2025-02-18T16:00:00+09:00"
}, {
    "id": 83637,
    "title": "通山栞のBookmark of Book 本の栞",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-18T16:00:00+09:00",
    "end": "2025-02-18T17:00:00+09:00"
}, {
    "id": 83638,
    "title": "うみとそらのおうち",
    "sub_title": "提供:株式会社オルフィックデザイン",
    "performer": "",
    "start": "2025-02-18T17:00:00+09:00",
    "end": "2025-02-18T18:00:00+09:00"
}, {
    "id": 83639,
    "title": "シーサイドSHOW",
    "sub_title": "",
    "performer": "",
    "start": "2025-02-18T18:00:00+09:00",
    "end": "2025-02-18T19:00:00+09:00"
}, {
    "id": 83640,
    "title": "Bee Talk",
    "sub_title": "提供:一般社団法人横浜ウーマンズライツ協会/ ぐるっとママ横浜/一般社団法人日本シングルマザー支援協会",
    "performer": "",
    "start": "2025-02-18T19:00:00+09:00",
    "end": "2025-02-18T20:00:00+09:00"
}]
'''