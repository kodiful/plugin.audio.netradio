# -*- coding: utf-8 -*-

import os
import locale
import shutil
import html

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


def decorator(this, title, dirname, filename):
    def wrapper(func):
        def inner(*args, **kwargs):
            # RSS設定がされていない場合は終了
            if this.GET('rss') == 'false': return
            # RSSを作成するディレクトリ
            this.path = os.path.join(this.CONTENTS_PATH, dirname)
            # open writer
            if os.path.exists(this.path) is False:
                os.makedirs(this.path, exist_ok=True)
            this.writer = open(os.path.join(this.path, filename), 'w', encoding='utf-8')
            # write header
            this.writer.write(this.header.format(image='icon.png', title=html.escape(title)))
            # write body
            func(*args, **kwargs)
            # write footer
            this.writer.write(this.footer)
            # close writer
            this.writer.close()
            # RSSから参照できるように、スタイルシートとアイコン画像をダウンロードフォルダにコピーする
            for item in ('stylesheet.xsl', 'icon.png'):
                shutil.copy(os.path.join(this.DATA_PATH, 'rss', item), os.path.join(this.path, item))
        return inner
    return wrapper


class Common(Common):
    
    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # 時刻表記のロケール設定                                                                                                                                                             
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # templates
        with open(os.path.join(self.DATA_PATH, 'rss', 'header.xml'), 'r', encoding='utf-8') as f:
            self.header = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'body.xml'), 'r', encoding='utf-8') as f:
            self.body = f.read()
        with open(os.path.join(self.DATA_PATH, 'rss', 'footer.xml'), 'r', encoding='utf-8') as f:
            self.footer = f.read()

    def _date(self, date):
        # "2023-04-20 14:00:00" -> "2023-04-20"
        return date[0:10]

    def _pubdate(self, date):
        # "2023-04-20 14:00:00" -> "Thu, 20 Apr 2023 14:00:00 +0900"
        pubdate = self.datetime(date).strftime('%a, %d %b %Y %H:%M:%S +0900')
        return pubdate
