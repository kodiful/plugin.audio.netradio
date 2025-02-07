# -*- coding: utf-8 -*-

import datetime
from xmltodict import parse

from resources.lib.timetable.common import Common
from resources.lib.db import DB


class Scraper(Common):

    TYPE = 'radk'
    #URL = 'http://radiko.jp/v2/api/program/now?area_id=%s'  # v2
    URL = 'https://radiko.jp/v3/program/now/{pref}.xml'  # v3

    def __init__(self, region, pref):
        super().__init__()
        db = DB()
        self.region = region
        self.pref = pref
        item = db.search_by_pref(pref)
        self.URL = self.URL.format(pref=item['radiko'])
        db.conn.close()

    def parse(self, data):
        data = parse(data)
        buf = []
        for s in data['radiko']['stations']['station']:
            station = self.normalize(s['name'])
            id = s['@id']
            progs = []
            #for p in s['scd']['progs']['prog']:  # v2
            proglist = s['progs']['prog']
            if type(proglist) == 'dict': proglist = [proglist]  # 1番組だけのときはdictなのでlist化する
            for p in proglist:  # v3
                '''
                v2:
                <prog ft="20230420050000" to="20230420063000" ftl="0500" tol="0630" dur="5400">
                    <title>生島ヒロシのおはよう定食・一直線</title>
                    <sub_title />
                    <imgs>
                    <img src="3995" type="" />
                    </imgs>
                    <pfm>生島ヒロシ　ゲスト：小田貴月 / 石原結實（イシハラクリニック院長）</pfm>
                    <desc />
                    <info>健康情報、最新ニュースなど、情報満載でお送りします。</info>
                    <metas>
                        <meta name="twitter" value="#radiko" />
                        <meta name="twitter-hash" value="#radiko" />
                        <meta name="facebook-fanpage" value="http://www.facebook.com/radiko.jp" />
                    </metas>
                    <url>https://www.tbsradio.jp/ohayou/</url>
                </prog>
                '''
                '''
                v3:
                <prog id="10003448874" master_id="" ft="20231110120000" to="20231110140000" ftl="1200" tol="1400" dur="7200">
                    <title>金曜ボイスログ (3)</title>
                    <url>https://www.tbsradio.jp/vl/</url>
                    <url_link>https://www.tbsradio.jp/vl/?x11=_(radiko-uid)</url_link>
                    <failed_record>0</failed_record>
                    <ts_in_ng>0</ts_in_ng>
                    <ts_out_ng>0</ts_out_ng>
                    <desc></desc>
                    <info>「あなたのレビューがラジオになる」をモットーに、あなたの愛するもの・ことをレビューしまくるラジオ番組。</info>
                    <pfm>臼井ミトン　ゲスト：柳生九兵衛</pfm>
                    <img>https://radiko.jp/res/program/DEFAULT_IMAGE/TBS/aiu147chgm.jpg</img>
                    <tag><item><name>臼井ミトン</name></item><item><name>音楽との出会いが楽しめる</name></item><item><name>人気アーティストトーク</name></item><item><name>作業がはかどる</name></item></tag>
                    <genre><personality id="C010"><name>タレント</name></personality><program id="P006"><name>バラエティ</name></program></genre>
                    <metas>
                        <meta name="twitter" value="#radiko" />
                    </metas>
                </prog>
                '''
                prog = {
                    'station': station,
                    'type': 'radk',
                    'abbr': id,
                    'title': self.normalize(p['title']),
                    'start': self._datetime(p['@ft']),
                    'end': self._datetime(p['@to']),
                    'act': self.normalize(p['pfm']),
                    'info': self.normalize(p['info']),
                    'desc': self.normalize(p['desc']),
                    'site': p['url'],
                    'region': self.region,
                    'pref': self.pref
                }
                progs.append(prog)
            buf += progs
        return buf

    def _datetime(self, t):
        # 20231110120000 -> 2023-11-10 12:00:00
        datetime_obj = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
