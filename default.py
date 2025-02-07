# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse
import shutil
import subprocess
import platform

import xbmc

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.directory import Directory
from resources.lib.download import Download

from resources.lib.keyword import Keyword
from resources.lib.station import Station


if __name__ == '__main__':

    # DBインスタンスを作成
    ThreadLocal.db = DB()

    # 引数
    args = urllib.parse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]

    # action
    action = args.get('action', 'show_station')

    # actionに応じた処理
    if action == 'show_station':
        type = args.get('type')
        region = args.get('region')
        pref = args.get('pref')
        Directory().show(type, region, pref)
    elif action == 'add_to_top':
        Directory().add_to_top(args.get('sid'))
    elif action == 'delete_from_top':
        Directory().delete_from_top(args.get('sid'))

    # 放送局
    elif action == 'set_station':
        Station().set(args.get('sid'))
    elif action == 'add_station':
        Station().add()
    elif action == 'delete_station':
        Station().delete(args.get('sid'))
    elif action == 'show_info':
        Station().show_info(args.get('sid'))
    elif action == 'update_info':
        Station().update_info()

    # キーワード
    elif action == 'set_keyword':
        Keyword().set(args.get('kid'), args.get('sid'))
    elif action == 'add_keyword':
        Keyword().add()
    elif action == 'delete_keyword':
        Keyword().delete(args.get('kid'))

    # ダウンロード
    elif action == 'show_download':
        Download().show(args.get('kid'))
    elif action == 'open_folder':
        path = os.path.join(Common.CONTENTS_PATH, args.get('kid', ''))
        os_ = platform.system()
        if os_ == 'Windows':
            subprocess.Popen(['explorer', path], shell=True)
        elif os_ == 'Darwin':
            subprocess.call(['open', path])
        else:
            Common.notify('Unsupported on %s' % os_)
    elif action == 'update_rss':
        Download().update_rss()

    # アドオン設定
    elif action == 'settings':
        Common.SET('pref', Directory().pref)
        shutil.copy(os.path.join(Common.DATA_PATH, 'settings', 'settings.xml'), Common.DIALOG_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    # 未定義
    else:
        Common.log('undefined action:', action)

    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
