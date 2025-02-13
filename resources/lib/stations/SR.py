# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.stations.common import Common


class Scraper(Common):

    PROTOCOL = 'SR'
    URL = 'http://csra.fm/stationlist/'

    def __init__(self):
        super().__init__(self.PROTOCOL)

    def parse(self, data):
        buf = []
        sections = BeautifulSoup(data, features='lxml').find_all('section')
        for section in sections:
            try:
                if section.h1:
                    station = section.h1.string.strip()
                    # 閉局しているものはスキップ
                    if section.prettify().find('閉局') > -1:
                        print('[SR] closed (skip):', station, file=sys.stderr)
                        continue
                    # listenradio.jpを参照しているものはスキップ
                    direct = section.find('a', class_='stm')['href'].strip()
                    if direct.startswith('http://listenradio.jp/'):
                        #print('[SR] listenradio protocol (skip):', station, file=sys.stderr)
                        continue
                    # ストリーミングURLがmms://で始まるか.asxで終わるものを採用
                    if direct.startswith('mms://') is False and direct.endswith('.asx') is False:
                        print('[SR] unsupported protocol (skip):', station, direct, file=sys.stderr)
                        continue
                    results = self.db.search_by_station(self.PROTOCOL, station)
                    if results:
                        code, region, pref, city, station, site, status = results
                        if status:
                            logo = 'http://csra.fm%s' % section.img['src'].strip()
                            #site = section.find('a', class_='site')['href'].strip()
                        else:
                            continue  # 最優先のみ採用する
                    else:
                        print('[SR] not found in master (skip):', station, file=sys.stderr)
                        continue
                else:
                    continue
            except Exception:
                print('[SR] unparsable content (skip):', station, file=sys.stderr)
                continue
            buf.append({
                'protocol': self.PROTOCOL,
                'key': '',
                'station': station,
                'code': code,
                'region': region,
                'pref': pref,
                'city': city,
                'logo': logo,
                'description': '',
                'site': site,
                'direct': direct,
                'delay': 0,
                'display': 1,
                'schedule': 0,
                'download': 0
            })
        return buf


# http://csra.fm/stationlist/

