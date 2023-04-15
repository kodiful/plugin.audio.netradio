# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading

# extディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

from resources.lib.common import Common
from resources.lib.service import Service


if __name__ == '__main__':

    # HTTP接続のタイムアウト(秒)を設定
    socket.setdefaulttimeout(60)

    # ffmpegのパスを設定
    os.environ['PATH'] = Common.GET('ffmpeg').replace('/ffmpeg', '')

    # サービスを初期化
    service = Service()

    # 別スレッドでサービスを起動
    thread = threading.Thread(target=service.monitor)
    thread.start()
