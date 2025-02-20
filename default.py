# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse
import shutil
import subprocess
import platform
import logging

import xbmc

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'extra'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.directory import Directory
from resources.lib.contents import Contents
from resources.lib.settings.settings import Settings
from resources.lib.settings.stations import Stations


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
    action = args.get('action', 'show_stations')

    # 表示
    if action == 'show_stations':
        protocol = args.get('protocol')
        region = args.get('region')
        pref = args.get('pref')
        Directory().show(protocol, region, pref)
    elif action == 'show_info':
        Directory().show_info(args.get('sid'))

    # 放送局
    elif action == 'get_station':
        Stations().open(args.get('sid'))
    elif action == 'set_station':
        Stations().save()
    elif action == 'delete_station':
        sid = args.get('sid') or Common.GET('sid')
        Stations().delete(sid)
    elif action == 'open_site':
        url = args.get('url') or Common.GET('site')
        os_ = platform.system()
        if os_ == 'Windows':
            subprocess.Popen(['start', url], shell=True)
        elif os_ == 'Darwin':
            subprocess.call(['open', url])
        else:
            Common.notify('Unsupported on %s' % os_)
            
    # キーワード
    elif action == 'get_keyword':
        kid = args.get('kid') or Common.GET('kid')
        Settings(flags=4).open(kid=int(kid))
    elif action == 'set_keyword':
        Settings().save(action)
    elif action == 'delete_keyword':
        Settings().save(action)
    
    # タイマー
    elif action == 'get_timer':
        Settings(flags=2).open()
    elif action == 'set_timer':
        Settings().save(action)

    # ダウンロード
    elif action == 'show_downloads':
        Contents().show(args.get('kid'))
    elif action == 'delete_download':
        Contents().delete(args.get('cid'))
    elif action == 'cancel_download':
        Contents().cancel(args.get('cid'))
    elif action == 'alert_download':
        Contents().alert(args.get('cid'))
    elif action == 'get_download':
        sid = args.get('sid') or Common.GET('sid')
        Settings(flags=7).open(sid=int(sid))
    elif action == 'set_download':
        Settings().save(action)
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
        shutil.copy(os.path.join(Common.DATA_PATH, 'settings', 'default.xml'), Common.DIALOG_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    # 未定義
    else:
        Common.log('undefined action:', action)

    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
