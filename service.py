# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
import subprocess
import logging

import xbmc

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'extra'))

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.service import Service
from resources.lib.transfer import Transfer


def check_ffmpeg():
    # fmpegのパスを取得
    ffmpeg = os.path.dirname(Common.GET('ffmpeg'))
    if ffmpeg:
        PATH = os.environ['PATH']
        if os.name == 'nt':
            os.environ['PATH'] = '%s;%s' % (ffmpeg, PATH)
        else:
            os.environ['PATH'] = '%s:%s' % (ffmpeg, PATH)
    # ffmpegのパスを確認
    p = subprocess.Popen(['ffmpeg'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    status = p.stdout.readline().decode('utf-8', errors='shift_jis').strip()
    # macOS
    # OK => "'ffmpeg version 5.1.2 Copyright (c) 2000-2022 the FFmpeg developers'""
    # NG => "'/bin/sh: ffmpeg: command not found'""
    # Windows
    # OK => "ffmpeg version 6.0-essentials_build-www.gyan.dev Copyright (c) 2000-2023 the FFmpeg developers" + "built with gcc 12.2.0 (Rev10, Built by MSYS2 project)"
    # NG => "'ffmpeg' は、内部コマンドまたは外部コマンド、" + "操作可能なプログラムまたはバッチ ファイルとして認識されていません。"
    return status.find('Copyright') > -1


if __name__ == '__main__':

    # HTTP接続のタイムアウト(秒)を設定
    socket.setdefaulttimeout(60)

    # ログレベルをWARNING以上に設定
    logging.basicConfig(level=logging.WARNING)

    # ffmpegのパスを確認して初期化
    if check_ffmpeg():
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
        # アドオンを起動
        if Common.GET('autoexec') == 'true':
            xbmc.executebuiltin(f'RunAddon({Common.ADDON_ID})')
    else:
        # ffmpegのパスが確認できない場合は通知
        Common.notify('FFmpeg not found', error=True)
