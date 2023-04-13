# -*- coding: utf-8 -*-

import os
import shutil

from resources.lib.common import Common

import xbmc


class Keyword(Common):
    
    def __init__(self):
        return

    def set(self, path):
        # 設定画面を開く
        shutil.copy(os.path.join(Common.RESOURCES_PATH, 'keyword.xml'), os.path.join(Common.RESOURCES_PATH, 'settings.xml'))
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        # 設定画面が最前面になるまで時間をおく
        xbmc.sleep(100)
        # 設定画面を書き換える
        data = Common.read_as_json(path)[0]
        self.log(data)
        if data.get('name'):
            Common.SET('keyword', data['title'])
            Common.SET('search', '0')
            Common.SET('day', '0')
            Common.SET('limit', 'true')
            Common.SET('station', data['name'])
        if data.get('keyword'):
            Common.SET('keyword', data['keyword'])
            Common.SET('search', data['search'])
            Common.SET('day', data['day'])
            Common.SET('limit', data['limit'])
            Common.SET('station', data['station'])

    def add(self):
        data = {}
        for key in ('keyword', 'search', 'day', 'limit', 'station'):
            data[key] = Common.GET(key)
        self.write_as_json(os.path.join(self.KEYWORDS_PATH, '%s.json' % data['keyword']), data)
        #Stations.load_logo(item, self.LOGO_PATH)
        xbmc.executebuiltin('Container.Refresh')
