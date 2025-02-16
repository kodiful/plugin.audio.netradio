# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse
import shutil
import subprocess
import platform
import logging

import xbmc
import xbmcgui

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.directory import Directory
from resources.lib.contents import Contents
from resources.lib.keywords import Keywords
from resources.lib.stations import Stations


if __name__ == '__main__':

    # ログレベルをWARNING以上に設定
    logging.basicConfig(level=logging.WARNING)

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
        protocol = args.get('protocol')
        region = args.get('region')
        pref = args.get('pref')
        Directory().show(protocol, region, pref)
    elif action == 'add_to_top':
        Directory().add_to_top(args.get('sid'))
    elif action == 'delete_from_top':
        Directory().delete_from_top(args.get('sid'))
    elif action == 'update_info':
        Directory().maintain_schedule()

    # 放送局
    elif action == 'set_station':
        Stations().set(args.get('sid'))
    elif action == 'add_station':
        Stations().add()
    elif action == 'delete_station':
        Stations().delete(args.get('sid'))
    elif action == 'show_info':
        Stations().show_info(args.get('sid'))
    elif action == 'open_site':
        url = args.get('url')
        Common.log(url)
        os_ = platform.system()
        if os_ == 'Windows':
            subprocess.Popen(['start', url], shell=True)
        elif os_ == 'Darwin':
            subprocess.call(['open', url])
        else:
            Common.notify('Unsupported on %s' % os_)
            
    # キーワード
    elif action == 'set_keyword':
        Keywords().set(args.get('kid'), args.get('sid'))
    elif action == 'add_keyword':
        Keywords().add()
    elif action == 'delete_keyword':
        Keywords().delete(args.get('kid'))

    # ダウンロード
    elif action == 'show_download':
        Contents().show(args.get('kid'))
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
        Contents().update_rss()

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
