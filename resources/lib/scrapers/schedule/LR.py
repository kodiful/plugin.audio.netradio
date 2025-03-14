# -*- coding: utf-8 -*-

import urllib.parse
from datetime import datetime, timedelta
from xmltodict import parse

from resources.lib.scrapers.schedule.common import Common


class Scraper(Common):

    PROTOCOL = 'LR'
    URL = 'https://listenradio.jp/Home/ProgramSchedule/{key}/{station}?X-Requested-With=XMLHttpRequest'

    def __init__(self, sid):
        super().__init__(f'{self.PROTOCOL}/{sid}')
        self.sid = sid
        self.db.cursor.execute('SELECT station, key, region, pref, site FROM stations WHERE sid = :sid', {'sid': sid})
        self.station, self.key, self.region, self.pref, self.site = self.db.cursor.fetchone()
        self.URL = self.URL.format(key=self.key, station=urllib.parse.quote(self.station))

    def parse(self, data):
        # xmlを辞書化
        parsed_xml = parse(data)
        # ttPage01->ttListセクションのデータを取得
        ttlist = parsed_xml['div']['div']['div']['div'][1]['div'][0]
        # 日付
        year = datetime.now().year
        month = datetime.now().month
        day = int(ttlist['h2']['span']['#text'])
        # 番組情報
        buf = []
        parentNode = ttlist['div']['ul']['li'] if isinstance(ttlist['div']['ul']['li'], list) else [ttlist['div']['ul']['li']]
        for li in parentNode:
            archive = li['div'][0] if isinstance(li['div'], list) else li['div']
            start, end = archive['p'][0]['#text'].split('-')  # 07:30-10:00
            start = f'{year:04d}-{month:02d}-{day:02d} {start}:00'
            end = f'{year:04d}-{month:02d}-{day:02d} {end}:00'
            title = archive['p'][2].get('#text', '')
            desc = archive['p'][3].get('#text', '')
            # startとendの日時が前後するときはendの日付を修正
            if start >= end:
                dt = self.datetime(end) + timedelta(days=1)  # 1日後に修正
                end = dt.strftime("%Y-%m-%d %H:%M:%S")
            prog = {
                'station': self.station,
                'protocol': self.PROTOCOL,
                'key': self.key,
                'title': self.normalize(title, unescape=True),
                'start': start,
                'end': end,
                'act': '',
                'info': '',
                'desc': self.normalize(desc, unescape=True),
                'site': self.site,
                'region': self.region,
                'pref': self.pref
            }
            buf.append(prog)
        return buf


# https://listenradio.jp/Home/ProgramSchedule/30058/FM%20ABASHIRI?X-Requested-With=XMLHttpRequest

