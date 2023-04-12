# -*- coding: utf-8 -*-

from resources.lib.common import Common

import socket
import urllib.request
import urllib.parse
import json
import websocket
import threading
import ffmpeg
import os
import time

from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler


class LocalProxy(HTTPServer):

    def __init__(self):
        # ポート番号
        self.port = Common.GET('port')
        # ポート番号が取得できたらHTTPサーバを準備する
        if self.port:
            # ポートが利用可能か確認する
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex(('127.0.0.1', int(self.port)))
            s.close()
            if result > 0:
                # HTTPサーバを初期化
                super().__init__(('', int(self.port)), LocalProxyHandler)
            else:
                # 通知メッセージ
                self.message = 'Localproxy port %s is busy' % self.port
        else:
            # 通知メッセージ
            self.message = 'Restart Kodi to enable localproxy'
    
    @staticmethod
    def proxy_radk(id, token):
        port = Common.GET('port')
        url = 'http://127.0.0.1:%s/radk?%s' % (port, urllib.parse.urlencode({'id': id, 'token': token}))
        return url

    @staticmethod
    def proxy_jcba(id):
        port = Common.GET('port')
        url = 'http://127.0.0.1:%s/jcba?%s' % (port, urllib.parse.urlencode({'id': id}))
        return url


class LocalProxyHandler(SimpleHTTPRequestHandler):

    HLS_CACHE = Common.HLS_CACHE_PATH
    HLS_FILE = 'hls.m3u8'
    HLS_TIME = 10

    def do_HEAD(self):
        self.do_request()

    def do_GET(self):
        self.do_request()

    def log_message(self, format, *args):
        # デフォルトのログ出力を抑制する
        # format: '"%s" %s %s'
        # args: ('GET /abort;pBVVfZdW HTTP/1.1', '200', '-')
        return

    def do_request(self):
        try:
            # HTTPリクエストをパースする
            request = urllib.parse.urlparse(self.path)
            # パスに応じて処理
            if request.path == '/radk':
                params = urllib.parse.parse_qs(request.query)
                url = f"https://f-radiko.smartstream.ne.jp/{params['id'][0]}/_definst_/simul-stream.stream/playlist.m3u"
                req = urllib.request.Request(url, headers={'x-radiko-authtoken': params['token'][0]})
                res = urllib.request.urlopen(req)
                data = res.read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            elif request.path == '/jcba':
                params = urllib.parse.parse_qs(request.query)
                url = f"https://api.radimo.smen.biz/api/v1/select_stream?station={params['id'][0]}&channel=0&quality=high&burst=5"
                req = urllib.request.Request(url)
                res = urllib.request.urlopen(req)
                data = res.read()
                data = json.loads(data)
                self.location = data['location']
                self.token = data['token']
                # 既存のwebsocketをクローズ
                if hasattr(self, 'ws'):
                    self.ws.close()
                # 別スレッドでwebsocketを起動
                threading.Thread(target=self.websocket).start()
                time.sleep(self.HLS_TIME / 3)
                # m3u8へリダイレクト
                self.send_response(301)
                self.send_header('Location', 'http://127.0.0.1:%s/hls.m3u8' % self.server.port)
                self.end_headers()
                self.wfile.write('301 Moved Permanently'.encode())
            elif request.path == '/hls.m3u8':
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-mpegurl')
                self.end_headers()
                # .m3u8ファイルの内容を返す
                with open(os.path.join(self.HLS_CACHE, self.HLS_FILE)) as f:
                    self.wfile.write(f.read().encode())
            elif request.path.endswith('.ts'):
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp2t')
                self.end_headers()
                # .tsファイルの内容を返す
                with open(os.path.join(self.HLS_CACHE, request.path.split('/')[-1]), 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('404 Not Found'.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('500 Internal Server Error'.encode())

    def websocket(self):
        self.postprocess = (
            ffmpeg
            .input('pipe:')
            .output(os.path.join(self.HLS_CACHE, self.HLS_FILE), f='hls', hls_time=self.HLS_TIME)
            .run_async(pipe_stdin=True)
        )
        for f in os.scandir(self.HLS_CACHE):
            os.remove(f.path)
        self.ws = websocket.WebSocketApp(
            self.location,
            subprotocols=['listener.fmplapla.com'],
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close
        )
        self.ws.run_forever()

    def on_open(self, ws):
        ws.send(self.token)

    def on_message(self, ws, message):
        self.postprocess.stdin.write(message)

    def on_close(self, ws):
        return
