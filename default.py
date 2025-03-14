# -*- coding: utf-8 -*-

import sys
import os
import urllib.parse
import shutil
import subprocess
import platform

import xbmc

# extraディレクトリをパッケージのパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'extra'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.directory import Directory
from resources.lib.contents import Contents
from resources.lib.settings import Settings, Stations


if __name__ == '__main__':

    # DBインスタンスを作成
    ThreadLocal.db = DB()

    # 引数
    args = urllib.parse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    args = dict(map(lambda x: (x[0], x[1][0]), args.items()))

    # action
    action = args.get('action', 'show_stations')

    # 表示
    if action == 'show_stations':
        protocol = args.get('protocol')
        region = args.get('region')
        pref = args.get('pref')
        Directory().show(protocol, region, pref)
    elif action == 'info_onair':
        sid = args.get('sid')
        Directory().info(int(sid))
    elif action == 'show_qrcode':
        Directory().show_qrcode(args.get('url'))
    elif action == 'add_to_top':
        sid = args.get('sid', 0)
        Directory().showhide(int(sid), 1)
    elif action == 'delete_from_top':
        sid = args.get('sid', 0)
        Directory().showhide(int(sid), 0)

    # 放送局
    elif action == 'get_station':
        sid = args.get('sid', 0)
        Stations().get(int(sid))
    elif action == 'set_station':
        Stations().set()
    elif action == 'delete_station':
        sid = args.get('sid') or Common.GET('sid')
        Stations().delete(int(sid))
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
        kid = args.get('kid', 0)
        Settings(flags=4).get(kid=int(kid))
    elif action == 'set_keyword':
        Settings().set(action)
    elif action == 'delete_keyword':
        Settings().set(action)

    # タイマー
    elif action == 'get_timer':
        Settings(flags=2).get()
    elif action == 'set_timer':
        Settings().set(action)

    # ダウンロード
    elif action == 'show_downloads':
        kid = args.get('kid', 0)
        protocol = args.get('protocol', '')
        station = args.get('station', '')
        date = args.get('date', '')
        Contents().show(kid=int(kid), protocol=protocol, station=station, date=date)
    elif action == 'info_download':
        cid = args.get('cid')
        Contents().info(int(cid))
    elif action == 'delete_download':
        cid = args.get('cid')
        Contents().delete(int(cid))
    elif action == 'play_download':
        cid = args.get('cid')
        Contents().play(int(cid))
    elif action == 'get_download':
        sid = args.get('sid', 0)
        Settings(flags=7).get(sid=int(sid))
    elif action == 'set_download':
        Settings().set(action)
    elif action == 'open_folder':
        path = Common.CONTENTS_PATH
        os_ = platform.system()
        if os_ == 'Windows':
            subprocess.Popen(['explorer', path], shell=True)
        elif os_ == 'Darwin':
            subprocess.call(['open', path])
        else:
            Common.notify('Unsupported on %s' % os_)
    elif action == 'update_rss':
        Contents().update_rss(notify=True)

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
