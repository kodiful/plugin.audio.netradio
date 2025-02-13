#!/usr/bin/env python

import re

 # <dd class="cf A08" data-order="X" data-pref="J09" data-open="2022-10-01"><a href="https://kanazawa-seasidefm.co.jp/" target="_blank">金沢シーサイドFM</a>JOZZ3DA-FM | 横浜 85.5 | <a href="https://fmplapla.com/kanazawaseasidefm/" target="_blank">FM++</a>

regexp = r'<.*?><a href="(.*?)".*?>(.*?)</a>(JOZZ[A-Z0-9\-]+)(.*?)<a href="(.*?)".*>(.*?)</a>'

with open('放送Link集 - コミュニティFM放送局の公式サイト一覧.html') as f:
    for line in filter(lambda x: x.startswith('<dd class="cf '), f.readlines()):
        line = line.replace('島田76.5', '島田 76.5')
        m = re.match(regexp, line.strip())
        if m:
            #print(*[m.group(i) for i in range(1,5)], sep='\t')
            url = m.group(1)
            name = re.sub(r'<.*?>.*?<.*?>', '', m.group(2))
            callsign = m.group(3)
            place, freq = re.split(r'[ ]+', m.group(4).strip(' |'))
            stream = m.group(5)
            protocol = m.group(6)
            print(name, callsign, url, place, freq, stream, protocol, sep='\t')

