# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup

from resources.lib.scrapers.stations.common import Common


logos = {
    'エフエムしろいし': 'https://www.830.fm/wordpress/wp-content/uploads/2023/03/fm830_logo.jpg',
    'Rakuten.FM TOHOKU': 'https://www.rakuteneagles.jp/media/sites/3/asset/cmn/images/news/202111/img_211104_01_16.jpg',
    '湘南ビーチFM': 'https://www.beachfm.co.jp/wp-content/themes/welcart_basic-voll-beachfm/img/common/logo_sidemenu.png',
    'FMかほく': 'https://fm.kahoku.net/wp-content/uploads/2024/11/FMkahoku.jpg',
    'たんなんFM': 'https://tannan.fm/images/logo.png',
    'ラヂオきしわだ': 'https://fm797.com/page/wp-content/uploads/2023/03/logo.gif',
    'エフエムつやま': 'https://www.fm-tsuyama.jp/wp-content/uploads/2020/02/shinrogo2.jpg'
}


class Scraper(Common):

    PROTOCOL = 'SD'

    def __init__(self):
        super().__init__(self.PROTOCOL)

    def run(self):
        sql = '''SELECT station, code, region, pref, city, site, SD
        FROM master
        WHERE LR = '' AND SJ = '' AND SP = '' AND SR = '' AND SD != ''
        '''
        self.db.cursor.execute(sql)
        buf = []
        for station, code, region, pref, city, site, direct in self.db.cursor.fetchall():
            buf.append({
                'top': 0,
                'vis': 1,
                'protocol': 'SD',
                'key': '',
                'station': station,
                'code': code,
                'region': region,
                'pref': pref,
                'city': city,
                'logo': logos.get(station, ''),
                'description': '',
                'site': site,
                'direct': direct,
                'delay': 0
            })
        return buf

