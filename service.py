# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
import subprocess

import xbmcgui

# extraディレクトリをパッケージのパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'extra'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.service import Service
from resources.lib.transfer import Transfer


def set_ffmpeg(message):
    xbmcgui.Dialog().ok(Common.ADDON_NAME, message)
    ffmpeg = xbmcgui.Dialog().browse(1, Common.ADDON_NAME, 'files')
    if ffmpeg:
        Common.SET('ffmpeg', ffmpeg)
        xbmcgui.Dialog().ok(Common.ADDON_NAME, Common.STR(30020))
    else:
        xbmcgui.Dialog().ok(Common.ADDON_NAME, Common.STR(30021))
    sys.exit()

if __name__ == '__main__':

    # HTTP接続のタイムアウト(秒)を設定
    socket.setdefaulttimeout(60)

    # ffmpegの起動を確認
    ffmpeg = Common.GET('ffmpeg')
    if ffmpeg and os.path.exists(ffmpeg):
        PATH = os.environ['PATH']
        if os.name == 'nt':
            os.environ['PATH'] = '%s;%s' % (ffmpeg, PATH)
        else:
            os.environ['PATH'] = '%s:%s' % (os.path.dirname(ffmpeg), PATH)
        # ffmpegの起動を確認
        p = subprocess.Popen(['ffmpeg'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        status = p.stdout.readline().decode('utf-8', errors='shift_jis').strip()
        # macOS
        # OK => "'ffmpeg version 5.1.2 Copyright (c) 2000-2022 the FFmpeg developers'""
        # NG => "'/bin/sh: ffmpeg: command not found'""
        # Windows
        # OK => "ffmpeg version 6.0-essentials_build-www.gyan.dev Copyright (c) 2000-2023 the FFmpeg developers" + "built with gcc 12.2.0 (Rev10, Built by MSYS2 project)"
        # NG => "'ffmpeg' は、内部コマンドまたは外部コマンド、" + "操作可能なプログラムまたはバッチ ファイルとして認識されていません。"
        if status.find('ffmpeg version') == -1:
            xbmcgui.Dialog().ok(Common.ADDON_NAME, status)
            set_ffmpeg(Common.STR(30022))
    else:
        set_ffmpeg(Common.STR(30022))
    
    # DBファイルの有無をチェック
    exists =  os.path.exists(Common.DB_FILE)
    # DBインスタンスを作成
    ThreadLocal.db = DB()
    # DBファイルがない場合は既存データをインポート
    if exists is False:
        Common.notify('Transferring data...')
        Transfer().run()

    # サービスを初期化
    service = Service()
    # 別スレッドでサービスを起動
    thread = threading.Thread(target=service.monitor, daemon=True)
    thread.start()
    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