'''
<div id="idx">
<div id="contentMain" class="col3 clearfix">
<div id="schedule">
<div class="ttHead">
    <p class="channelName">
        FM ABASHIRI
    </p>
<!--
    <p class="twitterUserName">
                <script type="text/javascript" src="http://platform.twitter.com/widgets.js" charset="utf-8"></script>
        <a href="https://twitter.com/ListenRadio_058" class="twitter-follow-button" data-show-count="false" data-lang="ja" data-dnt="true">ListenRadio_058 さんをフォロー</a>
    </p>
-->
    <a href="/" class="scheduleIcon TopLink" id="returnIndex" >
        <div class="ttClose">
            <img src="/Content/img/tt_close_btn.gif" width="26" height="26" alt="閉じる" />
        </div>
    </a>
    <p id="next" class="paginate">
        次の3件を見る
    </p>
</div>
<!-- ttHead -->
<div id="ttPage01">
        <div class="ttList sectionWrap">
            <h2 class="tue">
                <span class="date">11</span>
            </h2>
            <div class="list1 section">
                <ul class="innerList">
                        <li id="17032283">
                            <div class="archive">
                                <p class="time">00:00-07:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032284">
                            <div class="archive">
                                <p class="time">07:30-10:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Have a good Day !</p>
                                <p class="sum">朝番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032285">
                            <div class="archive">
                                <p class="time">10:00-11:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">竹屋真征の火曜１０時の偏見の塊</p>
                                <p class="sum">竹屋真征がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032286">
                            <div class="archive">
                                <p class="time">11:00-11:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組（再放送）</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032287">
                            <div class="archive">
                                <p class="time">11:30-15:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Break time Abashiri</p>
                                <p class="sum">昼番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032288">
                            <div class="archive">
                                <p class="time">15:00-15:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032289">
                            <div class="archive">
                                <p class="time">15:30-16:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">LIAミュージック</p>
                                <p class="sum">リスナーからのリクエストをお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032290">
                            <div class="archive">
                                <p class="time">16:00-17:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032291">
                            <div class="archive">
                                <p class="time">17:00-18:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ラジオでサークル始めてみました！？</p>
                                <p class="sum">東京農業大学オホーツクキャンパスの学生がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032292">
                            <div class="archive">
                                <p class="time">18:00-19:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032293">
                            <div class="archive">
                                <p class="time">19:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
        <div class="ttList sectionWrap">
            <h2 class="wed">
                <span class="date">12</span>
            </h2>
            <div class="list1 section">
                <ul class="innerList">
                        <li id="17032294">
                            <div class="archive">
                                <p class="time">00:00-07:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032295">
                            <div class="archive">
                                <p class="time">07:30-10:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Have a good Day !</p>
                                <p class="sum">朝番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032296">
                            <div class="archive">
                                <p class="time">10:00-11:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">“FP”トモローの“独り言”</p>
                                <p class="sum">トモローさんがお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032297">
                            <div class="archive">
                                <p class="time">11:00-11:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組（再放送）</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032298">
                            <div class="archive">
                                <p class="time">11:30-15:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Break time Abashiri</p>
                                <p class="sum">昼番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032299">
                            <div class="archive">
                                <p class="time">15:00-15:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032300">
                            <div class="archive">
                                <p class="time">15:30-16:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">LIAミュージック</p>
                                <p class="sum">リスナーからのリクエストをお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032301">
                            <div class="archive">
                                <p class="time">16:00-17:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032302">
                            <div class="archive">
                                <p class="time">17:00-18:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ラジオでサークル始めてみました！？</p>
                                <p class="sum">東京農業大学オホーツクキャンパスの学生がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032303">
                            <div class="archive">
                                <p class="time">18:00-19:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032304">
                            <div class="archive">
                                <p class="time">19:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
        <div class="ttList sectionWrap">
            <h2 class="thu">
                <span class="date">13</span>
            </h2>
            <div class="list1 section">
                <ul class="innerList">
                        <li id="17032305">
                            <div class="archive">
                                <p class="time">00:00-07:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032306">
                            <div class="archive">
                                <p class="time">07:30-10:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Have a good Day !</p>
                                <p class="sum">朝番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032307">
                            <div class="archive">
                                <p class="time">10:00-11:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">イシハラモトエの Xing on the Radio?</p>
                                <p class="sum">イシハラモトエがお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032308">
                            <div class="archive">
                                <p class="time">11:00-11:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組（再放送）</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032309">
                            <div class="archive">
                                <p class="time">11:30-15:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Break time Abashiri</p>
                                <p class="sum">昼番組「網走市のニュースと天気」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032310">
                            <div class="archive">
                                <p class="time">15:00-15:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032311">
                            <div class="archive">
                                <p class="time">15:30-16:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">LIAミュージック</p>
                                <p class="sum">リスナーからのリクエストをお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032312">
                            <div class="archive">
                                <p class="time">16:00-17:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032313">
                            <div class="archive">
                                <p class="time">17:00-18:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ラジオでサークル始めてみました！？</p>
                                <p class="sum">東京農業大学オホーツクキャンパスの学生がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032314">
                            <div class="archive">
                                <p class="time">18:00-19:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">パンドRadio</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                        <li id="17032315">
                            <div class="archive">
                                <p class="time">19:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
</div>
<!-- ttPage01 -->
<div id="ttPage02">
        <div class="ttList sectionWrap">
            <h2 class="fri">
                <span class="date">14</span>
            </h2>
            <div class="list4 section">
                <ul class="innerList">
                        <li id="17032316">
                            <div class="archive">
                                <p class="time">00:00-07:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032317">
                            <div class="archive">
                                <p class="time">07:30-10:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">スカイ定期便～本日は晴天なり～</p>
                                <p class="sum">ボイスオブオホーツクスカイがお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032318">
                            <div class="archive">
                                <p class="time">10:00-10:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">あおぞら歌謡曲</p>
                                <p class="sum">歌謡曲が黄金時代だった昭和の懐メロをたっぷりお届けする３０分 　あぶかわなおひろが札幌のスタジオからお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032319">
                            <div class="archive">
                                <p class="time">10:30-11:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">湊恵行のGreatest Covers</p>
                                <p class="sum">名曲のオリジナルバージョンとカバーバージョンをご紹介</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032320">
                            <div class="archive">
                                <p class="time">11:00-11:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組（再放送）</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032321">
                            <div class="archive">
                                <p class="time">11:30-12:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">エイジおじさんのためになるラジオ。ためラジ!</p>
                                <p class="sum">山下英二と山崎ひとみがお送りする大空町情報満載の番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032322">
                            <div class="archive">
                                <p class="time">12:00-15:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">FRIDAY　JUNCTION</p>
                                <p class="sum">伊藤ゆりかがお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032323">
                            <div class="archive">
                                <p class="time">15:00-15:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">日替わりパーソナリティ番組</p>
                                <p class="sum">日替わりパーソナリティがお送りします！</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032324">
                            <div class="archive">
                                <p class="time">15:30-16:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">LIAミュージック</p>
                                <p class="sum">リスナーからのリクエストをお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032325">
                            <div class="archive">
                                <p class="time">16:00-17:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">なにはともあれ金曜日</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032326">
                            <div class="archive">
                                <p class="time">17:00-18:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ラジオでサークル始めてみました！？</p>
                                <p class="sum">東京農業大学オホーツクキャンパスの学生がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032327">
                            <div class="archive">
                                <p class="time">18:00-19:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">なにはともあれ金曜日</p>
                                <p class="sum">夕番組「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032328">
                            <div class="archive">
                                <p class="time">19:00-20:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">大山慎介の「復活北海道」</p>
                                <p class="sum">大山慎介がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032329">
                            <div class="archive">
                                <p class="time">20:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
        <div class="ttList sectionWrap">
            <h2 class="sat">
                <span class="date">15</span>
            </h2>
            <div class="list4 section">
                <ul class="innerList">
                        <li id="17032330">
                            <div class="archive">
                                <p class="time">00:00-08:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032331">
                            <div class="archive">
                                <p class="time">08:00-09:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">大山慎介の「復活北海道」（再）</p>
                                <p class="sum">大山慎介がお送りする番組</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032332">
                            <div class="archive">
                                <p class="time">09:00-10:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ＦＭあばしり再放送 / （最終週）9:00あおぞら歌謡曲 9:30 ラジオしょうねん団</p>
                                <p class="sum">再放送をお送りします / （最終週）9:00　歌謡曲が黄金時代だった昭和の懐メロをたっぷりお届けする３０分 / （最終週）9:30　講談師「神田山陽」とオホーツクの子どもたちによるラジオを通じた課外活</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032333">
                            <div class="archive">
                                <p class="time">10:00-14:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">Peaceful SATURDAY</p>
                                <p class="sum">「網走市情報、各種コーナー」</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032334">
                            <div class="archive">
                                <p class="time">14:00-14:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">あおぞら歌謡曲（再） / （最終週）走裕介のデレスケラジオ</p>
                                <p class="sum">歌謡曲が黄金時代だった昭和の懐メロをたっぷりお届けする３０分 / （最終週）オホーツク出身の演歌歌手「走裕介」の近況や最新情報をお届けする番組 　あぶかわなおひろが札幌のスタジオからお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032335">
                            <div class="archive">
                                <p class="time">14:30-15:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">湊恵行のGreatest Covers（再）</p>
                                <p class="sum">名曲のオリジナルバージョンとカバーバージョンをご紹介</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032336">
                            <div class="archive">
                                <p class="time">15:00-15:30</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">（第一、第三土曜）伊藤ゆりかのなんてったってアイドル☆/（第二、第四土曜）あに愛でRoom（第五土曜</p>
                                <p class="sum">（第一、第三土曜）アイドルソング番組 /（第二、第四土曜）アニメソング番組 / （第五土曜）ゲストの好きな曲をランキングで紹介</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032337">
                            <div class="archive">
                                <p class="time">15:30-16:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">（第一、第三土曜）ふるさと一貫！へいらっしゃい！！/（第二、第四土曜）うぇるかむ創成塾！（第五土曜）</p>
                                <p class="sum">（第一、第三土曜）大学生の三浦雄大がお送りする番組/（第二、第四土曜）会員の取り組みや、 ?製品紹介、学びの情報などを交えた地域をHappyにする情報番組 / （第五土曜）大空高校の生徒たちが学校生活</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032338">
                            <div class="archive">
                                <p class="time">16:00-17:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ＦＭあばしり再放送</p>
                                <p class="sum">再放送をお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032339">
                            <div class="archive">
                                <p class="time">17:00-18:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">(再)ラジオでサークル始めてみました！？</p>
                                <p class="sum">再放送をお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032340">
                            <div class="archive">
                                <p class="time">18:00-19:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">(再)リハラジ</p>
                                <p class="sum">再放送をお送りします</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                        <li id="17032341">
                            <div class="archive">
                                <p class="time">19:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
        <div class="ttList sectionWrap">
            <h2 class="sun">
                <span class="date">16</span>
            </h2>
            <div class="list4 section">
                <ul class="innerList">
                        <li id="17032342">
                            <div class="archive">
                                <p class="time">00:00-00:00</p>
                                <p class="channelnm">FM ABASHIRI</p>
                                <p class="title">ミュージックバード</p>
                                <p class="sum">-</p>
                            </div>
                                <div class="showList">
                                    放送楽曲を表示</div>
                                <ul class="playingList">
                                j
                                </ul>
                        </li>
                </ul>
                <!-- innerList -->
            </div>
            <!-- section -->
        </div>
        <!-- ttList -->
</div>
<!-- ttPage02 -->
</div>
</div>
</div>
'''