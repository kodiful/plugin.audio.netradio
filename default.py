# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse
import shutil
import subprocess

import xbmc

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

from resources.lib.common import Common
from resources.lib.directory import Directory
from resources.lib.keyword import Keyword
from resources.lib.station import Station
from resources.lib.download import Download


if __name__ == '__main__':

    # 引数
    args = urllib.parse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]

    # action
    action = args.get('action', 'show_station')

    # ログ
    #Common.log('path=',xbmc.getInfoLabel('Container.FolderPath'))
    #Common.log('argv=',sys.argv)
    #Common.log(args)

    # actionに応じた処理
    if action == 'show_station':
        path = args.get('path')
        Directory().show(path)
    elif action == 'add_to_top':
        path = args.get('path')
        Directory().add_to_top(path)
    elif action == 'delete_from_top':
        path = args.get('path')
        Directory().delete_from_top(path)

    # 放送局
    elif action == 'set_station':
        Station().set(args.get('path'))
    elif action == 'add_station':
        Station().add()
    elif action == 'update_info':
        Common.write_mmap('True')

    # キーワード
    elif action == 'set_keyword':
        Keyword().set(args.get('path'))
    elif action == 'add_keyword':
        Keyword().add()

    # ダウンロード
    elif action == 'show_download':
        path = args.get('path')
        Download().show(path)
    elif action == "open_folder":
        keyword = args.get('keyword', '')
        path = os.path.join(Common.GET('folder'), keyword)
        if Common.OS == 'Windows':
            subprocess.Popen(['explorer', path], shell=True)
        elif Common.OS == 'Darwin':
            subprocess.call(['open', path])
    elif action == 'update_rss':
        Download().update_rss()

    # アドオン設定
    elif action == 'settings':
        src = os.path.join(Common.RESOURCES_PATH, 'default.xml')
        dst = os.path.join(Common.RESOURCES_PATH, 'settings.xml')
        shutil.copy(src, dst)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
    elif action == 'validate':
        pass  # 設定のバリデーションはここで行う

    # 未定義
    else:
        Common.log('undefined action:', action)
