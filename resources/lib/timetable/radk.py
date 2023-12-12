# -*- coding: utf-8 -*-

import sys
import os
import datetime
import requests
from xmltodict import parse

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

    TYPE = 'radk'
    #URL = 'http://radiko.jp/v2/api/program/now?area_id=%s'  # v2
    URL = 'https://radiko.jp/v3/program/now/%s.xml'  # v3

    def __init__(self, pref):
        item = self.search_by_pref(pref)
        self.URL = self.URL % item['radiko']
        super().__init__()
    
    def parse(self, data):
        data = parse(data)
        buf = {}
        for s in data['radiko']['stations']['station']:
            station = self.normalize(s['name'])
            id_ = s['@id']
            progs = []
            #for p in s['scd']['progs']['prog']:  # v2
            progs = s['progs']['prog']
            if type(progs) == 'dict': progs = [progs]  # 1番組だけのときはdictなのでlist化する
            for p in progs:  # v3
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
                progs.append({
                    'type': 'radk',
                    'id': id_,
                    'station': station,
                    'title': self.normalize(p['title']),
                    'START': p['@ft'],  # 20201027000000
                    'END': p['@to'],  # 20201027005300
                    'start': self.t2unixtime(p['@ft']),  # 20201027000000
                    'end': self.t2unixtime(p['@to']),  # 20201027005300
                    'weekday': self.t2weekday(p['@ft']),
                    'act': self.normalize(p['pfm']),
                    'info': self.normalize(p['info']),
                    'desc': self.normalize(p['desc']),
                    'url': p['url'],
                })
            buf[station] = progs
        return buf

    def t2unixtime(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
        # UNIX時間に変換
        return int(datetime_obj.timestamp())

    def t2weekday(self, t):
        # datetimeオブジェクトに変換
        datetime_obj = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
        # 曜日の数字に変換
        return str(datetime_obj.weekday())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--pref', default='東京都')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    countdown = Scraper(args.pref).update()
    print(countdown)