'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, maximum-scale=1.0, minimum-scale=1.0"/>
    <title>STATION LIST｜CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</title>
    <link rel="stylesheet" type="text/css" media="all" href="https://csra.fm/wp-content/themes/CSRA/style.css"/>

    <link rel="stylesheet" href="/js/jquery.mobile/jquery.mobile.css"/>

    <link rel="stylesheet" type="text/css" media="all" href="/csra/css/import.css"/>

    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-106451-31"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {
        dataLayer.push(arguments);
    }
    gtag('js', new Date());

    gtag('config', 'UA-106451-31');
    </script>

    <meta name='robots' content='max-image-preview:large'/>
    <style>
    img:is([sizes="auto" i], [sizes^="auto," i]) {
        contain-intrinsic-size: 3000px 1500px
    }
    </style>
    <script type="text/javascript">
    /* <![CDATA[ */
    window._wpemojiSettings = {
        "baseUrl": "https:\/\/s.w.org\/images\/core\/emoji\/15.0.3\/72x72\/",
        "ext": ".png",
        "svgUrl": "https:\/\/s.w.org\/images\/core\/emoji\/15.0.3\/svg\/",
        "svgExt": ".svg",
        "source": {
            "concatemoji": "https:\/\/csra.fm\/wp-includes\/js\/wp-emoji-release.min.js?ver=6.7.2"
        }
    };
    /*! This file is auto-generated */
    !function(i, n) {
        var o,
            s,
            e;
        function c(e) {
            try {
                var t = {
                    supportTests: e,
                    timestamp: (new Date).valueOf()
                };
                sessionStorage.setItem(o, JSON.stringify(t))
            } catch (e) {}
        }
        function p(e, t, n) {
            e.clearRect(0, 0, e.canvas.width, e.canvas.height),
            e.fillText(t, 0, 0);
            var t = new Uint32Array(e.getImageData(0, 0, e.canvas.width, e.canvas.height).data),
                r = (e.clearRect(0, 0, e.canvas.width, e.canvas.height), e.fillText(n, 0, 0), new Uint32Array(e.getImageData(0, 0, e.canvas.width, e.canvas.height).data));
            return t.every(function(e, t) {
                return e === r[t]
            })
        }
        function u(e, t, n) {
            switch (t) {
            case "flag":
                return n(e, "\ud83c\udff3\ufe0f\u200d\u26a7\ufe0f", "\ud83c\udff3\ufe0f\u200b\u26a7\ufe0f") ? !1 : !n(e, "\ud83c\uddfa\ud83c\uddf3", "\ud83c\uddfa\u200b\ud83c\uddf3") && !n(e, "\ud83c\udff4\udb40\udc67\udb40\udc62\udb40\udc65\udb40\udc6e\udb40\udc67\udb40\udc7f", "\ud83c\udff4\u200b\udb40\udc67\u200b\udb40\udc62\u200b\udb40\udc65\u200b\udb40\udc6e\u200b\udb40\udc67\u200b\udb40\udc7f");
            case "emoji":
                return !n(e, "\ud83d\udc26\u200d\u2b1b", "\ud83d\udc26\u200b\u2b1b")
            }
            return !1
        }
        function f(e, t, n) {
            var r = "undefined" != typeof WorkerGlobalScope && self instanceof WorkerGlobalScope ? new OffscreenCanvas(300, 150) : i.createElement("canvas"),
                a = r.getContext("2d", {
                    willReadFrequently: !0
                }),
                o = (a.textBaseline = "top", a.font = "600 32px Arial", {});
            return e.forEach(function(e) {
                o[e] = t(a, e, n)
            }), o
        }
        function t(e) {
            var t = i.createElement("script");
            t.src = e,
            t.defer = !0,
            i.head.appendChild(t)
        }
        "undefined" != typeof Promise && (o = "wpEmojiSettingsSupports", s = ["flag", "emoji"], n.supports = {
            everything: !0,
            everythingExceptFlag: !0
        }, e = new Promise(function(e) {
            i.addEventListener("DOMContentLoaded", e, {
                once: !0
            })
        }), new Promise(function(t) {
            var n = function() {
                try {
                    var e = JSON.parse(sessionStorage.getItem(o));
                    if ("object" == typeof e && "number" == typeof e.timestamp && (new Date).valueOf() < e.timestamp + 604800 && "object" == typeof e.supportTests)
                        return e.supportTests
                } catch (e) {}
                return null
            }();
            if (!n) {
                if ("undefined" != typeof Worker && "undefined" != typeof OffscreenCanvas && "undefined" != typeof URL && URL.createObjectURL && "undefined" != typeof Blob)
                    try {
                        var e = "postMessage(" + f.toString() + "(" + [JSON.stringify(s), u.toString(), p.toString()].join(",") + "));",
                            r = new Blob([e], {
                                type: "text/javascript"
                            }),
                            a = new Worker(URL.createObjectURL(r), {
                                name: "wpTestEmojiSupports"
                            });
                        return void (a.onmessage = function(e) {
                            c(n = e.data),
                            a.terminate(),
                            t(n)
                        })
                    } catch (e) {}
                c(n = f(s, u, p))
            }
            t(n)
        }).then(function(e) {
            for (var t in e)
                n.supports[t] = e[t],
                n.supports.everything = n.supports.everything && n.supports[t],
                "flag" !== t && (n.supports.everythingExceptFlag = n.supports.everythingExceptFlag && n.supports[t]);
            n.supports.everythingExceptFlag = n.supports.everythingExceptFlag && !n.supports.flag,
            n.DOMReady = !1,
            n.readyCallback = function() {
                n.DOMReady = !0
            }
        }).then(function() {
            return e
        }).then(function() {
            var e;
            n.supports.everything || (n.readyCallback(), (e = n.source || {}).concatemoji ? t(e.concatemoji) : e.wpemoji && e.twemoji && (t(e.twemoji), t(e.wpemoji)))
        }))
    }((window, document), window._wpemojiSettings);
    /* ]]> */
    </script>
    <style id='wp-emoji-styles-inline-css' type='text/css'>
    img.wp-smiley, img.emoji {
        display: inline !important;
        border: none !important;
        box-shadow: none !important;
        height: 1em !important;
        width: 1em !important;
        margin: 0 0.07em !important;
        vertical-align: -0.1em !important;
        background: none !important;
        padding: 0 !important;
    }
    </style>
    <link rel='stylesheet' id='wp-block-library-css' href='https://csra.fm/wp-includes/css/dist/block-library/style.min.css?ver=6.7.2' type='text/css' media='all'/>
    <style id='classic-theme-styles-inline-css' type='text/css'>
    /*! This file is auto-generated */
    .wp-block-button__link {
        color: #fff;
        background-color: #32373c;
        border-radius: 9999px;
        box-shadow: none;
        text-decoration: none;
        padding: calc(.667em + 2px) calc(1.333em + 2px);
        font-size:1.125em
    }

    .wp-block-file__button {
        background: #32373c;
        color: #fff;
        text-decoration: none
    }
    </style>
    <style id='global-styles-inline-css' type='text/css'>
    :root {
        --wp--preset--aspect-ratio--square: 1;
        --wp--preset--aspect-ratio--4-3: 4/3;
        --wp--preset--aspect-ratio--3-4: 3/4;
        --wp--preset--aspect-ratio--3-2: 3/2;
        --wp--preset--aspect-ratio--2-3: 2/3;
        --wp--preset--aspect-ratio--16-9: 16/9;
        --wp--preset--aspect-ratio--9-16: 9/16;
        --wp--preset--color--black: #000000;
        --wp--preset--color--cyan-bluish-gray: #abb8c3;
        --wp--preset--color--white: #ffffff;
        --wp--preset--color--pale-pink: #f78da7;
        --wp--preset--color--vivid-red: #cf2e2e;
        --wp--preset--color--luminous-vivid-orange: #ff6900;
        --wp--preset--color--luminous-vivid-amber: #fcb900;
        --wp--preset--color--light-green-cyan: #7bdcb5;
        --wp--preset--color--vivid-green-cyan: #00d084;
        --wp--preset--color--pale-cyan-blue: #8ed1fc;
        --wp--preset--color--vivid-cyan-blue: #0693e3;
        --wp--preset--color--vivid-purple: #9b51e0;
        --wp--preset--gradient--vivid-cyan-blue-to-vivid-purple: linear-gradient(135deg, rgba(6, 147, 227, 1) 0%, rgb(155, 81, 224) 100%);
        --wp--preset--gradient--light-green-cyan-to-vivid-green-cyan: linear-gradient(135deg, rgb(122, 220, 180) 0%, rgb(0, 208, 130) 100%);
        --wp--preset--gradient--luminous-vivid-amber-to-luminous-vivid-orange: linear-gradient(135deg, rgba(252, 185, 0, 1) 0%, rgba(255, 105, 0, 1) 100%);
        --wp--preset--gradient--luminous-vivid-orange-to-vivid-red: linear-gradient(135deg, rgba(255, 105, 0, 1) 0%, rgb(207, 46, 46) 100%);
        --wp--preset--gradient--very-light-gray-to-cyan-bluish-gray: linear-gradient(135deg, rgb(238, 238, 238) 0%, rgb(169, 184, 195) 100%);
        --wp--preset--gradient--cool-to-warm-spectrum: linear-gradient(135deg, rgb(74, 234, 220) 0%, rgb(151, 120, 209) 20%, rgb(207, 42, 186) 40%, rgb(238, 44, 130) 60%, rgb(251, 105, 98) 80%, rgb(254, 248, 76) 100%);
        --wp--preset--gradient--blush-light-purple: linear-gradient(135deg, rgb(255, 206, 236) 0%, rgb(152, 150, 240) 100%);
        --wp--preset--gradient--blush-bordeaux: linear-gradient(135deg, rgb(254, 205, 165) 0%, rgb(254, 45, 45) 50%, rgb(107, 0, 62) 100%);
        --wp--preset--gradient--luminous-dusk: linear-gradient(135deg, rgb(255, 203, 112) 0%, rgb(199, 81, 192) 50%, rgb(65, 88, 208) 100%);
        --wp--preset--gradient--pale-ocean: linear-gradient(135deg, rgb(255, 245, 203) 0%, rgb(182, 227, 212) 50%, rgb(51, 167, 181) 100%);
        --wp--preset--gradient--electric-grass: linear-gradient(135deg, rgb(202, 248, 128) 0%, rgb(113, 206, 126) 100%);
        --wp--preset--gradient--midnight: linear-gradient(135deg, rgb(2, 3, 129) 0%, rgb(40, 116, 252) 100%);
        --wp--preset--font-size--small: 13px;
        --wp--preset--font-size--medium: 20px;
        --wp--preset--font-size--large: 36px;
        --wp--preset--font-size--x-large: 42px;
        --wp--preset--spacing--20: 0.44rem;
        --wp--preset--spacing--30: 0.67rem;
        --wp--preset--spacing--40: 1rem;
        --wp--preset--spacing--50: 1.5rem;
        --wp--preset--spacing--60: 2.25rem;
        --wp--preset--spacing--70: 3.38rem;
        --wp--preset--spacing--80: 5.06rem;
        --wp--preset--shadow--natural: 6px 6px 9px rgba(0, 0, 0, 0.2);
        --wp--preset--shadow--deep: 12px 12px 50px rgba(0, 0, 0, 0.4);
        --wp--preset--shadow--sharp: 6px 6px 0px rgba(0, 0, 0, 0.2);
        --wp--preset--shadow--outlined: 6px 6px 0px -3px rgba(255, 255, 255, 1), 6px 6px rgba(0, 0, 0, 1);
        --wp--preset--shadow--crisp: 6px 6px 0px rgba(0, 0, 0, 1);
    }

    :where(.is-layout-flex) {
        gap: 0.5em;
    }

    :where(.is-layout-grid) {
        gap: 0.5em;
    }

    body .is-layout-flex {
        display: flex;
    }

    .is-layout-flex {
        flex-wrap: wrap;
        align-items: center;
    }

    .is-layout-flex > :is( *, div) {
        margin: 0;
    }

    body .is-layout-grid {
        display: grid;
    }

    .is-layout-grid > :is( *, div) {
        margin: 0;
    }

    :where(.wp-block-columns.is-layout-flex) {
        gap: 2em;
    }

    :where(.wp-block-columns.is-layout-grid) {
        gap: 2em;
    }

    :where(.wp-block-post-template.is-layout-flex) {
        gap: 1.25em;
    }

    :where(.wp-block-post-template.is-layout-grid) {
        gap: 1.25em;
    }

    .has-black-color {
        color: var(--wp--preset--color--black) !important;
    }

    .has-cyan-bluish-gray-color {
        color: var(--wp--preset--color--cyan-bluish-gray) !important;
    }

    .has-white-color {
        color: var(--wp--preset--color--white) !important;
    }

    .has-pale-pink-color {
        color: var(--wp--preset--color--pale-pink) !important;
    }

    .has-vivid-red-color {
        color: var(--wp--preset--color--vivid-red) !important;
    }

    .has-luminous-vivid-orange-color {
        color: var(--wp--preset--color--luminous-vivid-orange) !important;
    }

    .has-luminous-vivid-amber-color {
        color: var(--wp--preset--color--luminous-vivid-amber) !important;
    }

    .has-light-green-cyan-color {
        color: var(--wp--preset--color--light-green-cyan) !important;
    }

    .has-vivid-green-cyan-color {
        color: var(--wp--preset--color--vivid-green-cyan) !important;
    }

    .has-pale-cyan-blue-color {
        color: var(--wp--preset--color--pale-cyan-blue) !important;
    }

    .has-vivid-cyan-blue-color {
        color: var(--wp--preset--color--vivid-cyan-blue) !important;
    }

    .has-vivid-purple-color {
        color: var(--wp--preset--color--vivid-purple) !important;
    }

    .has-black-background-color {
        background-color: var(--wp--preset--color--black) !important;
    }

    .has-cyan-bluish-gray-background-color {
        background-color: var(--wp--preset--color--cyan-bluish-gray) !important;
    }

    .has-white-background-color {
        background-color: var(--wp--preset--color--white) !important;
    }

    .has-pale-pink-background-color {
        background-color: var(--wp--preset--color--pale-pink) !important;
    }

    .has-vivid-red-background-color {
        background-color: var(--wp--preset--color--vivid-red) !important;
    }

    .has-luminous-vivid-orange-background-color {
        background-color: var(--wp--preset--color--luminous-vivid-orange) !important;
    }

    .has-luminous-vivid-amber-background-color {
        background-color: var(--wp--preset--color--luminous-vivid-amber) !important;
    }

    .has-light-green-cyan-background-color {
        background-color: var(--wp--preset--color--light-green-cyan) !important;
    }

    .has-vivid-green-cyan-background-color {
        background-color: var(--wp--preset--color--vivid-green-cyan) !important;
    }

    .has-pale-cyan-blue-background-color {
        background-color: var(--wp--preset--color--pale-cyan-blue) !important;
    }

    .has-vivid-cyan-blue-background-color {
        background-color: var(--wp--preset--color--vivid-cyan-blue) !important;
    }

    .has-vivid-purple-background-color {
        background-color: var(--wp--preset--color--vivid-purple) !important;
    }

    .has-black-border-color {
        border-color: var(--wp--preset--color--black) !important;
    }

    .has-cyan-bluish-gray-border-color {
        border-color: var(--wp--preset--color--cyan-bluish-gray) !important;
    }

    .has-white-border-color {
        border-color: var(--wp--preset--color--white) !important;
    }

    .has-pale-pink-border-color {
        border-color: var(--wp--preset--color--pale-pink) !important;
    }

    .has-vivid-red-border-color {
        border-color: var(--wp--preset--color--vivid-red) !important;
    }

    .has-luminous-vivid-orange-border-color {
        border-color: var(--wp--preset--color--luminous-vivid-orange) !important;
    }

    .has-luminous-vivid-amber-border-color {
        border-color: var(--wp--preset--color--luminous-vivid-amber) !important;
    }

    .has-light-green-cyan-border-color {
        border-color: var(--wp--preset--color--light-green-cyan) !important;
    }

    .has-vivid-green-cyan-border-color {
        border-color: var(--wp--preset--color--vivid-green-cyan) !important;
    }

    .has-pale-cyan-blue-border-color {
        border-color: var(--wp--preset--color--pale-cyan-blue) !important;
    }

    .has-vivid-cyan-blue-border-color {
        border-color: var(--wp--preset--color--vivid-cyan-blue) !important;
    }

    .has-vivid-purple-border-color {
        border-color: var(--wp--preset--color--vivid-purple) !important;
    }

    .has-vivid-cyan-blue-to-vivid-purple-gradient-background {
        background: var(--wp--preset--gradient--vivid-cyan-blue-to-vivid-purple) !important;
    }

    .has-light-green-cyan-to-vivid-green-cyan-gradient-background {
        background: var(--wp--preset--gradient--light-green-cyan-to-vivid-green-cyan) !important;
    }

    .has-luminous-vivid-amber-to-luminous-vivid-orange-gradient-background {
        background: var(--wp--preset--gradient--luminous-vivid-amber-to-luminous-vivid-orange) !important;
    }

    .has-luminous-vivid-orange-to-vivid-red-gradient-background {
        background: var(--wp--preset--gradient--luminous-vivid-orange-to-vivid-red) !important;
    }

    .has-very-light-gray-to-cyan-bluish-gray-gradient-background {
        background: var(--wp--preset--gradient--very-light-gray-to-cyan-bluish-gray) !important;
    }

    .has-cool-to-warm-spectrum-gradient-background {
        background: var(--wp--preset--gradient--cool-to-warm-spectrum) !important;
    }

    .has-blush-light-purple-gradient-background {
        background: var(--wp--preset--gradient--blush-light-purple) !important;
    }

    .has-blush-bordeaux-gradient-background {
        background: var(--wp--preset--gradient--blush-bordeaux) !important;
    }

    .has-luminous-dusk-gradient-background {
        background: var(--wp--preset--gradient--luminous-dusk) !important;
    }

    .has-pale-ocean-gradient-background {
        background: var(--wp--preset--gradient--pale-ocean) !important;
    }

    .has-electric-grass-gradient-background {
        background: var(--wp--preset--gradient--electric-grass) !important;
    }

    .has-midnight-gradient-background {
        background: var(--wp--preset--gradient--midnight) !important;
    }

    .has-small-font-size {
        font-size: var(--wp--preset--font-size--small) !important;
    }

    .has-medium-font-size {
        font-size: var(--wp--preset--font-size--medium) !important;
    }

    .has-large-font-size {
        font-size: var(--wp--preset--font-size--large) !important;
    }

    .has-x-large-font-size {
        font-size: var(--wp--preset--font-size--x-large) !important;
    }

    :where(.wp-block-post-template.is-layout-flex) {
        gap: 1.25em;
    }

    :where(.wp-block-post-template.is-layout-grid) {
        gap: 1.25em;
    }

    :where(.wp-block-columns.is-layout-flex) {
        gap: 2em;
    }

    :where(.wp-block-columns.is-layout-grid) {
        gap: 2em;
    }

    :root :where(.wp-block-pullquote) {
        font-size: 1.5em;
        line-height: 1.6;
    }
    </style>
    <link rel='stylesheet' id='contact-form-7-css' href='https://csra.fm/wp-content/plugins/contact-form-7/includes/css/styles.css?ver=6.0.3' type='text/css' media='all'/>
    <link rel='stylesheet' id='wp-pagenavi-css' href='https://csra.fm/wp-content/plugins/wp-pagenavi/pagenavi-css.css?ver=2.70' type='text/css' media='all'/>
    <script type="text/javascript" src="https://csra.fm/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>
    <script type="text/javascript" src="https://csra.fm/wp-includes/js/jquery/jquery-migrate.min.js?ver=3.4.1" id="jquery-migrate-js"></script>
    <script type="text/javascript" src="https://csra.fm/wp-content/themes/CSRA/js/jquery.mobile/jquery.mobile.js?ver=6.7.2" id="jquery-mobile-js"></script>
    <link rel="https://api.w.org/" href="https://csra.fm/wp-json/"/>
    <link rel="alternate" title="JSON" type="application/json" href="https://csra.fm/wp-json/wp/v2/pages/2"/>
    <link rel="canonical" href="https://csra.fm/stationlist/"/>
    <link rel='shortlink' href='https://csra.fm/?p=2'/>
    <link rel="alternate" title="oEmbed (JSON)" type="application/json+oembed" href="https://csra.fm/wp-json/oembed/1.0/embed?url=https%3A%2F%2Fcsra.fm%2Fstationlist%2F"/>
    <link rel="alternate" title="oEmbed (XML)" type="text/xml+oembed" href="https://csra.fm/wp-json/oembed/1.0/embed?url=https%3A%2F%2Fcsra.fm%2Fstationlist%2F&#038;format=xml"/>
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico"/>
</head>
<body id="csra">

    <div id="home" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/765fm/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMアップルの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/765fm.png" alt="FMアップル">
                            </div>
                            <h1>FMアップル</h1>
                            <p>札幌市豊平区</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMアップルの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://765fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30090&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/eniwa/" class="stationlist" title="月 6:00-19:00/20:00-0:00
                    火-金 0:00-19:00/20:00-0:00
                    土 0:00-19:00
                    日 10:00-16:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/eniwa.png" alt="e-niwaFM">
                            </div>
                            <h1>e-niwaFM</h1>
                            <p>恵庭市</p>
                            <!--<p class="timedata">月 6:00-19:00/20:00-0:00
                            火-金 0:00-19:00/20:00-0:00
                            土 0:00-19:00
                            日 10:00-16:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.e-niwa.tv/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/eniwa.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmotaru/" class="stationlist" title="月  8:00-24:30  
                    火  8:00-24:30  
                    水  8:00-24:30  
                    木  8:00-24:30  
                    金  8:00-24:30  
                    土  10:00-24:30  
                    日  10:00-21:00

                    偶数週、奇数週で配信時間が異なります。
                    詳しくはHPをご確認ください。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmotaru.png" alt="FMおたる">
                            </div>
                            <h1>FMおたる</h1>
                            <p>小樽市</p>
                            <!--<p class="timedata">月  8:00-24:30  
                            火  8:00-24:30  
                            水  8:00-24:30  
                            木  8:00-24:30  
                            金  8:00-24:30  
                            土  10:00-24:30  
                            日  10:00-21:00

                            偶数週、奇数週で配信時間が異なります。
                            詳しくはHPをご確認ください。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmotaru.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/otaru.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/shiroishi/" class="stationlist" title="都合により現在、配信を停止しております">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/shiroishi.png" alt="エフエムしろいし">
                            </div>
                            <h1>エフエムしろいし</h1>
                            <p>札幌市</p>
                            <!--<p class="timedata">都合により現在、配信を停止しております</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.830.fm/" target="_blank" class="site">ホームページ</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/wi-radio/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのwi-radioの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/wi-radio.png" alt="Wi-radio">
                            </div>
                            <h1>Wi-radio</h1>
                            <p>伊達市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのwi-radioの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.date-kanko.jp/wiradio/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30087&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/763fm/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/763fm.png" alt="FMねむろ">
                            </div>
                            <h1>FMねむろ</h1>
                            <p>根室市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmnemuro.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30045&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmabashiri/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmabashiri.png" alt="FMあばしり">
                            </div>
                            <h1>FMあばしり</h1>
                            <p>網走市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.lia-abashiri.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30058/FMABASHIRI" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/sapporomura-radio/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのさっぽろ村ラジオの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/sapporomura-radio.png" alt="さっぽろ村ラジオ">
                            </div>
                            <h1>さっぽろ村ラジオ</h1>
                            <p>札幌市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのさっぽろ村ラジオの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.fm813.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30032/さっぽろ村ラジオ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmmaple/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMメイプルの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmmaple.png" alt="FMメイプル">
                            </div>
                            <h1>FMメイプル</h1>
                            <p>北広島市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMメイプルの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.facebook.com/fm.maple79.9" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30015/FMメイプル" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/hamanasufm761/" class="stationlist" title="「放送を聞く」をクリックし、ListenRadio のFMはまなすの番組表ページへ。
                    左上のListenRadio のロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/hamanasufm761.png" alt="FMはまなす">
                            </div>
                            <h1>FMはまなす</h1>
                            <p>岩見沢市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、ListenRadio のFMはまなすの番組表ページへ。
                            左上のListenRadio のロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://fm761.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://listenradio.jp/Home/ProgramSchedule/30004/FMはまなす" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/sankakuyama/" class="stationlist" title="月-木 0:00-19:00/21:00-24:00
                    金 0:00-20:00/21:00-24:00
                    土 0:00-18:00/21:00-24:00
                    日 0:00-6:00
                    ※コンサドーレ札幌のアウェイ戦の中継を除く
                    ※ネット休止時間
                    毎週月曜日～金曜日の18時から19時
                    毎週日曜日の8時～12時、20時～22時">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/sankakuyama.png" alt="三角山放送局">
                            </div>
                            <h1>三角山放送局</h1>
                            <p>札幌市西区</p>
                            <!--<p class="timedata">月-木 0:00-19:00/21:00-24:00
                            金 0:00-20:00/21:00-24:00
                            土 0:00-18:00/21:00-24:00
                            日 0:00-6:00
                            ※コンサドーレ札幌のアウェイ戦の中継を除く
                            ※ネット休止時間
                            毎週月曜日～金曜日の18時から19時
                            毎週日曜日の8時～12時、20時～22時</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.sankakuyama.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30005&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/jaga/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFM JAGAの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                    月-金 7:00-20:00/22:00-24:00
                    土 8:00-17:00/20:00/24:00
                    日 9:00-13:00/16:55-17:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/jaga.png" alt="FM JAGA">
                            </div>
                            <h1>FM JAGA</h1>
                            <p>帯広市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFM JAGAの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                            月-金 7:00-20:00/22:00-24:00
                            土 8:00-17:00/20:00/24:00
                            日 9:00-13:00/16:55-17:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.jaga.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30016&amp;cap=10005&amp;arp=1" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmwing/" class="stationlist" title="月-金 7:00-翌5:00
                    土 9:00-翌5:00
                    日 9:00-20:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmwing.png" alt="FM WING">
                            </div>
                            <h1>FM WING</h1>
                            <p>帯広市</p>
                            <!--<p class="timedata">月-金 7:00-翌5:00
                            土 9:00-翌5:00
                            日 9:00-20:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmwing.com/index.html" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fmwing.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/dramacity/" class="stationlist" title="月-金 9:00-22:00
                    土 15:00-22:30
                    日 9:00-21:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/dramacity.png" alt="RADIOワンダーストレージFMドラマシティ">
                            </div>
                            <h1>RADIOワンダーストレージFMドラマシティ</h1>
                            <p>札幌市厚別区</p>
                            <!--<p class="timedata">月-金 9:00-22:00
                            土 15:00-22:30
                            日 9:00-21:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://776.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="https://live.776.fm/" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm946/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm946.png" alt="FMくしろ">
                            </div>
                            <h1>FMくしろ</h1>
                            <p>釧路市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm946.com" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/FmKushiro.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/wappy761/" class="stationlist" title="月-金 7:30-20:00
                    土・日 8:00-13:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/wappy761.png" alt="FMわっぴ〜">
                            </div>
                            <h1>FMわっぴ〜</h1>
                            <p>稚内市</p>
                            <!--<p class="timedata">月-金 7:30-20:00
                            土・日 8:00-13:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://wappy761.jp" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fmwappy.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm837/" class="stationlist" title="月 8:00-17:00/20:00-23:00
                    火 8:00-17:00/20:00-23:00
                    水(第1・3・5) 8:00-14:30/15:00-17:00/18:00-19:00/20:00-23:00
                    水(第2・4) 8:00-17:00/18:00-19:00/20:00-23:00
                    木 8:00-11:00/12:00-17:00/20:00-23:00
                    金(第1・2・3・5) 8:00-11:00/14:00-15:00/16:00-17:00/19:00-23:00
                    金(第4) 8:00-11:00/11:30-12:00/14:00-15:00/16:00-17:00/19:00-23:00
                    土 10:00-12:00/18:00-20:00/24:00-25:00
                    日 9:00-11:00/11:45-18:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm837.png" alt="FMりべーる">
                            </div>
                            <h1>FMりべーる</h1>
                            <p>旭川市</p>
                            <!--<p class="timedata">月 8:00-17:00/20:00-23:00
                            火 8:00-17:00/20:00-23:00
                            水(第1・3・5) 8:00-14:30/15:00-17:00/18:00-19:00/20:00-23:00
                            水(第2・4) 8:00-17:00/18:00-19:00/20:00-23:00
                            木 8:00-11:00/12:00-17:00/20:00-23:00
                            金(第1・2・3・5) 8:00-11:00/14:00-15:00/16:00-17:00/19:00-23:00
                            金(第4) 8:00-11:00/11:30-12:00/14:00-15:00/16:00-17:00/19:00-23:00
                            土 10:00-12:00/18:00-20:00/24:00-25:00
                            日 9:00-11:00/11:45-18:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm837.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fm837.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radioniseko/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radioniseko.png" alt="ラジオニセコ">
                            </div>
                            <h1>ラジオニセコ</h1>
                            <p>ニセコ町</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://radioniseko.jp" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.radioniseko.jp/asx/radioniseko_24k.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radiokaros/" class="stationlist" title="月 7:00-24:00
                    火 7:00-21:00
                    水-金 7:00-24:00
                    土 7:00-18:00/20:00-24:00
                    日 9:00-23:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radiokaros.png" alt="ラジオカロスサッポロ">
                            </div>
                            <h1>ラジオカロスサッポロ</h1>
                            <p>札幌市</p>
                            <!--<p class="timedata">月 7:00-24:00
                            火 7:00-21:00
                            水-金 7:00-24:00
                            土 7:00-18:00/20:00-24:00
                            日 9:00-23:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.radiokaros.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/radiokaros.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="tohoku" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/befm765/" class="stationlist" title="月～金　11:00-22:00
                    土　15:00-22:00
                    日　17:00-24:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/befm765.png" alt="BeFM">
                            </div>
                            <h1>BeFM</h1>
                            <p>八戸市</p>
                            <!--<p class="timedata">月～金　11:00-22:00
                            土　15:00-22:00
                            日　17:00-24:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.befm.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/befm.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm791/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm791.png" alt="鹿角きりたんぽFM">
                            </div>
                            <h1>鹿角きりたんぽFM</h1>
                            <p>鹿角市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fm791.net/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/kiritampo.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/cassiopeia/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのカシオペアFMの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/cassiopeia.png" alt="カシオペアFM">
                            </div>
                            <h1>カシオペアFM</h1>
                            <p>二戸市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのカシオペアFMの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://779.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30050&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmtaihaku/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmtaihaku.png" alt="FMたいはく">
                            </div>
                            <h1>FMたいはく</h1>
                            <p>仙台市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-t.net/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/taihaku.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmkesennuma/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのラヂオけせんぬまの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmkesennuma.png" alt="ラヂオけせんぬま">
                            </div>
                            <h1>ラヂオけせんぬま</h1>
                            <p>気仙沼市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのラヂオけせんぬまの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://kfm775.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30094&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmtsubakidai/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのエフエム椿台の番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmtsubakidai.png" alt="エフエム椿台">
                            </div>
                            <h1>エフエム椿台</h1>
                            <p>秋田市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのエフエム椿台の番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm796.com" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30014&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radiomorioka/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのラヂオもりおかの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                    月-木 7:00-11:30/16:30-20:00
                    金 7:00-11:30/16:00-21:45">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radiomorioka.png" alt="ラヂオもりおか">
                            </div>
                            <h1>ラヂオもりおか</h1>
                            <p>盛岡市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのラヂオもりおかの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                            月-木 7:00-11:30/16:30-20:00
                            金 7:00-11:30/16:00-21:45</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://radiomorioka.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30017&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radio3/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radio3.png" alt="ラジオ3">
                            </div>
                            <h1>ラジオ3</h1>
                            <p>仙台市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.radio3.jp/index2.html" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30007&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-mot/" class="stationlist" title="月-金 7:00-15:00/17:00-22:00/23:00-25:00
                    土 10:00-11:00/16:00-23:30
                    日 9:00-11:00/15:30-25:00

                    2017年10月1日（日）　午前8：00～正午の間、
                    「本宮市総合防災訓練」の実施に伴い、
                    訓練への参加及び中継放送のため、
                    上記の時間帯の放送内容が変更となります。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-mot.png" alt="エフエム モットコム">
                            </div>
                            <h1>エフエム モットコム</h1>
                            <p>本宮市</p>
                            <!--<p class="timedata">月-金 7:00-15:00/17:00-22:00/23:00-25:00
                            土 10:00-11:00/16:00-23:30
                            日 9:00-11:00/15:30-25:00

                            2017年10月1日（日）　午前8：00～正午の間、
                            「本宮市総合防災訓練」の実施に伴い、
                            訓練への参加及び中継放送のため、
                            上記の時間帯の放送内容が変更となります。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-mot.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fmmotcom.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-iwaki/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-iwaki.png" alt="FMいわき">
                            </div>
                            <h1>FMいわき</h1>
                            <p>いわき市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-iwaki.co.jp/cgi-bin/WebObjects/1201dac04a1.woa/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fm-iwaki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/yutopia/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30030/FMゆーとぴあ

                    24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/yutopia.png" alt="FMゆーとぴあ">
                            </div>
                            <h1>FMゆーとぴあ</h1>
                            <p>湯沢市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30030/FMゆーとぴあ

                            24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.yutopia.or.jp/%7Efm763/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/FmYutopia.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmyokote/" class="stationlist" title="月-木 7:00-9:00/10:00-14:00/16:30-19:00/21:00-22:00
                    金 7:00-16:00/16:30-22:00
                    土 8:00-13:00
                    日 9:00-13:00/18:00-19:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmyokote.png" alt="横手かまくらエフエム">
                            </div>
                            <h1>横手かまくらエフエム</h1>
                            <p>横手市</p>
                            <!--<p class="timedata">月-木 7:00-9:00/10:00-14:00/16:30-19:00/21:00-22:00
                            金 7:00-16:00/16:30-22:00
                            土 8:00-13:00
                            日 9:00-13:00/18:00-19:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmyokote.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/yokote.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmmiyako/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmmiyako.png" alt="みやこハーバーラジオ">
                            </div>
                            <h1>みやこハーバーラジオ</h1>
                            <p>宮古市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://miyakofm.com" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/FmMiyako.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm764i/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm764i.png" alt="ラジオ石巻">
                            </div>
                            <h1>ラジオ石巻</h1>
                            <p>石巻市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm764.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/RadioIshinomaki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/bay-wave/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのBAY WAVEの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                    月-金 9:00-20:00
                    土 12:00-15:00/16:55-19:00/22:00-24:00
                    ※サッカー生中継による一部変更もあります。
                    日 11:00-13:00/22:00-23:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/bay-wave.png" alt="BAY WAVE">
                            </div>
                            <h1>BAY WAVE</h1>
                            <p>塩釜市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのBAY WAVEの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                            月-金 9:00-20:00
                            土 12:00-15:00/16:55-19:00/22:00-24:00
                            ※サッカー生中継による一部変更もあります。
                            日 11:00-13:00/22:00-23:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.bay-wave.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30056&amp;cap=10005&amp;arp=2" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm797/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのfmいずみの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm797.png" alt="fmいずみ">
                            </div>
                            <h1>fmいずみ</h1>
                            <p>仙台市泉区</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのfmいずみの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm797.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30018/fmいずみ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/ringo-radio/" class="stationlist" title="3月31日で閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/ringo-radio.png" alt="りんごFM">
                            </div>
                            <h1>りんごFM</h1>
                            <p>山元町</p>
                            <!--<p class="timedata">3月31日で閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://ringo-radio.cocolog-nifty.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/RingoFM.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm_natori801mhz/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm_natori801mhz.png" alt="なとらじ">
                            </div>
                            <h1>なとらじ</h1>
                            <p>名取市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.natori801.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/Natoraji.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/minamisomasaigaifm/" class="stationlist" title="閉局しました。

                    ※毎週 日 23:00～翌 月 8:30まで、メンテナンスのため休止
                    ※12月27日（土）18:00から1月5日（月）9:00まで、年末年始につき放送休止。なお、災害時など緊急の場合には、放送を再開し、情報を提供していく予定です。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/minamisomasaigaifm.png" alt="南相馬ひばりエフエム">
                            </div>
                            <h1>南相馬ひばりエフエム</h1>
                            <p>南相馬市</p>
                            <!--<p class="timedata">閉局しました。

                            ※毎週 日 23:00～翌 月 8:30まで、メンテナンスのため休止
                            ※12月27日（土）18:00から1月5日（月）9:00まで、年末年始につき放送休止。なお、災害時など緊急の場合には、放送を再開し、情報を提供していく予定です。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://minamisomasaigaifm.hostei.com/index.html" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/MinamisomaFM.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/kocofm/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/kocofm.png" alt="郡山コミュニティ放送">
                            </div>
                            <h1>郡山コミュニティ放送</h1>
                            <p>郡山市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.kocofm.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/kocofm.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/onagawafm/" class="stationlist" title="3月31日で閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/onagawafm.png" alt="女川さいがいFM">
                            </div>
                            <h1>女川さいがいFM</h1>
                            <p>女川町</p>
                            <!--<p class="timedata">3月31日で閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://onagawafm.jp/" target="_blank" class="site">ホームページ</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/rikuzentakata-fm/" class="stationlist" title="3月16日閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/rikuzentakata-fm.png" alt="陸前高田災害FM">
                            </div>
                            <h1>陸前高田災害FM</h1>
                            <p>陸前高田市</p>
                            <!--<p class="timedata">3月16日閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://rikuzentakata-fm.blogspot.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/rikuzentakataFM.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/odagaimasafm/" class="stationlist" title="閉局しました。

                    月・火・木 8:00-9:00/10:00-10:20/18:30-19:30
                    水 8:00-9:00/10:00-10:20/11:00-11:30/18:30-19:30
                    金 8:00-9:00/10:00-10:20/18:30-20:30
                    土 12:00-13:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/odagaimasafm.png" alt="富岡臨時災害FM局（おだがいさまFM）">
                            </div>
                            <h1>富岡臨時災害FM局（おだがいさまFM）</h1>
                            <p>富岡町</p>
                            <!--<p class="timedata">閉局しました。

                            月・火・木 8:00-9:00/10:00-10:20/18:30-19:30
                            水 8:00-9:00/10:00-10:20/11:00-11:30/18:30-19:30
                            金 8:00-9:00/10:00-10:20/18:30-20:30
                            土 12:00-13:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.gurutto-koriyama.com/detail/index_213.html" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/OdagaisamaFM.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmaozora/" class="stationlist" title="3月24日で閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmaozora.png" alt="亘理臨時災害FM局（FMあおぞら）">
                            </div>
                            <h1>亘理臨時災害FM局（FMあおぞら）</h1>
                            <p>亘理町</p>
                            <!--<p class="timedata">3月24日で閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.town.watari.miyagi.jp/index.cfm/22,21308,126,html" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/aozora.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/otsuchi/" class="stationlist" title="3月18日で閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/otsuchi.png" alt="おおつちさいがいエフエム">
                            </div>
                            <h1>おおつちさいがいエフエム</h1>
                            <p>大槌町</p>
                            <!--<p class="timedata">3月18日で閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.town.otsuchi.iwate.jp/" target="_blank" class="site">ホームページ</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/kamaishi/" class="stationlist" title="3月31日で閉局">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/kamaishi.png" alt="釜石災害FM">
                            </div>
                            <h1>釜石災害FM</h1>
                            <p>釜石市</p>
                            <!--<p class="timedata">3月31日で閉局</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.city.kamaishi.iwate.jp/index.cfm/12,18557,121,html" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/kamaishi.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmasmo/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmasmo.png" alt="FMあすも">
                            </div>
                            <h1>FMあすも</h1>
                            <p>一関市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://emus.jimdo.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://fmasmo.fmplapla.com/player/" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="kanto" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/takahagi/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/takahagi.png" alt="たかはぎFM">
                            </div>
                            <h1>たかはぎFM</h1>
                            <p>高萩市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.t768.net" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/takahagi.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/kawaguchi/" class="stationlist" title="6:00～25:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/kawaguchi.png" alt="FM Kawaguchi">
                            </div>
                            <h1>FM Kawaguchi</h1>
                            <p>川口市</p>
                            <!--<p class="timedata">6:00～25:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm856.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/kawaguchi.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmuu/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmuu.png" alt="FM-UU">
                            </div>
                            <h1>FM-UU</h1>
                            <p>牛久市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmuu.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fmuu.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/hitachi/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/hitachi.png" alt="FMひたち">
                            </div>
                            <h1>FMひたち</h1>
                            <p>日立市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.hfm.or.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/hitachi.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/koshigaya/" class="stationlist" title="7月17日から本格運用。

                    「放送を聞く」をクリックし、リスラジのこしがやエフエムの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/koshigaya.png" alt="こしがやエフエム">
                            </div>
                            <h1>こしがやエフエム</h1>
                            <p>越谷市</p>
                            <!--<p class="timedata">7月17日から本格運用。

                            「放送を聞く」をクリックし、リスラジのこしがやエフエムの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://koshigaya.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30096&amp;cap=10005&amp;arp=3" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/775fm/" class="stationlist" title="24時間放送

                    「放送を聞く」をクリックし、リスラジのTokyo Star Radioの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/775fm.png" alt="Tokyo Star Radio">
                            </div>
                            <h1>Tokyo Star Radio</h1>
                            <p>八王子市</p>
                            <!--<p class="timedata">24時間放送

                            「放送を聞く」をクリックし、リスラジのTokyo Star Radioの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://775fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30081/Tokyo Star Radio" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmsetagaya/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのエフエム世田谷の番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmsetagaya.png" alt="エフエム世田谷">
                            </div>
                            <h1>エフエム世田谷</h1>
                            <p>世田谷区</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのエフエム世田谷の番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://fmsetagaya.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30027/エフエム世田谷" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radio-fuchues/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのラジオフチューズの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radio-fuchues.png" alt="ラジオフチューズ">
                            </div>
                            <h1>ラジオフチューズ</h1>
                            <p>府中市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのラジオフチューズの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.radio-fuchues.tokyo/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30059/ラジオフチューズ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/marinefm/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/marinefm.png" alt="マリンFM">
                            </div>
                            <h1>マリンFM</h1>
                            <p>横浜市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.marine-fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30065/マリンFM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/775livelyfm/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/775livelyfm.png" alt="775ライブリーFM">
                            </div>
                            <h1>775ライブリーFM</h1>
                            <p>朝霞市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://775fm.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/smile.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fukaya-fm/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMふっかちゃんの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fukaya-fm.png" alt="FMふっかちゃん">
                            </div>
                            <h1>FMふっかちゃん</h1>
                            <p>深谷市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMふっかちゃんの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.fukaya-fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30047/FMふっかちゃん" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-watarase/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMわたらせの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-watarase.png" alt="FMわたらせ">
                            </div>
                            <h1>FMわたらせ</h1>
                            <p>加須市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMわたらせの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://fm-watarase.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30048/FM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmpalulun/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30022/FMぱるるん

                    月 6:00-27:00
                    火 6:00-27:00
                    水 7:00-14:00/16:00-27:00
                    木 6:00-27:00
                    金 6:00-27:00
                    土 5:00-29:00
                    日 5:00-26:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmpalulun.png" alt="FMぱるるん">
                            </div>
                            <h1>FMぱるるん</h1>
                            <p>水戸市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30022/FMぱるるん

                            月 6:00-27:00
                            火 6:00-27:00
                            水 7:00-14:00/16:00-27:00
                            木 6:00-27:00
                            金 6:00-27:00
                            土 5:00-29:00
                            日 5:00-26:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmpalulun.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/fmpalulun.asx" target="_blank" class="stm">放送を聞く</a>
                        <a href="http://www.fmpalulun.co.jp/listen/" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm767f/" class="stationlist" title="月-木 8:00-19:00
                    金 8:00-24:00
                    土 0:00-18:00
                    日 9:00-18:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm767f.png" alt="フラワーラジオ">
                            </div>
                            <h1>フラワーラジオ</h1>
                            <p>鴻巣市</p>
                            <!--<p class="timedata">月-木 8:00-19:00
                            金 8:00-24:00
                            土 0:00-18:00
                            日 9:00-18:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.fm767.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.fm767.com/flower_64k.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/beachfm/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30028/湘南ビーチFM

                    24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/beachfm.png" alt="湘南ビーチFM">
                            </div>
                            <h1>湘南ビーチFM</h1>
                            <p>逗子市・葉山町</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30028/湘南ビーチFM

                            24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.beachfm.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30028/FM" target="_blank" class="stm">放送を聞く</a>
                        <a href="https://www.beachfm.co.jp/video/" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/redswave/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30008/REDSWAVE

                    月-日 6:00-25:00
                    ※浦和レッズ戦実況中継番組の再放送を除く。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/redswave.png" alt="REDS WAVE">
                            </div>
                            <h1>REDS WAVE</h1>
                            <p>さいたま市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30008/REDSWAVE

                            月-日 6:00-25:00
                            ※浦和レッズ戦実況中継番組の再放送を除く。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://redswave.com" target="_blank" class="site">ホームページ</a>
                        <a href="http://redswave.com/simul.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radio-tsukuba/" class="stationlist" title="24時間
                    ※毎週月2:00-5:00メンテナンスのため放送停止">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radio-tsukuba.png" alt="ラヂオつくば">
                            </div>
                            <h1>ラヂオつくば</h1>
                            <p>つくば市</p>
                            <!--<p class="timedata">24時間
                            ※毎週月2:00-5:00メンテナンスのため放送停止</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://radio-tsukuba.net" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/tsukuba.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm844/" class="stationlist" title="24時間
                    ※毎週 月0:00-月5:00まで、メンテナンスのため休止">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm844.png" alt="エフエムたちかわ">
                            </div>
                            <h1>エフエムたちかわ</h1>
                            <p>立川市</p>
                            <!--<p class="timedata">24時間
                            ※毎週 月0:00-月5:00まで、メンテナンスのため休止</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm844.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fm-tachikawa.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/kawasakifm/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30046/かわさきFM

                    24時間
                    ※都合により変更する場合があります。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/kawasakifm.png" alt="かわさきFM">
                            </div>
                            <h1>かわさきFM</h1>
                            <p>川崎市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30046/かわさきFM

                            24時間
                            ※都合により変更する場合があります。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.kawasakifm.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/kawasaki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-totsuka/" class="stationlist" title="24時間

                    「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30064/FM戸塚">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-totsuka.png" alt="FM戸塚">
                            </div>
                            <h1>FM戸塚</h1>
                            <p>横浜市</p>
                            <!--<p class="timedata">24時間

                            「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30064/FM戸塚</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-totsuka.com" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/totsuka.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/chofu-fm/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30039/調布FM

                    24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/chofu-fm.png" alt="調布FM">
                            </div>
                            <h1>調布FM</h1>
                            <p>調布市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30039/調布FM

                            24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.chofu-fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/chofu_fm.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/maebashi/" class="stationlist" title="24時間
                    ※J-WAVE配信番組を除く。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/maebashi.png" alt="まえばしCITYエフエム">
                            </div>
                            <h1>まえばしCITYエフエム</h1>
                            <p>前橋市</p>
                            <!--<p class="timedata">24時間
                            ※J-WAVE配信番組を除く。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.maebashi.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://radio.maebashi.fm:8080/mwave" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/kfm789/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30031/かつしかFM

                    24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/kfm789.png" alt="かつしかFM">
                            </div>
                            <h1>かつしかFM</h1>
                            <p>葛飾区</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30031/かつしかFM

                            24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.kfm789.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/katsushika.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmsagami/" class="stationlist" title="月-金 5:00-26:00
                    土・日 7:00-26:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmsagami.png" alt="エフエムさがみ">
                            </div>
                            <h1>エフエムさがみ</h1>
                            <p>相模原市</p>
                            <!--<p class="timedata">月-金 5:00-26:00
                            土・日 7:00-26:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmsagami.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.fmsagami.co.jp/asx/fmsagami.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/792fm/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/792fm.png" alt="レインボータウンFM">
                            </div>
                            <h1>レインボータウンFM</h1>
                            <p>江東区</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.792fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/rainbowtown.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmkaon/" class="stationlist" title="「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                    http://listenradio.jp/Home/ProgramSchedule/30057/FMカオン

                    24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmkaon.png" alt="FM kaon">
                            </div>
                            <h1>FM kaon</h1>
                            <p>海老名市</p>
                            <!--<p class="timedata">「放送を聞く」で再生できない方は、下記のリスラジアドレスにアクセスしてください。
                            http://listenradio.jp/Home/ProgramSchedule/30057/FMカオン

                            24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmkaon.com/" target="_blank" class="site">ホームページ</a>
                        <a href="mms://hdv.nkansai.tv/kaon" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="tokai" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/cty-fm/" class="stationlist" title="7:00-10:00/12:00-19:00
                    ※ただし曜日により変動します。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/cty-fm.png" alt="CTY-FM">
                            </div>
                            <h1>CTY-FM</h1>
                            <p>四日市市</p>
                            <!--<p class="timedata">7:00-10:00/12:00-19:00
                            ※ただし曜日により変動します。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://cty-fm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="https://fmplapla.com/fmyokkaichi/" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-egao/" class="stationlist" title="月-土 24時間
                    日 5:00-27:00
                    ☆上記放送時間以外にも、臨時災害放送・特別番組など「羽根スタジオ（特設スタジオを含む）」から放送する番組に関しては全て配信されます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-egao.png" alt="エフエムEGAO">
                            </div>
                            <h1>エフエムEGAO</h1>
                            <p>岡崎市</p>
                            <!--<p class="timedata">月-土 24時間
                            日 5:00-27:00
                            ☆上記放送時間以外にも、臨時災害放送・特別番組など「羽根スタジオ（特設スタジオを含む）」から放送する番組に関しては全て配信されます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fm-egao.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.simulradio.info/asx/FmOkazaki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/okazaki/" class="stationlist" title="月-土 24時間
                    日 5:00-27:00
                    ☆上記放送時間以外にも、臨時災害放送・特別番組など「羽根スタジオ（特設スタジオを含む）」から放送する番組に関しては全て配信されます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/okazaki.png" alt="FMおかざき">
                            </div>
                            <h1>FMおかざき</h1>
                            <p>岡崎市</p>
                            <!--<p class="timedata">月-土 24時間
                            日 5:00-27:00
                            ☆上記放送時間以外にも、臨時災害放送・特別番組など「羽根スタジオ（特設スタジオを含む）」から放送する番組に関しては全て配信されます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmokazaki.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/FmOkazaki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/838fm/" class="stationlist" title="5:00-25:00（毎日）

                    「放送を聞く」をクリックし、リスラジのPitch FMの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/838fm.png" alt="Pitch FM">
                            </div>
                            <h1>Pitch FM</h1>
                            <p>刈谷市</p>
                            <!--<p class="timedata">5:00-25:00（毎日）

                            「放送を聞く」をクリックし、リスラジのPitch FMの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.838.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="https://fmplapla.com/pitchfm/" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="hokushinetsu" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/fm761/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm761.png" alt="ラジオ・ミュー">
                            </div>
                            <h1>ラジオ・ミュー</h1>
                            <p>黒部市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm761.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30006/ラジオ・ミュー" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmn1/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmn1.png" alt="えふえむ・エヌ・ワン">
                            </div>
                            <h1>えふえむ・エヌ・ワン</h1>
                            <p>野々市市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmn1.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="https://www.fmn1.jp/netaudio.html" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/harbor779/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのハーバーステーションの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                    月-金 8:00-20:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/harbor779.png" alt="ハーバーステーション">
                            </div>
                            <h1>ハーバーステーション</h1>
                            <p>敦賀市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのハーバーステーションの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                            月-金 8:00-20:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://harbor779.com" target="_blank" class="site">ホームページ</a>
                        <a href="https://listenradio.jp/Home/ProgramSchedule/30012/FM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/azuminofm/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/azuminofm.png" alt="あづみ野FM">
                            </div>
                            <h1>あづみ野FM</h1>
                            <p>安曇野市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.azuminofm.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/azumino.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="kinki" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/radiocafe/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radiocafe.png" alt="京都三条ラジオカフェ">
                            </div>
                            <h1>京都三条ラジオカフェ</h1>
                            <p>京都市中京区</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://radiocafe.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/radiocafe.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmtango/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmtango.png" alt="FMたんご">
                            </div>
                            <h1>FMたんご</h1>
                            <p>京丹後市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fm-tango.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30073/FM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmmoov/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmmoov.png" alt="FM MOOV KOBE">
                            </div>
                            <h1>FM MOOV KOBE</h1>
                            <p>神戸市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-moov.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fmmoov.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radiosweet/" class="stationlist" title="テスト配信中">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radiosweet.png" alt="Radio Sweet">
                            </div>
                            <h1>Radio Sweet</h1>
                            <p>東近江市</p>
                            <!--<p class="timedata">テスト配信中</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.sweet815.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30061/ラジオスイート" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm805/" class="stationlist" title="24時間配信">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm805.png" alt="805たんば">
                            </div>
                            <h1>805たんば</h1>
                            <p>丹波市</p>
                            <!--<p class="timedata">24時間配信</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.tanba.info/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fm805.asx" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/radiomixkyoto/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/radiomixkyoto.png" alt="RADIO MIX KYOTO">
                            </div>
                            <h1>RADIO MIX KYOTO</h1>
                            <p>京都市北区</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://radiomix.kyoto/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/radiomixkyoto.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmotokuni/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmotokuni.png" alt="FMおとくに">
                            </div>
                            <h1>FMおとくに</h1>
                            <p>乙訓地域</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fm-otokuni.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30063/FM" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fukuchiyama/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fukuchiyama.png" alt="FM丹波">
                            </div>
                            <h1>FM丹波</h1>
                            <p>福知山市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fukuchiyama.fm-tanba.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://fukuchiyama.fm-tanba.jp/simul.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/senri-fm/" class="stationlist" title="24時間

                    「放送を聞く」をクリックし、リスラジのFM千里の番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/senri-fm.png" alt="FM 千里">
                            </div>
                            <h1>FM 千里</h1>
                            <p>豊中市</p>
                            <!--<p class="timedata">24時間

                            「放送を聞く」をクリックし、リスラジのFM千里の番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.senri-fm.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30048&amp;cap=10005&amp;arp=6" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/tcc117/" class="stationlist" title="地上波を終了し、インターネット放送局として再出発

                    土 12:00-20:00
                    日-金 12:00-20:00(土曜日の再放送)">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/tcc117.png" alt="エフエムわいわい">
                            </div>
                            <h1>エフエムわいわい</h1>
                            <p>神戸市</p>
                            <!--<p class="timedata">地上波を終了し、インターネット放送局として再出発

                            土 12:00-20:00
                            日-金 12:00-20:00(土曜日の再放送)</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://tcc117.jp/fmyy/" target="_blank" class="site">ホームページ</a>
                        <a href="http://tcc117.jp/fmyy/asx/fmyy.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/764/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/764.png" alt="FMジャングル">
                            </div>
                            <h1>FMジャングル</h1>
                            <p>豊岡市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.764.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/jungle.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/banban/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/banban.png" alt="BAN-BANラジオ">
                            </div>
                            <h1>BAN-BANラジオ</h1>
                            <p>加古川市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.banban.jp/radio/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/banban.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/816fm/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/816fm.png" alt="FMはしもと">
                            </div>
                            <h1>FMはしもと</h1>
                            <p>橋本市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://816.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/hasimoto.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="chugokushikoku" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/darazfm/" class="stationlist" title="24時間
                    ※FM802配信番組、ガイナーレ鳥取 サッカー中継を除く">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/darazfm.png" alt="DARAZ FM">
                            </div>
                            <h1>DARAZ FM</h1>
                            <p>米子市</p>
                            <!--<p class="timedata">24時間
                            ※FM802配信番組、ガイナーレ鳥取 サッカー中継を除く</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.darazfm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.darazfm.com/streaming.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm815/" class="stationlist" title="月 11:00-12:00/16:00-18:00/21:00-21:30/22:00-23:00
                    火 11:00-12:00/14:00-14:30/16:00-19:00
                    水 11:00-12:00/16:00-18:00/19:00-20:00/22:00-22:30
                    木 11:00-12:00/14:00-14:15/16:00-18:30/22:00-22:30
                    金(第1・3・5週) 8:45-09:00/11:00-12:00/16:00-18:00/22:30-23:30
                    金(第2・4週) 8:35-9:00/11:00-12:00/16:00-18:00/22:30-23:30
                    土 15:00-18:00/18:30-18:45
                    日 9:00-10:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm815.png" alt="FM高松">
                            </div>
                            <h1>FM高松</h1>
                            <p>高松市</p>
                            <!--<p class="timedata">月 11:00-12:00/16:00-18:00/21:00-21:30/22:00-23:00
                            火 11:00-12:00/14:00-14:30/16:00-19:00
                            水 11:00-12:00/16:00-18:00/19:00-20:00/22:00-22:30
                            木 11:00-12:00/14:00-14:15/16:00-18:30/22:00-22:30
                            金(第1・3・5週) 8:45-09:00/11:00-12:00/16:00-18:00/22:30-23:30
                            金(第2・4週) 8:35-9:00/11:00-12:00/16:00-18:00/22:30-23:30
                            土 15:00-18:00/18:30-18:45
                            日 9:00-10:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm815.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/fm815.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/bfm/" class="stationlist" title="月 7:30-9:00/11:00-12:00/14:00-16:00/18:00-21:00/22:00-24:00
                    火 7:30-9-00/11:00-12:00/14:00-16:00/18:00-19:00/21:00-24:00
                    水 7:30-9-00/11:00-12:00/14:00-16:00/18:00-19:00/21:00-24:00
                    木 7:30-9:00/11:00-12:00/14:00-16:00/18:00-19:00/20:00-20:30/21:00-24:00
                    金 7:30-9:00/10:30-24:00
                    土 10:00-12:00/19:00-27:00
                    日 12:00-15:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/bfm.png" alt="FMびざん">
                            </div>
                            <h1>FMびざん</h1>
                            <p>徳島市</p>
                            <!--<p class="timedata">月 7:30-9:00/11:00-12:00/14:00-16:00/18:00-21:00/22:00-24:00
                            火 7:30-9-00/11:00-12:00/14:00-16:00/18:00-19:00/21:00-24:00
                            水 7:30-9-00/11:00-12:00/14:00-16:00/18:00-19:00/21:00-24:00
                            木 7:30-9:00/11:00-12:00/14:00-16:00/18:00-19:00/20:00-20:30/21:00-24:00
                            金 7:30-9:00/10:30-24:00
                            土 10:00-12:00/19:00-27:00
                            日 12:00-15:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.bfm.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/b-fm791.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>
    <div id="kyushuokinawa" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <ul id="areanav">
                <li>
                    <a href="#home" data-transition="slide">北海道</a>
                </li>
                <li>
                    <a href="#tohoku" data-transition="slide">東北</a>
                </li>
                <li>
                    <a href="#kanto" data-transition="slide">関東</a>
                </li>
                <li>
                    <a href="#tokai" data-transition="slide">東海</a>
                </li>
                <li>
                    <a href="#hokushinetsu" data-transition="slide">北信越</a>
                </li>
                <li>
                    <a href="#kinki" data-transition="slide">近畿</a>
                </li>
                <li>
                    <a href="#chugokushikoku" data-transition="slide">中国・四国</a>
                </li>
                <li>
                    <a href="#kyushuokinawa" data-transition="slide">九州・沖縄</a>
                </li>
            </ul>
            <div class="stationlists">
                <section>
                    <a href="/blog/author/ginowancity/" class="stationlist" title="24時間

                    「放送を聞く」をクリックし、リスラジのぎのわんシティFMの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/ginowancity.png" alt="ぎのわんシティFM">
                            </div>
                            <h1>ぎのわんシティFM</h1>
                            <p>宜野湾市</p>
                            <!--<p class="timedata">24時間

                            「放送を聞く」をクリックし、リスラジのぎのわんシティFMの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://gcfm818.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/?chp=30098&amp;cap=10005&amp;arp=8" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/hibiki882/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/hibiki882.png" alt="AIR STATION HIBIKI">
                            </div>
                            <h1>AIR STATION HIBIKI</h1>
                            <p>北九州市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.hibiki882.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.simulradio.info/asx/hibiki.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmkumejima/" class="stationlist" title="5:00-25:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmkumejima.png" alt="FMくめじま">
                            </div>
                            <h1>FMくめじま</h1>
                            <p>久米島</p>
                            <!--<p class="timedata">5:00-25:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmkumejima.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fmkumejima.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmnobeoka/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmnobeoka.png" alt="FMのべおか">
                            </div>
                            <h1>FMのべおか</h1>
                            <p>延岡市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmnobeoka.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/nobeoka.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/ginowan/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/ginowan.png" alt="FMぎのわん">
                            </div>
                            <h1>FMぎのわん</h1>
                            <p>宜野湾市</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmginowan.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30093/FM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/ginga/" class="stationlist" title="テスト配信中">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/ginga.png" alt="FMぎんが">
                            </div>
                            <h1>FMぎんが</h1>
                            <p>鹿児島市</p>
                            <!--<p class="timedata">テスト配信中</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fm786.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/ginga.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmyonabaru/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmyonabaru.png" alt="FMよなばる">
                            </div>
                            <h1>FMよなばる</h1>
                            <p>与那原町</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-yonabaru.site/" target="_blank" class="site">ホームページ</a>
                        <a href="mms://hdv.nkansai.tv/yonabaru" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/heartfmnanjo/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのハートFMなんじょうの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/heartfmnanjo.png" alt="ハートFMなんじょう">
                            </div>
                            <h1>ハートFMなんじょう</h1>
                            <p>南城市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのハートFMなんじょうの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://www.hfmn.okinawa/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30091/FM" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmnaha/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのfm那覇の番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmnaha.png" alt="fm那覇">
                            </div>
                            <h1>fm那覇</h1>
                            <p>那覇市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのfm那覇の番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmnaha.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30068/FM" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmtatsugo/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmtatsugo.png" alt="FMたつごう">
                            </div>
                            <h1>FMたつごう</h1>
                            <p>大島郡龍郷町</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://tatsugo.fm-s.org/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30072/FMたつごう" target="_blank" class="stm">放送を聞く</a>
                        <a href="kiirokiiro" target="_blank" class="stm2">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/choku861/" class="stationlist" title="">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/choku861.png" alt="ちょっくらじお">
                            </div>
                            <h1>ちょっくらじお</h1>
                            <p>直方市古町</p>
                            <!--<p class="timedata"></p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://choku861.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30085/CHOKUラジ！" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm854/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのオキラジオの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm854.png" alt="オキラジ">
                            </div>
                            <h1>オキラジ</h1>
                            <p>沖縄市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのオキラジオの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="https://fm854.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30066/オキラジ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmyanbaru/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMやんばるの番組表ページへ。 左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmyanbaru.png" alt="FMやんばる">
                            </div>
                            <h1>FMやんばる</h1>
                            <p>名護市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMやんばるの番組表ページへ。 左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://fmyanbaru.co.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30095/FMやんばる" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/npo-d/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/npo-d.png" alt="あまみFM">
                            </div>
                            <h1>あまみFM</h1>
                            <p>奄美市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.npo-d.org" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.npo-d.org/simul/AmamiFM.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/shimabara/" class="stationlist" title="7:00-22:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/shimabara.png" alt="FMしまばら">
                            </div>
                            <h1>FMしまばら</h1>
                            <p>島原市</p>
                            <!--<p class="timedata">7:00-22:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.shimabara.fm/" target="_blank" class="site">ホームページ</a>
                        <a href="http://www.shimabara.fm/st/fm-shimabara-live.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/starcornfm/" class="stationlist" title="平日 7:30-14:30/17:00-20:00
                    土曜 10:00-17:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/starcornfm.png" alt="スターコーンFM">
                            </div>
                            <h1>スターコーンFM</h1>
                            <p>築上郡築上町</p>
                            <!--<p class="timedata">平日 7:30-14:30/17:00-20:00
                            土曜 10:00-17:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.starcornfm.com/" target="_blank" class="site">ホームページ</a>
                        <a href="mms://hdv.nkansai.tv/starcorn" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-nirai/" class="stationlist" title="24時間
                    ※放送休止　月 4:00-5:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-nirai.png" alt="エフエム ニライ">
                            </div>
                            <h1>エフエム ニライ</h1>
                            <p>北谷町</p>
                            <!--<p class="timedata">24時間
                            ※放送休止　月 4:00-5:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-nirai.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30003/FM" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmishigaki/" class="stationlist" title="24時間

                    「放送を聞く」をクリックし、リスラジのFMいしがきの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmishigaki.png" alt="FMいしがき">
                            </div>
                            <h1>FMいしがき</h1>
                            <p>石垣市</p>
                            <!--<p class="timedata">24時間

                            「放送を聞く」をクリックし、リスラジのFMいしがきの番組表ページへ。左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmishigaki.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30069/FMいしがきサンサンラジオ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm21/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm21.png" alt="FM21">
                            </div>
                            <h1>FM21</h1>
                            <p>浦添市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm21.net/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/fm21.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmlequio/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmlequio.png" alt="FMレキオ">
                            </div>
                            <h1>FMレキオ</h1>
                            <p>那覇市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fmlequio.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/lequio.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fm-toyomi/" class="stationlist" title="「放送を聞く」をクリックし、リスラジのFMとよみの番組表ページへ。
                    左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                    5:00-23:00">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fm-toyomi.png" alt="FMとよみ">
                            </div>
                            <h1>FMとよみ</h1>
                            <p>豊見城市</p>
                            <!--<p class="timedata">「放送を聞く」をクリックし、リスラジのFMとよみの番組表ページへ。
                            左上のListenRadioのロゴの下の再生マークをクリックすると放送が聞けます。

                            5:00-23:00</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-toyomi.com/" target="_blank" class="site">ホームページ</a>
                        <a href="http://listenradio.jp/Home/ProgramSchedule/30083/FMとよみ" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/comiten/" class="stationlist" title="8:00-23:00（毎日）">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/comiten.png" alt="コミュニティラジオ天神">
                            </div>
                            <h1>コミュニティラジオ天神</h1>
                            <p>福岡市</p>
                            <!--<p class="timedata">8:00-23:00（毎日）</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://comiten.jp/" target="_blank" class="site">ホームページ</a>
                        <a href="http://comiten.jp/live.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/fmnanjo/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/fmnanjo.png" alt="FMなんじょう">
                            </div>
                            <h1>FMなんじょう</h1>
                            <p>南城市</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.fm-nanjo.net/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/nanjo.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
                <section>
                    <a href="/blog/author/motob/" class="stationlist" title="24時間">
                        <div>
                            <div class="stationlogo">
                                <img src="/logo/motob.png" alt="FMもとぶ">
                            </div>
                            <h1>FMもとぶ</h1>
                            <p>本部町</p>
                            <!--<p class="timedata">24時間</p>-->
                        </div>
                    </a>
                    <div class="stationlink">
                        <a href="http://www.motob.net/" target="_blank" class="site">ホームページ</a>
                        <a href="http://csra.fm/asx/motob.asx" target="_blank" class="stm">放送を聞く</a>
                    </div>
                </section>
            </div>
        </article>
        <aside id="footnav">
            <ul>
                <li class="line">
                    <a href="/rule/" class="external">利用規約</a>
                </li>
                <li class="line">
                    <a href="/policy/" class="external">サイトポリシー</a>
                </li>
                <li class="line">
                    <a href="/faq/" class="external">よくある質問</a>
                </li>
                <li>
                    <a href="/contact/" class="external">お問い合せ</a>
                </li>
            </ul>
        </aside>
        <footer data-role="footer">
            <p id="credit">CSRA Community Simul Radio Alliance</p>
            <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
        </footer>
    </div>

    <div id="rule" data-role="page">
        <header data-role="header">
            <h1 id="sitetitle">
                <a href="https://csra.fm/" title="CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！" rel="home">CSRA &#8211; 日本全国のコミュニティFM放送をWebで楽しむ！</a>
            </h1>
            <div class="specialprogram311">
                <a href="http://www.simulradio.info/specialprogram311.html" target="_blank">東日本大震災 各局特別番組並びに関連イベントのお知らせ</a>
            </div>
            <div class="h_facebook">
                <a href="https://www.facebook.com/pages/CSRA/433903369980091" target="_blank">Facebook</a>
            </div>
            <nav>
                <ul>
                    <li id="nav1">
                        <a href="/" data-transition="slide" rel="external">HOME</a>
                    </li>
                    <li id="nav2">
                        <a href="/news/" rel="external">NEWS &amp; TOPICS</a>
                    </li>
                    <li id="nav3">
                        <a href="/stationlist/" rel="external">STATION LIST</a>
                    </li>
                    <li id="nav4">
                        <a href="/howtouse/" rel="external">HOW TO USE</a>
                    </li>
                </ul>
            </nav>
        </header>
        <article data-role="content">
            <div class="content">
                <div class="stationcontent">
                    <h1>STATION LIST</h1>
                </div>
                <div class="stationbody">
                    <div id="main">
                        <section>
                            <div class="entrybody">
                                <div class="entrycontent"></div>
                            </div>
                        </section>
                    </div>
                </div>
                <div>
                    <aside id="footnav">
                        <ul>
                            <li class="line">
                                <a href="/rule/" class="external">利用規約</a>
                            </li>
                            <li class="line">
                                <a href="/policy/" class="external">サイトポリシー</a>
                            </li>
                            <li class="line">
                                <a href="/faq/" class="external">よくある質問</a>
                            </li>
                            <li>
                                <a href="/contact/" class="external">お問い合せ</a>
                            </li>
                        </ul>
                    </aside>
                    <footer data-role="footer">
                        <p id="credit">CSRA Community Simul Radio Alliance</p>
                        <p id="copyright">Copyright&copy; Community Simul Radio Alliance All Rights Reserved.</p>
                    </footer>
                </div>

                <script type="text/javascript" src="https://csra.fm/wp-includes/js/dist/hooks.min.js?ver=4d63a3d491d11ffd8ac6" id="wp-hooks-js"></script>
                <script type="text/javascript" src="https://csra.fm/wp-includes/js/dist/i18n.min.js?ver=5e580eb46a90c2b997e6" id="wp-i18n-js"></script>
                <script type="text/javascript" id="wp-i18n-js-after">
                /* <![CDATA[ */
                wp.i18n.setLocaleData({
                    'text direction\u0004ltr': ['ltr']
                });
                /* ]]> */
                </script>
                <script type="text/javascript" src="https://csra.fm/wp-content/plugins/contact-form-7/includes/swv/js/index.js?ver=6.0.3" id="swv-js"></script>
                <script type="text/javascript" id="contact-form-7-js-translations">
                /* <![CDATA[ */
                (function(domain, translations) {
                    var localeData = translations.locale_data[domain] || translations.locale_data.messages;
                    localeData[""].domain = domain;
                    wp.i18n.setLocaleData(localeData, domain);
                })("contact-form-7", {
                    "translation-revision-date": "2025-01-14 04:07:30+0000",
                    "generator": "GlotPress\/4.0.1",
                    "domain": "messages",
                    "locale_data": {
                        "messages": {
                            "": {
                                "domain": "messages",
                                "plural-forms": "nplurals=1; plural=0;",
                                "lang": "ja_JP"
                            },
                            "This contact form is placed in the wrong place.": ["\u3053\u306e\u30b3\u30f3\u30bf\u30af\u30c8\u30d5\u30a9\u30fc\u30e0\u306f\u9593\u9055\u3063\u305f\u4f4d\u7f6e\u306b\u7f6e\u304b\u308c\u3066\u3044\u307e\u3059\u3002"],
                            "Error:": ["\u30a8\u30e9\u30fc:"]
                        }
                    },
                    "comment": {
                        "reference": "includes\/js\/index.js"
                    }
                });
                /* ]]> */
                </script>
                <script type="text/javascript" id="contact-form-7-js-before">
                /* <![CDATA[ */
                var wpcf7 = {
                    "api": {
                        "root": "https:\/\/csra.fm\/wp-json\/",
                        "namespace": "contact-form-7\/v1"
                    }
                };
                /* ]]> */
                </script>
                <script type="text/javascript" src="https://csra.fm/wp-content/plugins/contact-form-7/includes/js/index.js?ver=6.0.3" id="contact-form-7-js"></script>
</body>
</?php>
'''