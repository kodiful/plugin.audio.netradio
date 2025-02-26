# -*- coding: utf-8 -*-

from xmltodict import parse

from resources.lib.scrapers.schedule.common import Common


class Scraper(Common):

    PROTOCOL = 'RDK'
    URL = 'https://radiko.jp/v3/program/now/{area_id}.xml'

    def __init__(self, sid):
        super().__init__(self.PROTOCOL)
        self.sid = sid
        self.db.cursor.execute('SELECT region, pref FROM stations WHERE sid = :sid', {'sid': sid})
        self.region, self.pref = self.db.cursor.fetchone()
        area_id = self.db.search_by_pref(self.pref)
        self.URL = self.URL.format(area_id=area_id)

    def parse(self, data):
        data = parse(data)
        buf = []
        for s in data['radiko']['stations']['station']:
            station = self.normalize(s['name'])
            id = s['@id']
            progs = []
            proglist = s['progs']['prog']
            if type(proglist) == 'dict': proglist = [proglist]  # 1番組だけのときはdictなのでlist化する
            for p in proglist:
                title = p['title']
                start = p['@ft']
                end = p['@to']
                act = p['pfm']
                info = p['info']
                desc = p['desc']
                prog = {
                    'station': station,
                    'protocol': self.PROTOCOL,
                    'key': id,
                    'title': self.normalize(title),
                    'start': self._datetime(start),
                    'end': self._datetime(end),
                    'act': self.normalize(act),
                    'info': self.normalize(info),
                    'desc': self.normalize(desc),
                    'site': p['url'] or '',
                    'region': self.region,
                    'pref': self.pref
                }
                progs.append(prog)
            buf += progs
        return buf

    def _datetime(self, t):
        # 20231110120000 -> 2023-11-10 12:00:00
        #dt = datetime.strptime(t, '%Y%m%d%H%M%S')
        #return dt.strftime('%Y-%m-%d %H:%M:%S')
        return f'{t[0:4]}-{t[4:6]}-{t[6:8]} {t[8:10]}:{t[10:12]}:{t[12:14]}'

    def get_nextaired(self):
        sql = 'SELECT MIN(nextaired) FROM stations AS s WHERE s.protocol = :protocol AND s.pref = :pref'
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL, 'pref': self.pref})
        nextaired, = self.db.cursor.fetchone()
        return nextaired
    
    def _get_nextaired(self):
        sql = '''
        SELECT MIN(c.end)
        FROM contents AS c JOIN stations AS s ON c.sid = s.sid
        WHERE c.end > NOW() AND s.protocol = :protocol AND s.pref = :pref
        '''
        self.db.cursor.execute(sql, {'protocol': self.PROTOCOL, 'pref': self.pref})
        nextaired, = self.db.cursor.fetchone()
        return nextaired

    def set_nextaired(self):
        sql = '''
        UPDATE stations
        SET nextaired = :nextaired
        WHERE protocol = :protocol AND pref = :pref
        '''
        nextaired = self._get_nextaired()
        self.db.cursor.execute(sql, {'nextaired': nextaired, 'protocol': self.PROTOCOL, 'pref': self.pref})
        return nextaired


# https://radiko.jp/v3/program/now/JP13.xml

