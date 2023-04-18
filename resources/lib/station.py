# -*- coding: utf-8 -*-

import os
import shutil

from resources.lib.common import Common
from resources.lib.stations.common import Common as Stations

import xbmc


class Station(Common):
    
    def __init__(self):
        return
    
    def set(self, path=None):
        # 設定画面を開く
        src = os.path.join(Common.RESOURCES_PATH, 'station.xml')
        dst = os.path.join(Common.RESOURCES_PATH, 'settings.xml')
        shutil.copy(src, dst)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        # 設定画面が最前面になるまで時間をおく
        xbmc.sleep(100)
        # 設定画面を書き換える
        if path is None:
            data = {'station': '', 'description': '',  'stream': '', 'logo': '', 'official': ''}
        else:
            data = Common.read_as_json(path)
        for key in ('station', 'description', 'logo', 'stream', 'official'):
            Common.SET(key, data[key])

    def add(self):
        data = {'type': 'user'}
        for key in ('station', 'description', 'stream', 'logo', 'official'):
            data[key] = Common.GET(key)
        item = {'type': '', 'id': '', 'station': '', 'code': '', 'region': '', 'pref': '', 'city': '', 'logo': '', 'description': '', 'official': '', 'stream': ''}
        item.update(data)
        self.write_as_json(os.path.join(self.DIRECTORY_PATH, '%s.json' % item['station']), item)
        Stations.load_logo(item, self.LOGO_PATH, force=True)
        xbmc.executebuiltin('Container.Refresh')
