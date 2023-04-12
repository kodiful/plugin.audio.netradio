# -*- coding: utf-8 -*-

# extディレクトリをパスに追加
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'ext'))

# HTTP接続のタイムアウト(秒)を設定
import socket
socket.setdefaulttimeout(60)

import threading

from resources.lib.service import Service
from resources.lib.localproxy import LocalProxy


if __name__ == '__main__':
    # ローカルプロキシを初期化
    httpd = LocalProxy()
    # 別スレッドでローカルプロキシを起動
    threading.Thread(target=httpd.serve_forever).start()
    # サービスを初期化
    service = Service()
    # 別スレッドでサービスを起動
    threading.Thread(target=service.monitor).start()