'''
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<radiko>
<ttl>300</ttl>
<srvtime>1739326797</srvtime>
<stations>
<station id="TBS">
<name>TBSラジオ</name>
<progs>
<date>20250212</date>
<prog id="11202590" master_id="" ft="20250212110000" to="20250212120000" ftl="1100" tol="1200" dur="3600">
<title>ジェーン・スー 生活は踊る (1)</title>
<url>https://www.tbsradio.jp/so/</url>
<url_link>https://www.tbsradio.jp/so/?x11=_(radiko-uid)</url_link>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info>聴けば日々の生活が潤う、人情・愛情・生活情報をお届けするラジオ。<br> 水曜パートナーはTBSの杉山真也アナウンサー。<br /> <br /> ◆11時台前半　生活情報<br /> <br /> ◆12時　ジェーン・スーがリスナーの悩みを聞く「相談は踊る」<br /> <br /> ◆13時　生活の知恵を授かる「スーさん、コレいいよ！」<br /> 焼き芋アンバサダー・天谷窓大さんによる「焼き芋アレンジ」<br /> <br /> ◆13時台後半　リスナーの皆さんのおすすめ情報を紹介する「スーさん、コレもいいよ！」<br /> <br /> LINEは<a href="https://line.me/R/ti/p/%40996phlct" target="_blank"><u>コチラ！</u></a><br> X（旧Twitter）：<a href="https://twitter.com/seikatsu954905" target="_blank"><u>@seikatsu954905</u></a><br> instagram：<a href="https://www.instagram.com/seikatsu954905" target="_blank"><u>seikatsu954905</u></a><br> facebook：<a href="https://www.facebook.com/seikatsu@954905" target="_blank"><u>@seikatsu954905</u></a><br> メール：<a href="mailto:so@tbs.co.jp"><u>so@tbs.co.jp</u></a><br> 受付FAX番号：03-5562-0954</info>
<pfm>ジェーン・スー / 杉山真也（TBSアナウンサー）　ゲスト：天谷窓大（焼き芋アンバサダー）</pfm>
<img>https://program-static.cf.radiko.jp/bfu2sp43c4.jpg</img>
<tag>
<item>
<name>ジェーン・スー</name>
</item>
<item>
<name>杉山真也</name>
</item>
<item>
<name>生活は踊る</name>
</item>
<item>
<name>誰にも言えないお悩み相談</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P003">
<name>情報</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11202590" master_id="" ft="20250212120000" to="20250212130000" ftl="1200" tol="1300" dur="3600">
<title>ジェーン・スー 生活は踊る (2)</title>
<url>https://www.tbsradio.jp/so/</url>
<url_link>https://www.tbsradio.jp/so/?x11=_(radiko-uid)</url_link>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info>聴けば日々の生活が潤う、人情・愛情・生活情報をお届けするラジオ。<br> 水曜パートナーはTBSの杉山真也アナウンサー。<br /> <br /> ◆11時台前半　生活情報<br /> <br /> ◆12時　ジェーン・スーがリスナーの悩みを聞く「相談は踊る」<br /> <br /> ◆13時　生活の知恵を授かる「スーさん、コレいいよ！」<br /> 焼き芋アンバサダー・天谷窓大さんによる「焼き芋アレンジ」<br /> <br /> ◆13時台後半　リスナーの皆さんのおすすめ情報を紹介する「スーさん、コレもいいよ！」<br /> <br /> LINEは<a href="https://line.me/R/ti/p/%40996phlct" target="_blank"><u>コチラ！</u></a><br> X（旧Twitter）：<a href="https://twitter.com/seikatsu954905" target="_blank"><u>@seikatsu954905</u></a><br> instagram：<a href="https://www.instagram.com/seikatsu954905" target="_blank"><u>seikatsu954905</u></a><br> facebook：<a href="https://www.facebook.com/seikatsu@954905" target="_blank"><u>@seikatsu954905</u></a><br> メール：<a href="mailto:so@tbs.co.jp"><u>so@tbs.co.jp</u></a><br> 受付FAX番号：03-5562-0954</info>
<pfm>ジェーン・スー / 杉山真也（TBSアナウンサー）　ゲスト：天谷窓大（焼き芋アンバサダー）</pfm>
<img>https://program-static.cf.radiko.jp/bfu2sp43c4.jpg</img>
<tag>
<item>
<name>ジェーン・スー</name>
</item>
<item>
<name>杉山真也</name>
</item>
<item>
<name>生活は踊る</name>
</item>
<item>
<name>誰にも言えないお悩み相談</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P003">
<name>情報</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="QRR">
<name>文化放送</name>
<progs>
<date>20250212</date>
<prog id="11188818" master_id="" ft="20250212110000" to="20250212130000" ftl="1100" tol="1300" dur="7200">
<title>くにまる食堂（11：00～13：00）</title>
<url>https://www.joqr.co.jp/qr/program/kunimaru/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc><div>12時台は「北の国から」で1981年の子役時代から22年にわたり黒板蛍役を演じ、お茶の間の人気を博した俳優の中嶋朋子さんがご来店。</div><div>3月7日（金）から出演される舞台「イノック・アーデン」についてお話を伺います。</div><br>◆◆ゲスト情報◆◆<br>12時台：中嶋朋子<br><br>番組メールアドレス：<br><a href="mailto:kunimaru@joqr.net">kunimaru@joqr.net</a><br><br>X（旧Twitter）ハッシュタグは「<a href="https://twitter.com/search?q=%23%E3%81%8F%E3%81%AB%E3%81%BE%E3%82%8B" target="_blank">#くにまる</a>」<br>X（旧Twitter）ページは「<a href="https://twitter.com/kunimaru_joqr" target="_blank">https://twitter.com/kunimaru_joqr</a>」<br><br></desc>
<info><p>リスナーが今気になる政治・経済・エンタメ情報をお届けし、リスナーの意見を紹介する機会を充実させ、”知りたい””言いたい”気持ちに応える場所になります。<br />毎日通ってしまう食堂のように、聞くことが日常の一部になるラジオ番組です。<br />※水曜日9:00～11:00のパートナーは週替わりです。</p><p>金曜日は「くにまる食堂フライデー ～どうした！？一蔵！～」を放送中！<br />▼詳細はこちらから▼<br /><a href="https://www.joqr.co.jp/qr/program/kunimaru_friday/">（「くにまる食堂フライデー ～どうした！？一蔵！～」　https://www.joqr.co.jp/qr/program/kunimaru_friday/）</a></p><br>文化放送公式X（旧Twitter）アカウントは「<a href="https://twitter.com/joqrpr" target="_blank">@joqrpr</a>」<br>文化放送公式X（旧Twitter）ハッシュタグは「<a href="https://twitter.com/search?q=%23%E6%96%87%E5%8C%96%E6%94%BE%E9%80%81" target="_blank">#文化放送</a>」<br>文化放送公式facebookページは<br>「<a href="https://www.facebook.com/1134joqr" target="_blank">https://www.facebook.com/1134joqr</a>」<br>文化放送公式LINEは「<a href="https://page.line.me/joqr_916" target="_blank">@joqr_916</a>」<br></info>
<pfm>野村邦丸、坂口愛美</pfm>
<img>https://program-static.cf.radiko.jp/abxar3fcvx.jpg</img>
<tag>
<item>
<name>文化放送</name>
</item>
<item>
<name>くにまる</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P001">
<name>ニュース/天気/交通</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11188819" master_id="" ft="20250212130000" to="20250212153000" ftl="1300" tol="1530" dur="9000">
<title>大竹まこと ゴールデンラジオ！</title>
<url>https://www.joqr.co.jp/qr/program/golden/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>【パートナー】<br>水谷加奈<br>【13時台レギュラー】<br>いとうあさこ<br>【メインディッシュ】<br>松本創　※zoom<br>【交遊録】<br>きたろう(タレント、俳優)<br>番組メールアドレス：<br><a href="mailto:golden@joqr.net">golden@joqr.net</a><br><br>X（旧Twitter）ページは「<a href="https://twitter.com/1134golden" target="_blank">https://twitter.com/1134golden</a>」<br>facebookページは「<a href="https://www.facebook.com/1134golden/" target="_blank">https://www.facebook.com/1134golden/</a>」<br><br></desc>
<info><p>“面白い”けれど”真剣に”、”くだらない”けれど”正直に”。<br />価値観の急激な変化が迫られている今。<br />様々な歪みが生じ、いろいろな事件、難解な問題が日々起こっています。<br />高齢者対策、団塊の世代の今後、少年犯罪、少子化、・・・、細部では、コミュニケーションから生じる様々な事件、コンプライアンスやモラルの問題、日本のあり方まで。<br />本当に大事なことは、”今”、”時代”に注目してゆき、個人がいろいろな問題に疑問を持ち、考え、行動する事です。<br />「大竹まことゴールデンラジオ！」は、”大竹まこと同世代”を中心に、全世代の男女に向けてお送りします。<br />厳しい時代に、”頑張って生きている人たち”を応援し、番組を通じて楽しいこと、素敵に生きることを提案、日々変化するニュースを扱いながら、エンタテインメントの心を忘れずに、”筋”の通った本気の発言をしてゆきます。</p><p>〒105-8002<br />文化放送 「ゴールデンラジオ」行き</p><p>メールは <a href="mailto:golden@joqr.net">golden@joqr.net</a></p><br>文化放送公式X（旧Twitter）アカウントは「<a href="https://twitter.com/joqrpr" target="_blank">@joqrpr</a>」<br>文化放送公式X（旧Twitter）ハッシュタグは「<a href="https://twitter.com/search?q=%23%E6%96%87%E5%8C%96%E6%94%BE%E9%80%81" target="_blank">#文化放送</a>」<br>文化放送公式facebookページは<br>「<a href="https://www.facebook.com/1134joqr" target="_blank">https://www.facebook.com/1134joqr</a>」<br>文化放送公式LINEは「<a href="https://page.line.me/joqr_916" target="_blank">@joqr_916</a>」<br></info>
<pfm>大竹まこと、水谷加奈、砂山圭大郎</pfm>
<img>https://program-static.cf.radiko.jp/vp38cx1j3y.jpg</img>
<tag>
<item>
<name>文化放送</name>
</item>
<item>
<name>ゴールデンラジオ</name>
</item>
<item>
<name>大竹まこと</name>
</item>
<item>
<name>水谷加奈</name>
</item>
<item>
<name>いとうあさこ</name>
</item>
<item>
<name>きたろう</name>
</item>
</tag>
<genre>
<personality id="C010">
<name>タレント</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="LFR">
<name>ニッポン放送</name>
<progs>
<date>20250212</date>
<prog id="11189730" master_id="" ft="20250212110000" to="20250212112000" ftl="1100" tol="1120" dur="1200">
<title>テレフォン人生相談</title>
<url>https://www.1242.com/jinseisoudan/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>2</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>2</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc>人生には様々な喜びがあり、同時に苦しみや悩みもあります。人に言えない、誰にも相談できない、悩みや苦しみ。そんな時いくらかお役に立てれば…というのが、この番組です。各界の専門家があなたのご相談に応じます。<br><br>〇パーソナリティ：加藤諦三、今井通子、柴田理恵、玉置妙憂、田中ウルヴェ京<br>〇回答者：大原敬子（幼児教育研究）、マドモアゼル・愛（エッセイスト）、高橋龍太郎（精神科医）、三石由起子（作家・翻訳家）、森田豊（医師・医療ジャーナリスト）、中川潤（弁護士）、大迫恵美子（弁護士）、坂井眞（弁護士）、塩谷崇之（弁護士）、野島梨恵（弁護士）<br><br>■ご相談受付<br>毎週火曜日と水曜日にご相談をお受けしています。<br>受付時間 13：30～15：00<br>電話番号 03－3211－3288 または 03－3211－3299<br>電話受付はお休みすることがあります。放送でご案内しますので、ご確認ください。</desc>
<info>番組ホームページは<a href="https://www.1242.com/jinseisoudan/">こちら</a></info>
<pfm>加藤諦三、今井通子、柴田理恵、玉置妙憂、田中ウルヴェ京</pfm>
<img>https://program-static.cf.radiko.jp/yi2752uku5.jpg</img>
<tag/>
<genre>
<personality id="C012">
<name>文化人</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11189731" master_id="" ft="20250212112000" to="20250212113000" ftl="1120" tol="1130" dur="600">
<title>伊集院光のちょいタネ</title>
<url>https://www.1242.com/ij/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc>月～金曜の11時20分からの10分間は「伊集院光のちょいタネ」<br><br>◇今日のメールテーマ＝「タネ」は【旅行の目的は何ですか？】<br>◇今日のパートナーは、東島衣里アナウンサーです。<br><br>番組で募集したメールテーマが皆さんから寄せられたメッセージによって、<br>話題が樹木のように伸びていくような番組を目指し、たくさんのメッセージを紹介していきます！</desc>
<info>メールアドレス：<br><a href="mailto:ij@1242.com">ij@1242.com</a><br><br>番組ホームページは<a href="https://www.1242.com/ij/">こちら</a><br><br>twitterハッシュタグは「<a href="http://twitter.com/search?q=%23%E4%BC%8A%E9%9B%86%E9%99%A2%E5%85%89%E3%81%AE%E3%82%BF%E3%83%8D">#伊集院光のタネ</a>」twitterアカウントは「<a href="http://twitter.com/ijuintane">@ijuintane</a>」</info>
<pfm>伊集院光、東島衣里</pfm>
<img>https://program-static.cf.radiko.jp/kl4n51rzgs.jpg</img>
<tag>
<item>
<name>伊集院光のタネ</name>
</item>
</tag>
<genre>
<personality id="C010">
<name>タレント</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#伊集院光のタネ"/>
<meta name="twitter" value="from:ijuintane"/>
</metas>
</prog>
</progs>
</station>
<station id="RN1">
<name>ラジオNIKKEI第1</name>
<progs>
<date>20250212</date>
<prog id="11203495" master_id="" ft="20250212090000" to="20250212113500" ftl="0900" tol="1135" dur="9300">
<title>マーケットプレス　前場</title>
<url>https://www.radionikkei.jp/marketpress/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>東京株式市場の株式情報を中心に、為替・商品の情報や経済ニュースなどを生放送でお送りします。ラジオNIKKEIの記者たちが集めた投資情報をリアルタイムでレポートします。<br> <br> 番組公式ブログ：<a href="https://www.radionikkei.jp/marketpress/">https://www.radionikkei.jp/marketpress/</a><br> 番組X（旧twitter）アカウント： <a href="https://twitter.com/market_press">https://twitter.com/market_press</a><br> <br> 皆様からのお声をお待ちしています。</desc>
<info/>
<pfm/>
<img>https://program-static.cf.radiko.jp/j1ukn0x1xa.png</img>
<tag>
<item>
<name>投資が学べる</name>
</item>
</tag>
<genre>
<personality id="C014">
<name>評論家</name>
</personality>
<program id="P020">
<name>株/投資</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11203496" master_id="" ft="20250212113500" to="20250212120500" ftl="1135" tol="1205" dur="1800">
<title>経営トップに聞く！強みと人材戦略</title>
<url>https://www.radionikkei.jp/tsuyomi/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>この番組では、毎回ピックアップする注目企業の経営トップをゲストにお招きして、事業の側面だけでなく人材戦略の観点からも企業の強みに迫ります。トップの人柄が垣間見えるプライベートなQ&Aも。聞き手は、“相場の福の神”こと藤本誠之さん。</desc>
<info/>
<pfm>藤本誠之 / 飯村美樹</pfm>
<img>https://program-static.cf.radiko.jp/gnlu3iqthr.jpg</img>
<tag>
<item>
<name>投資が学べる</name>
</item>
</tag>
<genre>
<program id="P013">
<name>経済</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="RN2">
<name>ラジオNIKKEI第2</name>
<progs>
<date>20250212</date>
<prog id="11223490" master_id="" ft="20250212090000" to="20250212120000" ftl="0900" tol="1200" dur="10800">
<title>RaNi Music♪Morning</title>
<url>https://www.radionikkei.jp/ranimusic/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><a href='https://www.radionikkei.jp/ranimusic/radikorani_music.html'><img src='https://www.ranimusic.jp/noa/radikoimg/continuous_play_400x60.jpg' /></a><br /><br />▼この時間のプレイリスト▼<br /><br />9:00 best day, best way/LiSA (2013年)<br />9:04 Soup/Remi Wolf (2024年)<br />9:09 ミモザ/ゴスペラーズ (2004年)<br />9:13 Love Someone/Lukas Graham (2018年)<br />9:17 Dragon Night/SEKAI NO OWARI (2014年)<br />9:20 I'm Not The Only One feat. Alicia Keys/Sam Smith (2024年)<br />9:24 Dancing in the Dark/Bruce Springsteen (1984年)<br />9:28 Same Blue/Official髭男dism (2024年)<br />9:32 Modern Girl/Sheena Easton (1980年)<br />9:36 ルバート/ヨルシカ (2024年)<br />9:39 Lonely/Diplo & Jonas Brothers (2019年)<br />9:42 Magnificent Time/Travis (2016年)<br />9:44 Return to Pooh Corner/Kenny Loggins (1994年)<br />9:48 PAPARAZZI/少女時代 (2012年)<br />9:52 Black Walnut/SHEBAD (2024年)<br />9:56 Cosmic Treat/Perfume (2024年)<br />9:59 Smile/Katy Perry (2020年)<br />10:01 Better Place/Rachel Platten (2016年)<br />10:04 フェアリーテール/Novelbright (2021年)<br />10:09 もうええわ/藤井風 (2019年)<br />10:13 Perfect Way/Scritti Politti (1985年)<br />10:17 メトロシティ/imase & なとり (2024年)<br />10:20 Talk talk feat Troye Sivan/Charli XCX (2024年)<br />10:23 Alright/Janet Jackson (1990年)<br />10:28 CYAN/フレデリック (2024年)<br />10:32 Bad Habits/Ed Sheeran (2021年)<br />10:36 向日葵/木村カエラ (2016年)<br />10:40 Dancing In The Flames/The Weeknd (2024年)<br />10:44 Sugar/Maroon 5 (2015年)<br />10:48 ALL I WANT/平手友梨奈 (2024年)<br />10:52 I'll Be/Celine Dion (2023年)<br />10:54 Girls Just Want To Have Fun/Cyndi Lauper (1983年)<br />10:58 Tragicomedy/SHE'S (2020年)<br />11:02 Love Me Like That/Mike Perry (2024年)<br />11:04 One of Those Days/Little Big Town (2016年)<br />11:09 アイオライト/Omoinotake (2024年)<br />11:11 Will You Be There/Michael Jackson (1993年)<br />11:17 うたエール/ゆず (2018年)<br />11:21 clouds/JVKE (2024年)<br />11:24 Tweedia/安田レイ (2015年)<br />11:28 アオゾラペダル/嵐 (2006年)<br />11:34 luther/Kendrick Lamar & SZA (2024年)<br />11:36 雪明かり (Yukiakari)/&TEAM (2024年)<br />11:40 The Middle/Zedd, Maren Morris & Grey (2018年)<br />11:43 The End of the Innocence/Don Henley (1989年)<br />11:48 幽霊と作家/水曜日のカンパネラ (2024年)<br />11:52 Place In This World/Michael W. Smith (1991年)<br />11:56 青いベンチ/サスケ (2003年)<br />（洋楽：56%　邦楽：44%）<br /><br /><a href='https://www.radionikkei.jp/lp/ranimusic.html'><img src='https://www.ranimusic.jp/noa/radikoimg/cmsup.jpg' /></a><br /><br /><a href='https://radiko.jp/share/?sid=RN2&t=20250212083000'><img src='https://www.ranimusic.jp/noa/radikoimg/playtopb.png' /> <em>この日の最初のRaNi Music♪へ</em></a><br /><br /><a href='https://radiko.jp/share/?sid=RN2&t=20250212120000'><img src='https://www.ranimusic.jp/noa/radikoimg/playnextb.png' /> <em>次の時間のRaNi Music♪へ</em></a><br /><br /><a href='https://www.radionikkei.jp/ranimusic/onair/?date=20250212#oa-0900'><img src='https://www.ranimusic.jp/noa/radikoimg/playonpub.png' /><em>その他の楽曲情報はこちらへ</em></a><br /></info>
<pfm/>
<img>https://program-static.cf.radiko.jp/88a8ec34-ef4d-471f-a21f-cbc6e63d48f9.png</img>
<tag>
<item>
<name>音楽番組</name>
</item>
<item>
<name>RaNiMusic</name>
</item>
<item>
<name>RNM</name>
</item>
<item>
<name>RMMORNING</name>
</item>
</tag>
<genre>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11223491" master_id="" ft="20250212120000" to="20250212150000" ftl="1200" tol="1500" dur="10800">
<title>RaNi Music♪Day</title>
<url>https://www.radionikkei.jp/ranimusic/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><a href='https://www.radionikkei.jp/ranimusic/radikorani_music.html'><img src='https://www.ranimusic.jp/noa/radikoimg/continuous_play_400x60.jpg' /></a><br /><br />▼この時間のプレイリスト▼<br /><br />12:00 New me/YOASOBI (2024年)<br />12:03 Heaven's What I Feel/Gloria Estefan (1998年)<br />12:09 Beautiful Journey/平井大 (2019年)<br />12:13 Last Friday Night/Katy Perry (2011年)<br />12:17 メーベル/なとり (2025年)<br />12:20 SHELL ( OF A MAN )/Saya Gray (2024年)<br />12:23 空へ/山崎まさよし (2016年)<br />12:28 青い車/スピッツ (1994年)<br />12:33 No One/Alicia Keys (2007年)<br />12:37 ONE/Aimer (2017年)<br />12:42 フリージア/Uru (2017年)<br />12:48 Azalea/米津玄師 (2024年)<br />12:52 Fast Car/Tracy Chapman (1989年)<br />12:57 Blue Thermal/SHE'S (2022年)<br />13:01 Visiting Hours/Ed Sheeran (2021年)<br />13:04 Shake & Shake/sumika (2021年)<br />13:09 Taste/Sabrina Carpenter (2024年)<br />13:11 ダーリン/Mrs. GREEN APPLE (2025年)<br />13:16 Why Don't We/Austin Mahone (2019年)<br />13:18 flowers/ゆず (2024年)<br />13:21 This Kiss/Faith Hill (1998年)<br />13:24 VALENTI/BoA (2002年)<br />13:28 KISS ME/氷室京介 (1992年)<br />13:32 Leather and Lace/Stevie Nicks and Don Henley (1981年)<br />13:35 風神/Vaundy (2024年)<br />13:39 MMMBop/Hanson (1996年)<br />13:44 us/milet (2019年)<br />13:48 水平線/back number (2021年)<br />13:53 Let You Be Right/Meghan Trainor (2018年)<br />13:56 ミュージック・アワー/ポルノグラフィティ (2000年)<br />14:00 Back 4 More/Tuxedo (2024年)<br />14:03 Universe/Official髭男dism (2021年)<br />14:09 愛してるって言ってみてもいいかな/松下洸平 (2024年)<br />14:12 Deja vu feat. Sia/Giorgio Moroder (2015年)<br />14:15 ラブレター/YOASOBI (2021年)<br />14:18 Man on the Moon/R.E.M. (1992年)<br />14:23 One More Time/西野カナ (2017年)<br />14:28 REAL/JO1 (2021年)<br />14:32 Love Takes Time/Mariah Carey (1990年)<br />14:35 Corner/三浦大知 (2019年)<br />14:38 YOU & I feat. Khalid/Anne-Marie (2023年)<br />14:41 下弦の月/SCANDAL (2013年)<br />14:45 ねっこ/King Gnu (2024年)<br />14:48 カイト/嵐 (2020年)<br />14:51 Dance With Me/Tones and I (2024年)<br />14:54 Rusty Nail/X JAPAN (1994年)<br />（洋楽：39%　邦楽：61%）<br /><br /><a href='https://www.radionikkei.jp/lp/ranimusic.html'><img src='https://www.ranimusic.jp/noa/radikoimg/cmsup.jpg' /></a><br /><br /><a href='https://radiko.jp/share/?sid=RN2&t=20250212083000'><img src='https://www.ranimusic.jp/noa/radikoimg/playtopb.png' /> <em>この日の最初のRaNi Music♪へ</em></a><br /><br /><a href='https://radiko.jp/share/?sid=RN2&t=20250212150000'><img src='https://www.ranimusic.jp/noa/radikoimg/playnextb.png' /> <em>次の時間のRaNi Music♪へ</em></a><br /><br /><a href='https://www.radionikkei.jp/ranimusic/onair/?date=20250212#oa-1200'><img src='https://www.ranimusic.jp/noa/radikoimg/playonpub.png' /><em>その他の楽曲情報はこちらへ</em></a><br /></info>
<pfm/>
<img>https://program-static.cf.radiko.jp/0145ad41-d166-4ad3-b6bb-496132a605c6.png</img>
<tag>
<item>
<name>音楽番組</name>
</item>
<item>
<name>RaNiMusic</name>
</item>
<item>
<name>RNM</name>
</item>
<item>
<name>RMDAY</name>
</item>
</tag>
<genre>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="INT">
<name>interfm</name>
<progs>
<date>20250212</date>
<prog id="11186958" master_id="" ft="20250212110000" to="20250212125500" ftl="1100" tol="1255" dur="6900">
<title>Otona no Radio Alexandria</title>
<url>https://audee.jp/program/show/57661</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><div class="station_content_description "><table border="0" cellpadding="5" > <tr> <td style="padding: 5px;"><img src="https://pms-next-prod-api-program.s3.ap-northeast-1.amazonaws.com/image/person/aa3f5cb4-9f1b-4570-836f-500a727e142f_sq.jpg" height="60" width="60" alt="ロバート・ハリス"></td> </tr></table><br /><br /> ロバート・ハリスが送る文化情報発信番組。植物、動物、そして人間の生生流転の中でのストーリー【生き物の物語】、ロバート・ハリスのデイリーエッセイ【SELF PORTRAIT】、過去とイマを繋ぐ名曲たちをオンエアする【大人のサードプレイス】・・・好奇心をくすぐる雑談を添えながら、”様々な生き方”のヒントを共有していきます。 <br /><br /> 番組Webサイト：<a href="https://audee.jp/program/show/57661">https://audee.jp/program/show/57661</a><br /> メッセージフォーム：<a href="https://form.audee.jp/alexandria/message">https://form.audee.jp/alexandria/message</a><br /><br /></div></info>
<pfm>ロバート・ハリス</pfm>
<img>https://program-static.cf.radiko.jp/9rga0wfjft.jpg</img>
<tag>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
<item>
<name>気分転換におすすめ</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11186959" master_id="" ft="20250212125500" to="20250212130000" ftl="1255" tol="1300" dur="300">
<title>Public Service Announcement - Yokohama City (English)</title>
<url>https://www.interfm.co.jp/yokohama_en</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><div class="station_content_description "> InterFM897が開局以来続けている「P.S.A.」(Public Service Announcement)は、在日外国人に向け、生活情報や災害時の避難場所などの案内を含め、日本での生活に役立つ情報を中心に、各言語でお届けしています。<br /><br />国際都市「横浜」にふさわしい、多彩な言語での放送が好評です。 <br /><br /> 番組Webサイト：<a href="https://www.interfm.co.jp/yokohama_en">https://www.interfm.co.jp/yokohama_en</a><br /> メールアドレス：<a href="mailto:voice@interfm.co.jp">voice@interfm.co.jp</a><br /><br /></div></info>
<pfm/>
<img>https://program-static.cf.radiko.jp/cdurqtgzoj.jpg</img>
<tag>
<item>
<name>English</name>
</item>
<item>
<name>PSA</name>
</item>
<item>
<name>横浜市</name>
</item>
<item>
<name>Yokohama City</name>
</item>
</tag>
<genre>
<personality id="C001">
<name>アナウンサー</name>
</personality>
<program id="P001">
<name>ニュース/天気/交通</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="FMT">
<name>TOKYO FM</name>
<progs>
<date>20250212</date>
<prog id="11187389" master_id="" ft="20250212110000" to="20250212113000" ftl="1100" tol="1130" dur="1800">
<title>ディア・フレンズ</title>
<url>https://www.tfm.co.jp/dear/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><div class="station_content_description "><table border="0" cellpadding="5" > <tr> <td style="padding: 5px;"><img src="https://pms-next-prod-api-program.s3.ap-northeast-1.amazonaws.com/image/person/e68432e8-4a0a-4d5f-8562-ca5ffc2b0189_sq.jpg" height="60" width="60" alt="坂本美雨"></td> </tr></table><br /><br /> ＼wacciの橋口洋平さんが初登場！／<br /><br />今年、結成15周年イヤーの「wacci」<br />約2年ぶり、6枚目となるニューアルバム『Dressing』が<br />1月29日にリリース♬<br /><br />ドラマ「放課後カルテ」の主題歌『どんな小さな』や<br />これまでリリースした曲に、新曲を加えた全15曲が収録！<br /><br />結成15周年を記念して、初の日比谷野外音楽堂ワンマンも決定しています！！<br /><br />wacciのこれまで、これから、についてお話しうかがっていきます♬<br /><br />【 Q&A 】<br />これまでに経験したドラマのようなできごとは？ <br /><br /> 番組Webサイト：<a href="https://www.tfm.co.jp/dear/">https://www.tfm.co.jp/dear/</a><br /> <br /> Xハッシュタグは「<a href="http://twitter.com/search?q=%23%E3%83%87%E3%82%A3%E3%82%A2%E3%83%95%E3%83%AC%E3%83%B3%E3%82%BA">#ディアフレンズ</a>」<br /> Xアカウントは「<a href="http://twitter.com/dearfriends80">@dearfriends80</a>」<br /><br /></div></info>
<pfm>坂本美雨</pfm>
<img>https://program-static.cf.radiko.jp/z3c537lqhm.jpg</img>
<tag>
<item>
<name>坂本美雨</name>
</item>
</tag>
<genre>
<personality id="C004">
<name>ミュージシャン</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11187390" master_id="" ft="20250212113000" to="20250212130000" ftl="1130" tol="1300" dur="5400">
<title>ALL-TIME BEST～LUNCH TIME POWER MUSIC～ supported by Ginza Sony Park</title>
<url>https://www.tfm.co.jp/atb/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><div class="station_content_description "><table border="0" cellpadding="5" > <tr> <td style="padding: 5px;"><img src="https://pms-next-prod-api-program.s3.ap-northeast-1.amazonaws.com/image/person/ad23e521-10ca-4d30-ba30-d65dd677d352_sq.jpg" height="60" width="60" alt="LOVE"></td> </tr></table><br /><br /> “今日” “いま” リアルタイムにこだわった新旧・洋邦ベストミックスを90分ノンストップでお届け！ <br /><br /> ▽11:51〜 【 TOKYO FM NEWS 】<br/>---<br /><br />▽11:53〜 【 交通情報 】<br/>---<br /><br />▽12:30〜 【 Street Music Snap by Ginza Sony Park 】<br/>都会の中の公園「Ginza Sony Park」で過ごす年齢も国籍も音楽のジャンルも聴き方も様々な人たち。<br />街角ファッションスナップのようにGinza Sony Parkにいる方へのインタビューを通して、オススメする音楽をスナップしていきます。<br /><br />▽12:50〜 【 交通情報 】<br/>---<br /><br />▽12:54〜 【 ALL-TIME BEST ラジオショッピング 】<br/>---<br /><br /> 番組Webサイト：<a href="https://www.tfm.co.jp/atb/">https://www.tfm.co.jp/atb/</a><br /> メッセージフォーム：<a href="https://www.tfm.co.jp/f/atb/form">https://www.tfm.co.jp/f/atb/form</a><br /> <br /> Xハッシュタグは「<a href="http://twitter.com/search?q=%23ATB">#ATB</a>」<br /> Xアカウントは「<a href="http://twitter.com/LOVEstaff">@LOVEstaff</a>」<br /><br /></div></info>
<pfm>LOVE</pfm>
<img>https://program-static.cf.radiko.jp/n6e7w0qpyr.jpg</img>
<tag>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
<item>
<name>作業がはかどる</name>
</item>
<item>
<name>ドライブ中におすすめ</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="FMJ">
<name>J-WAVE</name>
<progs>
<date>20250212</date>
<prog id="11208989" master_id="" ft="20250212110000" to="20250212130000" ftl="1100" tol="1300" dur="7200">
<title>STEP ONE(PART2)</title>
<url>https://www.j-wave.co.jp/original/stepone/</url>
<url_link>https://www.j-wave.co.jp/original/stepone/?x11=_(radiko-uid)</url_link>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>働く方へのお役立ち情報とGood Musicをお届け♪<br /> サッシャ&ノイハウス萌菜がナビゲート！<br /> ★西田優大が海外旅から得た学びとは？<br /> ★いまちゃんと知っておきたいDeepSeekのこと<br /> ★ゲストは、Laura day romance<br /> ☆birdの新曲を初オンエア！<br /> ▼9:15～　「START UP」<br /> 1日をスタートさせるための基礎情報と<br /> やる気スイッチが入る入魂の１曲をお届け！<br /> <br /> ▼9:35～　「Expedia LISTEN AND LEARN 」<br /> 「人生で得た学びや、気づき」について伺うコーナー<br /> 今週は、B.LEAGUEの西田優大選手さんが登場！<br /> <br /> ▼10:10～ 「SAISON CARD ON THE EDGE」<br /> いまちゃんと知っておきたいDeepSeekのことについて、<br /> ITジャーナリストの三上洋さんに伺います<br /> <br /> ▼11:15～『MUSIC BOOSTER』 <br /> お仕事時間を音楽で彩る20分！<br /> DJによるNON STOP MIXをお届けします。<br /> 今週の担当は、DJ DRAGON<br /> <br /> ▼11:45～ 『CHEER UP WORKERS』 <br /> J-WAVEを聞いているあなたのお仕事をPR！ <br /> <br /> ▼12:05- 『CHINTAI GLOBAL BEATS』<br /> STEP ONE独自の視点で海外情報とNEW MUSICをお届け！<br /> <br /> ▼12:30～『MUSIC+1』<br /> Laura day romanceが登場！<br /> <br /> 11:07 PHOTOGRAPH / ED SHEERAN<br /> </desc>
<info><a href="https://www.j-wave.co.jp/original/stepone/?x11=_(radiko-uid)" target="_blank"><img src="https://www.j-wave.co.jp/epg/images/649966c7c76a6.jpeg"><img src="https://www.j-wave.co.jp/epg/images/649966c7cc897.png" height="52"></a><br /> <br /> 9:35-西田優大<br /> 10:10-三上洋（ITジャーナリスト）<br /> 12:30-Laura day romance</info>
<pfm>サッシャ / ノイハウス萌菜</pfm>
<img>https://program-static.cf.radiko.jp/hclv9hjj0l.jpg</img>
<tag>
<item>
<name>作業がはかどる</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
<item>
<name>気分転換におすすめ</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P003">
<name>情報</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11208990" master_id="" ft="20250212130000" to="20250212133000" ftl="1300" tol="1330" dur="1800">
<title>TALK TO NEIGHBORS</title>
<url>https://www.j-wave.co.jp/original/talktoneighbors/</url>
<url_link>https://www.j-wave.co.jp/original/talktoneighbors/?x11=_(radiko-uid)</url_link>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>2月10日〜2月13日のゲストは、シンガーソングライターの畠山美由紀さん。<br /> クリス智子がじっくりお話を伺います。<br /> 2月12日は、引き続きシンガーソングライターの畠山美由紀さんをゲストにお迎え。<br /> <br /> この日は、畠山さんの日常とルーツをのぞかせていただきます。<br /> <br /> 心地よい雰囲気を大切にしながら、その瞬間にしか聴けないゲストの言葉を引き出すプロフェッショナル、<br /> クリス智子が毎週一組のゲストをお迎えして、よりじっくりと、より濃密なトークをお届けする番組。<br /> <br /> 毎週金曜日には、放送された内容に加え、Podcastでしか聞けないお話も交えて配信します。</desc>
<info><a href="https://www.j-wave.co.jp/original/talktoneighbors/?x11=_(radiko-uid)" target="_blank"><img src="https://www.j-wave.co.jp/epg/images/66081efa68116.jpeg"><img src="https://www.j-wave.co.jp/epg/images/66081efa6e355.png" height="52"></a><br /> <br /> 畠山美由紀</info>
<pfm>クリス智子</pfm>
<img>https://program-static.cf.radiko.jp/opf5qu1yqp.jpg</img>
<tag>
<item>
<name>気分転換におすすめ</name>
</item>
<item>
<name>人気アーティストトーク</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P007">
<name>トーク</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="JORF">
<name>ラジオ日本</name>
<progs>
<date>20250212</date>
<prog id="11167221" master_id="" ft="20250212110000" to="20250212115500" ftl="1100" tol="1155" dur="3300">
<title>SWEET!! (3)</title>
<url>https://www.jorf.co.jp/?program=sw</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>▽昨日より今日、もっとSWEETな一日に！<br>毎日のHOTな情報から主婦に役立つ情報まで盛りだくさんでお送りします。<br><br>▽パーソナリティ：棚橋麻衣<br><br>▽今日のメッセージテーマは「理想の老後」<br><br>▼09：40頃　気になるニュース<br>今日の新聞から気になる記事をご紹介！<br><br>▼10：10頃　ゲストコーナー<br>姿月あさとさんをお迎えします！<br><br>▼11：05頃　HAPPY ENGLISH<br>ハワイ出身Vance Kがセレクトした洋楽を解説！<br><br>▼11：20頃　女神の選択<br>―キラキラと輝く女神の選択を、ちょっと覗いてみませんか？<br>今週は、フリーランスでアクセサリー企画をされています後藤園子さんにお話伺います。<br><br>番組へのメッセージはこちら<br>メール：<A Href="mailto:sw@jorf.co.jp">sw@jorf.co.jp</a><br>Xアカウントは「<A Href="https://X.com/sweet924_1422" target="_blank">@sweet924_1422</A>」</desc>
<info>Xハッシュタグは「<a href="http://twitter.com/search?q=%23%E3%82%B9%E3%82%A4%E3%83%BC%E3%83%88924">#スイート924</a>」</info>
<pfm>棚橋麻衣</pfm>
<img>https://program-static.cf.radiko.jp/9c209820-89d8-4a94-ad27-5d56469766a4.jpeg</img>
<tag>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
</tag>
<genre>
<personality id="C010">
<name>タレント</name>
</personality>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11167222" master_id="" ft="20250212115500" to="20250212120000" ftl="1155" tol="1200" dur="300">
<title>ラジオ日本ニュース・天気予報</title>
<url/>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info>Xハッシュタグは「<a href="http://twitter.com/search?q=%23jorf">#jorf</a>」</info>
<pfm/>
<img>https://program-static.cf.radiko.jp/bcaa3eae-7605-464e-9c4c-923c3e9371e4.png</img>
<tag/>
<genre>
<personality id="C001">
<name>アナウンサー</name>
</personality>
<program id="P001">
<name>ニュース/天気/交通</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="BAYFM78">
<name>BAYFM78</name>
<progs>
<date>20250212</date>
<prog id="11188158" master_id="" ft="20250212110000" to="20250212120000" ftl="1100" tol="1200" dur="3600">
<title>miracle!! Hour.3</title>
<url>https://bayfm.co.jp/program/anna/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>■今回のTOPICS ●いよいよ開催間近！ ２月１６日（日曜日）ショッピングモール「牧の原モア」で開催！ ニュータウンニューワールドの公開録音パーティーの詳細発表！ ベイエフエムのウェブサイトの特設ページを合わせてチェック！ ●リサーチテーマは・・・「　忘れたいこと、じょんがら節　」 忘れたいのに忘れられないあのハナシ！ アンナの「クチじょんがら」でスッキリ忘れて頂く、 心の消しゴム企画！忘れたいことは、なあに？ ●＃ミラクルワード 9時45分凸凹　忙しいあなたに代わって 今押さえたい、気になる「コトバ」をキャッチアップ！ ●ミラクルゴールデンヒッツ　 10時～　水曜日は世界のR&B HIP HOPから！ ゴールデンなあの曲をミラクルチョイス！ ●「　こぶくろさん　」 11時～　スーパーやコンビニで百花繚乱の 個包装、小袋入りのグルメをセレクション！</desc>
<info><p><br><a href="https://link.bayfm.co.jp/3iepjgc"><img src="https://bayfm.co.jp/wp-content/uploads/dj_photo160/anna.jpg"></a><br><strong>ANNA</strong><br><br><br><br>BAYFM ミラクル 9:00 - 11:59 生放送<br><br>番組宛メール　<a href="mailto:anna@bayfm.co.jp">anna@bayfm.co.jp</a>　24時間受付中<br>番組公式HP　<a href="https://link.bayfm.co.jp/3MZ55pc">https://bayfm.co.jp/program/anna/</a><br>番組公式X　<a href="https://link.bayfm.co.jp/3KRr67w">https://twitter.com/bayfm_miracle</a><br>番組公式ハッシュタグ　<a href="https://link.bayfm.co.jp/3w8ihBR">「#アンナミラクル」</a><br>DJ ANNAのブログ　<a href="https://link.bayfm.co.jp/3KPuMqk">https://ameblo.jp/annahanashi/</a><br><br>--------<br>09:04頃【今日のリサーチテーマの発表＆メニュー紹介】<br><br>09:20 【BAYFMリスナー安全運転宣言】<br>みなさんが日々の生活の中で気づいた交通安全メッセージをご紹介。<br><br>09:40 #ミラクルワード<br><br>09:57 【Weather News】<br><br>10:00 【今日のミラクルコレクション 洋楽邦楽の新旧アルバムを紹介】<br><br>10:20 【ヤマサ・デイリーティップス】<br>　　　毎日の生活に役立つ充実ライフのヒントをお届け！<br><br>月・火　毎週日替わりアーティスト・コメント<br><br>11:05 【Precious Report】<br><br>11:18 【BAYFM Updates】<br><br>11:51【Ending】<br><br>--------<br><br><a href="https://link.bayfm.co.jp/37p5S26" target="_blank" rel="noopener">■BAYFM公式HP</a><br><a href="https://link.bayfm.co.jp/3whdQoF" target="_blank" rel="noopener">■オンエア楽曲一覧</a></p></info>
<pfm>ANNA</pfm>
<img>https://program-static.cf.radiko.jp/d4wvphk2rl.jpg</img>
<tag>
<item>
<name>気分転換におすすめ</name>
</item>
<item>
<name>アンナミラクル</name>
</item>
<item>
<name>ANNA</name>
</item>
<item>
<name>アンナ</name>
</item>
<item>
<name>地域活性</name>
</item>
<item>
<name>バラエティー</name>
</item>
<item>
<name>主婦</name>
</item>
<item>
<name>料理</name>
</item>
<item>
<name>午前中</name>
</item>
<item>
<name>千葉県</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P006">
<name>バラエティ</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11188159" master_id="" ft="20250212120000" to="20250212125100" ftl="1200" tol="1251" dur="3060">
<title>YAMAMAN presents MUSIC SALAD FROM U-kari STUDIO</title>
<url>https://bayfm.co.jp/program/salad/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>聞くだけじゃなく参加して楽しむランチタイムプログラム！ ユーカリスタジオから公開生放送です。 番組の最後にかける曲を投票で決める「サラドレ」！ ひとことメッセージとラジオネームをどんどん紹介していく「ひとことメッセージタイム」！ 番組にメッセージを送ると新アイテム「まるっとコアラスタ」が当たるチャンスも！ 明日が楽しみになるタネをまく「縁ジョイント」は橋本がチャレンジしている あの大作戦の話をお届けします！</desc>
<info><p><br><a href="https://link.bayfm.co.jp/3iepjgc"><img src="https://bayfm.co.jp/wp-content/uploads/dj_photo160/hashimoto_noi.jpg"></a><br><strong>橋本乃依</strong><br><br>2月12日（水）<br>1.　ももいろクローバーZ　/　行くぜっ！怪盗少女 -ZZ ver.-<br>2.　PRINCESS PRINCESS　/　19 GROWING UP<br>3.　King Gnu　/　白日<br>4.　GRe4N BOYZ　/　愛唄<br>5.　井上陽水　/　リバーサイドホテル<br><br>投票＆メッセージは<a href="https://link.bayfm.co.jp/3NLdCfB">こちら</a>から<br>投票だけの方は<a href="https://link.bayfm.co.jp/3NKPSYT">こちら</a>から<br><br>番組公式HP　<a href="https://link.bayfm.co.jp/363srJl" target="_blank" rel="noopener">https://bayfm.co.jp/program/salad/</a><br>番組公式Facebook　<a href="https://link.bayfm.co.jp/3CTXd3t" target="_blank" rel="noopener">https://www.facebook.com/MusicSalad</a><br>番組公式X　<a href="https://link.bayfm.co.jp/34PjhzK" target="_blank" rel="noopener">https://twitter.com/Msalad</a><br>番組公式ハッシュタグ<a href="https://link.bayfm.co.jp/3MXoWFd">「#musicsalad」</a><br><br><a href="https://link.bayfm.co.jp/37p5S26" target="_blank" rel="noopener">■BAYFM公式HP</a><br><a href="https://link.bayfm.co.jp/3whdQoF" target="_blank" rel="noopener">■オンエア楽曲一覧</a></p></info>
<pfm>橋本 乃依</pfm>
<img>https://program-static.cf.radiko.jp/hgq3elg4z7.jpg</img>
<tag>
<item>
<name>ドライブ中におすすめ</name>
</item>
<item>
<name>musicsalad</name>
</item>
<item>
<name>橋本乃依</name>
</item>
<item>
<name>サラドレ</name>
</item>
<item>
<name>公開生放送</name>
</item>
<item>
<name>千葉県</name>
</item>
<item>
<name>BAYFM</name>
</item>
</tag>
<genre>
<personality id="C010">
<name>タレント</name>
</personality>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="NACK5">
<name>NACK5</name>
<progs>
<date>20250212</date>
<prog id="11188752" master_id="" ft="20250212110000" to="20250212120000" ftl="1100" tol="1200" dur="3600">
<title>Smile SUMMIT Part3</title>
<url>https://www.nack5.co.jp/program/smilesummit/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><p>栗林さみがお送りする【Smile SUMMIT】！<br><br><br>▽9:00<br>　朝の頭の体操にピッタリな【Smile Quiz】<br>　正解者から抽選で１人に、クイズ専用ステッカーをプレゼント！<br>　ぜひ、ご参加ください！<br><br><br>▼9:10<br>　採れたての話題を取りそろえた【Smile MARKET】<br>　今日のキーワードは「私を叱ったあの先生」<br><br><br>▽10:10<br>　今押さえておくべき「笑顔のタネ」を<br>　みんなでお勉強する【SMILE LEARNING】<br>　今週は『ブラックサンダー』をラーニング！<br><br><br>▼10:45<br>【Smile YEN】<br>　あなたの「最近のお買い物・節約事情」教えてください！<br>　栗林もこのコーナーでがんばって１０万円貯めます！<br><br>▼11:00<br>　今日、これを食べると運気がアップする！<br>　占いコーナー【ラッキーランチ】<br>　今日は「金運」<br><br>▽11:10<br>　働くあなたを応援する新コーナー【Cheerful Style】<br>　水曜日はうちで働いている人をテーマに、家事や育児あるある、<br>　ちょっとした知恵や工夫などを紹介する「スマカジ」<br><br>▼11:35<br>【森林 永理奈 チョット CHAT CLUB】<br>パーソナリティの森林永理奈が　家事、育児のライフハックをお話しします！<br><br>▽12:08<br>　みんなで気になる話題を語り合う<br><br>【THE SUMMIT TALK（ザ・サミットーク）】<br>　議題は10時00分頃に発表します！<br><br>◎番組公式【X】アカウントは・・・【@smilesummit795】<br>　つぶやく時は、ハッシュタグ【#smile795】を付けてつぶやいて下さい！<br><br>●今日もみんなで笑顔の頂点を目指しましょう！●<br></p><p>【メッセージフォーム】</p><p><a href="https://www.nack5.co.jp/message/4835/" target="_blank">今日のテーマ【私を叱ったあの先生】</a></p><p><a href="https://www.nack5.co.jp/message/540/" target="_blank">換気リクエスト</a></p><p><a href="https://www.nack5.co.jp/message/5050/" target="_blank">ブラックサンダー プレゼント</a></p><p><a href="https://www.nack5.co.jp/message/3332/" target="_blank">Smile Walker</a></p><p><a href="https://www.nack5.co.jp/message/2645/" target="_blank">Smile YEN</a></p><p><a href="https://www.nack5.co.jp/message/1585/" target="_blank">Smile For You</a></p><p><a href="https://www.nack5.co.jp/message/3671/" target="_blank">Cheerful Style【月曜：ビタミンサミー】</a></p><p><a href="https://www.nack5.co.jp/message/3675/" target="_blank">Cheerful Style【火曜：Live it up！】</a></p><p><a href="https://www.nack5.co.jp/message/3677/" target="_blank">Cheerful Style【水曜：スマカジ！】</a></p><p><a href="https://www.nack5.co.jp/message/78/" target="_blank">ふつおた</a></p></info>
<pfm>栗林さみ</pfm>
<img>https://program-static.cf.radiko.jp/pxbsazpizz.jpg</img>
<tag>
<item>
<name>栗林さみ</name>
</item>
<item>
<name>smile795</name>
</item>
<item>
<name>nack5</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P003">
<name>情報</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11188753" master_id="" ft="20250212120000" to="20250212123000" ftl="1200" tol="1230" dur="1800">
<title>Smile SUMMIT Part4</title>
<url>https://www.nack5.co.jp/program/smilesummit/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info><p>栗林さみがお送りする【Smile SUMMIT】！<br><br><br>▽9:00<br>　朝の頭の体操にピッタリな【Smile Quiz】<br>　正解者から抽選で１人に、クイズ専用ステッカーをプレゼント！<br>　ぜひ、ご参加ください！<br><br><br>▼9:10<br>　採れたての話題を取りそろえた【Smile MARKET】<br>　今日のキーワードは「私を叱ったあの先生」<br><br><br>▽10:10<br>　今押さえておくべき「笑顔のタネ」を<br>　みんなでお勉強する【SMILE LEARNING】<br>　今週は『ブラックサンダー』をラーニング！<br><br><br>▼10:45<br>【Smile YEN】<br>　あなたの「最近のお買い物・節約事情」教えてください！<br>　栗林もこのコーナーでがんばって１０万円貯めます！<br><br>▼11:00<br>　今日、これを食べると運気がアップする！<br>　占いコーナー【ラッキーランチ】<br>　今日は「金運」<br><br>▽11:10<br>　働くあなたを応援する新コーナー【Cheerful Style】<br>　水曜日はうちで働いている人をテーマに、家事や育児あるある、<br>　ちょっとした知恵や工夫などを紹介する「スマカジ」<br><br>▼11:35<br>【森林 永理奈 チョット CHAT CLUB】<br>パーソナリティの森林永理奈が　家事、育児のライフハックをお話しします！<br><br>▽12:08<br>　みんなで気になる話題を語り合う<br><br>【THE SUMMIT TALK（ザ・サミットーク）】<br>　議題は10時00分頃に発表します！<br><br>◎番組公式【X】アカウントは・・・【@smilesummit795】<br>　つぶやく時は、ハッシュタグ【#smile795】を付けてつぶやいて下さい！<br><br>●今日もみんなで笑顔の頂点を目指しましょう！●<br></p><p>【メッセージフォーム】</p><p><a href="https://www.nack5.co.jp/message/4835/" target="_blank">今日のテーマ【私を叱ったあの先生】</a></p><p><a href="https://www.nack5.co.jp/message/540/" target="_blank">換気リクエスト</a></p><p><a href="https://www.nack5.co.jp/message/5050/" target="_blank">ブラックサンダー プレゼント</a></p><p><a href="https://www.nack5.co.jp/message/3332/" target="_blank">Smile Walker</a></p><p><a href="https://www.nack5.co.jp/message/2645/" target="_blank">Smile YEN</a></p><p><a href="https://www.nack5.co.jp/message/1585/" target="_blank">Smile For You</a></p><p><a href="https://www.nack5.co.jp/message/3671/" target="_blank">Cheerful Style【月曜：ビタミンサミー】</a></p><p><a href="https://www.nack5.co.jp/message/3675/" target="_blank">Cheerful Style【火曜：Live it up！】</a></p><p><a href="https://www.nack5.co.jp/message/3677/" target="_blank">Cheerful Style【水曜：スマカジ！】</a></p><p><a href="https://www.nack5.co.jp/message/78/" target="_blank">ふつおた</a></p></info>
<pfm>栗林さみ</pfm>
<img>https://program-static.cf.radiko.jp/pxbsazpizz.jpg</img>
<tag>
<item>
<name>栗林さみ</name>
</item>
<item>
<name>smile795</name>
</item>
<item>
<name>nack5</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P003">
<name>情報</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="YFM">
<name>ＦＭヨコハマ</name>
<progs>
<date>20250212</date>
<prog id="11187027" master_id="" ft="20250212090000" to="20250212120000" ftl="0900" tol="1200" dur="10800">
<title>Lovely Day♡</title>
<url>https://www.fmyokohama.co.jp/program/LovelyDay</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info>9:45【PLAY OUR LIST】<br />　ミュージックプレイリストに加えたくなる曲を、様々なテーマでお届けします。<br />　<br />10:10【ラブリー♡オーラルケア～歯っとする話～】<br /><br />10:30【ゲスト】<br />　ワンデイゲスト・三宅健さん 登場！<br /><br />9:15/10:00/11:05　【街角リポート】<br />　街角リポーター藤田優一/フジタくんが街角情報をお届けします。<br />　オンエア後に、今日の街角リポートの様子をチェック<a href="http://blog.fmyokohama.jp/machikado/">→街角リポートブログ</a><br /><br />X アカウント：<a href="https://twitter.com/LovelyDay847" target="_blank">@LovelyDay847</a><br />X ハッシュタグ：<a href="https://twitter.com/search?q=%23lovelyday847" target="_blank">#lovelyday847</a><br />Instagram：<a href="https://www.instagram.com/lovelyday847" target="_blank">https://www.instagram.com/lovelyday847</a><br />facebook：<a href="https://www.facebook.com/FmyokohamaLovelyDay" target="_blank">https://www.facebook.com/FmyokohamaLovelyDay</a><br />LINEアカウント：<a href="https://page.line.me/lovelyday847" target="_blank">@lovelyday847</a><br />メールアドレス：<a href="mailto:lovely@fmyokohama.jp">lovely@fmyokohama.jp</a><br /></info>
<pfm>近藤さや香 / 藤田優一</pfm>
<img>https://program-static.cf.radiko.jp/4bbe4368-0ad2-40aa-8ba6-a7091f92a9df.jpeg</img>
<tag>
<item>
<name>近藤さや香</name>
</item>
<item>
<name>藤田優一</name>
</item>
<item>
<name>lovelyday847</name>
</item>
<item>
<name>LovelyDay</name>
</item>
<item>
<name>街角リポート</name>
</item>
<item>
<name>家事</name>
</item>
<item>
<name>子育て</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
</tag>
<genre>
<personality id="C001">
<name>アナウンサー</name>
</personality>
<program id="P021">
<name>ライフスタイル</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11187028" master_id="" ft="20250212120000" to="20250212150000" ftl="1200" tol="1500" dur="10800">
<title>Kiss & Ride</title>
<url>https://www.fmyokohama.co.jp/program/KissAndRide</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc/>
<info>あなたをのせるラジオ「Kiss & Ride」<br />水曜日は小林大河がチャラッとソロリとお届け！<br />ちょっと聞いてよ～、なメッセージ＆リクエストは24時間受付中！<br />Xからのリクエストは「#キスリク」ハ・ミ・ン・グ♪<br /><br />▽12:15頃/14:15頃【CHECK IN】<br />　水/木リポーター長友愛莉が神奈川のいろんな所へチェックイン！らくらく～にアモーレ！！<br />　リポートX「@kr_report_Fyoko」<br /><br />▽13:05頃【キスライPICK UP】<br />　シートにお招きするのは1dayジャック中の三宅健さん！<br />　健さんのちょっと聞いてよ～とは！？<br /><br />▽14:30頃【キスライ・マネ活5minutes】<br />　将来・趣味に役立つ資産形成“マネ活”のヒントを！<br />　ファイナンシャルアドバイザー山口博之さんに聞く、NISA制度について。<br /><br />X アカウント：<a href="https://twitter.com/kr_staff" target="_blank">@kr_staff</a><br />X ハッシュタグ：<a href="https://twitter.com/search?q=%23%E3%82%AD%E3%82%B9%E3%83%A9%E3%82%A4" target="_blank">#キスライ</a><br />メールアドレス：<a href="mailto:kr@fmyokohama.jp">kr@fmyokohama.jp</a><br /></info>
<pfm>小林大河 / 長友愛莉</pfm>
<img>https://program-static.cf.radiko.jp/14e005a7-9488-4616-8c60-87dd119c067d.jpeg</img>
<tag>
<item>
<name>人気アーティストトーク</name>
</item>
<item>
<name>音楽との出会いが楽しめる</name>
</item>
<item>
<name>マネ活</name>
</item>
<item>
<name>Z世代</name>
</item>
<item>
<name>小林大河</name>
</item>
<item>
<name>長友愛莉</name>
</item>
<item>
<name>キスライ</name>
</item>
<item>
<name>リポート</name>
</item>
<item>
<name>気分転換におすすめ</name>
</item>
<item>
<name>作業がはかどる</name>
</item>
<item>
<name>ドライブ中におすすめ</name>
</item>
</tag>
<genre>
<personality id="C015">
<name>ラジオDJ</name>
</personality>
<program id="P021">
<name>ライフスタイル</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="IBS">
<name>LuckyFM 茨城放送</name>
<progs>
<date>20250212</date>
<prog id="11139913" master_id="" ft="20250212110000" to="20250212130000" ftl="1100" tol="1300" dur="7200">
<title>HAPPYパンチ！　②</title>
<url>https://lucky-ibaraki.com/happy/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>「辛いことなんか、PUNCHで吹き飛ばしてHAPPYになろう！なんとかなるよ！」というメッセージを込めて放送中！<br> 地元茨城出身のシンガーソングライター『KATSUMI』、 <br> ロックバンド「スキップカウズ」のボーカル『イマヤス』、 <br> アコースティックデュオ「京太朗と晴彦」のボーカル『京太朗』 <br> そして、20数年にわたり茨城放送の人気番組を多数担当してきた『たかとりじゅん』という4人の大人の男の個性に <br> 5人の女性アシスタントの若い感性をプラスして楽しい時間をお届けします！ <br></desc>
<info>～本日のメニュー～<br> ▼9:10,12:30「ニュース」<br> ▼9:13,9:56,10:56,12:33「天気予報」<br> ▼9:27,10:30,11:30「交通情報」<br><br> ▼9:35「JAさわやかモーニング」<br> ▼10:00「PUNCH TOPICS!!」<br> アシスタントのくまきもえが、いま、気になっているあれこれをご紹介！！<br> ▼11:35「ぼくの作文わたしの作文」<br><br> ◎番組へのメッセージはこちら↓<br> メール：<a href="mailto:happy@lucky-ibaraki.com">happy@lucky-ibaraki.com</a><br> X：#ハピパン をつけて投稿<br> ◎<a href="https://twitter.com/happy_luckyfm ">「HAPPYパンチ！」番組X</a><br> ◎<a href="https://lucky-ibaraki.com/blogs/?blog=blog_happy">「HAPPYパンチ！」番組ブログ</a></info>
<pfm>イマヤス / くまきもえ</pfm>
<img>https://program-static.cf.radiko.jp/5231d302-42bf-4a1c-90d3-1430b600abca.jpeg</img>
<tag>
<item>
<name>HAPPYパンチ</name>
</item>
<item>
<name>ハピパン</name>
</item>
<item>
<name>イマヤス</name>
</item>
<item>
<name>くまきもえ</name>
</item>
<item>
<name>LuckyFM</name>
</item>
<item>
<name>茨城放送</name>
</item>
</tag>
<genre/>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11139914" master_id="" ft="20250212130000" to="20250212160000" ftl="1300" tol="1600" dur="10800">
<title>MUSIC STATE</title>
<url>https://lucky-ibaraki.com/ims/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>0</ts_in_ng>
<tsplus_in_ng>0</tsplus_in_ng>
<ts_out_ng>0</ts_out_ng>
<tsplus_out_ng>0</tsplus_out_ng>
<desc>曜日変わりのパーソナリティが個性豊かなトークと音楽で綴るミュージックワイドプログラム。火曜・水曜はイーアスつくばLucky Studioから公開生放送！</desc>
<info>イーアスつくばLucky Studioからから生放送！<br> ▼13：30 「Music R」<br> 音楽を年代ごとにご紹介するコーナー。水曜日はR40。40代の方々が、10代20代のころに聞いていた曲をお送りします！<br> ▼14：30 「SOUND JAM」<br> ▼15：20 「マシコの青なじみ」<br> リクエストやメッセージは下記アドレスまでどうぞ！<br> メール：<a href="mailto:ms@lucky-ibaraki.com">ms@lucky-ibaraki.com</a><br></info>
<pfm>マシコタツロウ</pfm>
<img>https://program-static.cf.radiko.jp/46338fcb-fe74-4368-9837-f799a6a71acc.jpeg</img>
<tag>
<item>
<name>MUSICSTATE</name>
</item>
<item>
<name>マシコタツロウ</name>
</item>
<item>
<name>青なじみ</name>
</item>
<item>
<name>茨城弁</name>
</item>
<item>
<name>LuckyFM</name>
</item>
<item>
<name>茨城放送</name>
</item>
</tag>
<genre>
<personality id="C004">
<name>ミュージシャン</name>
</personality>
<program id="P005">
<name>音楽</name>
</program>
</genre>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="JOAK">
<name>NHKラジオ第1（東京）</name>
<progs>
<date>20250212</date>
<prog id="11209216" master_id="" ft="20250212110500" to="20250212115000" ftl="1105" tol="1150" dur="2700">
<title>ふんわり　まいにちリクエスト♪　１１時台（２／１２）</title>
<url>https://www.nhk.jp/p/rs/DXN681PPZ1/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>2</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>2</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc/>
<info>１１時台は【まいにちリクエスト♪】「２月１２日に聴きたい！」という曲を、エピソードを添えてお送りください♪<br><br>みなさんから日付指定のリクエストを募集しています。思い入れたっぷりのエピソードがある曲でも、「久しぶりに、聴いてみたいなぁ～」という曲でもＯＫ。あなたの聴きたい曲を、どしどしお寄せください。お待ちしています♪</info>
<pfm>【司会】伍代夏子，稲垣秀人</pfm>
<img>https://program-static.cf.radiko.jp/yrpww7gpwu.jpg</img>
<tag/>
<genre/>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11209217" master_id="" ft="20250212115000" to="20250212120000" ftl="1150" tol="1200" dur="600">
<title>気象情報・交通情報</title>
<url>https://www.nhk.or.jp/radionews/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>2</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>2</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc/>
<info/>
<pfm/>
<img>https://program-static.cf.radiko.jp/64b810d0-a8b0-487b-86ed-2212bdfb8379.png</img>
<tag/>
<genre/>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
<station id="JOAK-FM">
<name>NHK-FM（東京）</name>
<progs>
<date>20250212</date>
<prog id="11209087" master_id="" ft="20250212110000" to="20250212115000" ftl="1100" tol="1150" dur="3000">
<title>邦楽百番　筝曲「四季の眺」ほか</title>
<url>https://www.nhk.jp/p/hyakuban/rs/246PY8J911/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>2</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>2</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc/>
<info>中島一子，奥田雅楽之一，田辺洌山，宮越雅虹，田村雅釉徽，唯是雅枝，吉川雅楽巴里，坂本雅穂，【司会】水谷彰宏<br><br>「四季の眺」<br>殿村平右衛門:作詞<br>松浦検校 八重崎検校・箏手付:作曲<br>（唄と三絃）中島 一子、（唄と箏）奥田 雅楽之一、（尺八）田辺 洌山<br>（１６分０３秒）<br>～ＮＨＫ５０９スタジオ～<br><br>「薄桜」<br>永福門院（ＰＤ）:作詞<br>中島 靖子:作曲<br>（唄）宮越 雅虹、（箏）田村 雅釉徽<br>（６分５７秒）<br>～ＮＨＫ５０９スタジオ～<br><br>「大海原」<br>坪内 逍遙:作詞<br>斎藤 松声:作曲<br>（唄）中島 一子、（唄）唯是 雅枝、（箏本手）吉川 雅楽巴里、（箏替手）奥田 雅楽之一、（三絃）坂本 雅穂、（尺八）田辺 洌山<br>（１９分５０秒）<br>～ＮＨＫ５０９スタジオ～<br></info>
<pfm>中島一子，奥田雅楽之一，田辺洌山，宮越雅虹，田村雅釉徽，唯是雅枝，吉川雅楽巴里，坂本雅穂，【司会】水谷彰宏</pfm>
<img>https://program-static.cf.radiko.jp/icrm432jwe.jpg</img>
<tag/>
<genre/>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
<prog id="11209088" master_id="" ft="20250212115000" to="20250212120000" ftl="1150" tol="1200" dur="600">
<title>気象情報・交通情報</title>
<url>https://www.nhk.or.jp/radionews/</url>
<url_link/>
<failed_record>0</failed_record>
<ts_in_ng>2</ts_in_ng>
<tsplus_in_ng>2</tsplus_in_ng>
<ts_out_ng>2</ts_out_ng>
<tsplus_out_ng>2</tsplus_out_ng>
<desc/>
<info/>
<pfm/>
<img>https://program-static.cf.radiko.jp/db3f2e1f-c31f-44d3-88b7-ca87fb88ac9c.png</img>
<tag/>
<genre/>
<metas>
<meta name="twitter" value="#radiko"/>
</metas>
</prog>
</progs>
</station>
</stations>
</radiko>
'''