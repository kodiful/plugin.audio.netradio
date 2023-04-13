# -*- coding: utf-8 -*-

# extディレクトリをパスに追加
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

# HTTP接続のタイムアウト(秒)を設定
import socket
socket.setdefaulttimeout(60)

import urllib.parse
import shutil

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.directory import Directory


if __name__ == '__main__':

    # 引数
    args = urllib.parse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]

    # action
    action = args.get('action', 'show')

    # ログ
    # Common.log('path=',xbmc.getInfoLabel('Container.FolderPath'))
    # Common.log('argv=',sys.argv)
    # Common.log(args)

    # actionに応じた処理
    if action == 'show':
        path = args.get('path')
        Directory().show(path)
    elif action == 'add_to_top':
        path = args.get('path')
        Directory().add_to_top(path)
    elif action == 'delete_from_top':
        path = args.get('path')
        Directory().delete_from_top(path)

    # 放送局追加
    elif action == 'new_station':
        data = {'name': '', 'description': '', 'logo': 'https://', 'stream': 'https://'}
        shutil.copy(os.path.join(Common.RESOURCES_PATH, 'station.xml'), os.path.join(Common.RESOURCES_PATH, 'settings.xml'))
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        xbmc.sleep(1000)
        for key in ('name', 'description', 'logo', 'stream'):
            Common.SET(key, data[key])
    elif action == 'change_station':
        data = Common.read_as_json(args.get('path'))
        shutil.copy(os.path.join(Common.RESOURCES_PATH, 'station.xml'), os.path.join(Common.RESOURCES_PATH, 'settings.xml'))
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        xbmc.sleep(1000)
        for key in ('name', 'description', 'logo', 'stream'):
            Common.SET(key, data[key])
    elif action == 'add_station':
        data = {'type': 'user'}
        for key in ('name', 'description', 'logo', 'stream'):
            data[key] = Common.GET(key)
        Directory().add_station(data)

    # キーワード追加
    elif action == 'add_keyword':
        pass
    # キーワード削除
    elif action == 'delete_keyword':
        pass

    # アドオン設定
    elif action == 'settings':
        src = os.path.join(Common.RESOURCES_PATH, 'default.xml')
        dst = os.path.join(Common.RESOURCES_PATH, 'settings.xml')
        shutil.copy(src, dst)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
    # 未定義
    else:
        Common.log('undefined action:', action)
