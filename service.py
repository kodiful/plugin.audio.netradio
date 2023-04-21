# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
import subprocess

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

from resources.lib.common import Common
from resources.lib.service import Service


def check_ffmpeg():
    # fmpegのパスを取得
    ffmpeg = Common.GET('ffmpeg')
    if ffmpeg:
        PATH = os.environ['PATH']
        if Common.OS == 'Windows':
            os.environ['PATH'] = '%s;%s' % (PATH, ffmpeg)
        else:
            os.environ['PATH'] = '%s:%s' % (PATH, ffmpeg)
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

    # ffmpegのパスを確認して初期化
    if check_ffmpeg():

        # サービスを初期化
        service = Service()

        # 別スレッドでサービスを起動
        thread = threading.Thread(target=service.monitor)
        thread.start()