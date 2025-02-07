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
import queue
import ctypes

from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler


class LocalProxy(HTTPServer, Common):

    def __init__(self):
        # ポート番号
        self.port = self.GET('port')
        # ポート番号が取得できたらHTTPサーバを準備する
        if self.port:
            # ポートが利用可能か確認する
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex(('127.0.0.1', int(self.port)))
            s.close()
            if result > 0:
                # スレッドキュー
                self.queue = queue.Queue()
                # HTTPサーバを初期化
                super().__init__(('', int(self.port)), LocalProxyHandler)
            else:
                self.notify('Localproxy port %s is busy' % self.port)
        else:
            self.notify('Localproxy port is not defined')

    @staticmethod
    def proxy(type, abbr='', direct='', token='', download=False):
        if type == 'radk':
            kwargs = {'download': download, 'type': 'radk', 'abbr': abbr, 'token': token}
        elif type == 'jcba':
            kwargs = {'download': download, 'type': 'jcba', 'abbr': abbr}
        elif type == 'fmpp':
            kwargs = {'download': download, 'type': 'fmpp', 'abbr': abbr}
        else:
            kwargs = {'download': download, 'type': 'redirect', 'url': direct}
        port = Common.GET('port')
        query = urllib.parse.urlencode(kwargs)
        return f'http://127.0.0.1:{port}/?{query}'


class LocalProxyHandler(SimpleHTTPRequestHandler, Common):

    HLS_CACHE = Common.HLS_CACHE_PATH
    HLS_FILE = 'hls.m3u8'
    HLS_TIME = 5

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
            params = urllib.parse.parse_qs(request.query)
            # パスに応じて処理
            if request.path == '/':
                self.do_request_type(request, params)
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
                self.wfile.write(b'404 Not Found')
        except Exception as e:
            self.log(e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'500 Internal Server Error')

    def do_request_type(self, request, params):
        # スレッドキューのメンテナンス
        download = params['download'][0]
        if download == 'False':
            q = self.server.queue
            alive = None
            while q.qsize() > 0:
                thread, query = data = q.get()
                if query == request.query:
                    alive = data
                else:
                    ident = ctypes.c_long(thread.ident)
                    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ident, ctypes.py_object(SystemExit))
            if alive:
                q.put(alive)
        # typeに応じて処理
        type_ = params['type'][0]
        if type_ == 'redirect':
            url = params['url'][0]
            # urlへリダイレクト
            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        elif type_ == 'radk':
            abbr = params['abbr'][0]
            url = f"https://f-radiko.smartstream.ne.jp/{abbr}/_definst_/simul-stream.stream/playlist.m3u"
            token = params['token'][0]
            req = urllib.request.Request(url, headers={'x-radiko-authtoken': token})
            res = urllib.request.urlopen(req)
            data = res.read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif type_ == 'jcba':
            abbr = params['abbr'][0]
            url = f'https://api.radimo.smen.biz/api/v1/select_stream?station={abbr}&channel=0&quality=high&burst=5'
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            data = res.read()
            data = json.loads(data)
            self.location = data['location']
            self.token = data['token']
            if self.server.queue.qsize() == 0:
                # 別スレッドでwebsocketを起動
                thread = self.server.thread = threading.Thread(target=self.start_websocket)
                thread.start()
                # スレッドキューに格納
                self.server.queue.put((thread, request.query))
            # m3u8が生成される時間を待つ
            time.sleep(3)
            # m3u8へリダイレクト
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:%s/hls.m3u8' % self.server.port)
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        elif type_ == 'fmpp':
            abbr = params['abbr'][0]
            url = f'https://fmplapla.com/api/select_stream?station={abbr}&burst=5'
            req = urllib.request.Request(url, headers={'Origin': 'https://fmplapla.com'}, method='POST')
            res = urllib.request.urlopen(req)
            data = res.read()
            data = json.loads(data)
            self.location = data['location']
            self.token = data['token']
            if self.server.queue.qsize() == 0:
                # 別スレッドでwebsocketを起動
                thread = self.server.thread = threading.Thread(target=self.start_websocket)
                thread.start()
                # スレッドキューに格納
                self.server.queue.put((thread, request.query))
            # m3u8が生成される時間を待つ
            time.sleep(3)
            # m3u8へリダイレクト
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:%s/hls.m3u8' % self.server.port)
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def start_websocket(self):
        # キャッシュをクリア
        for f in os.scandir(self.HLS_CACHE):
            os.remove(f.path)
        # websocketを開始する
        self.ws = websocket.WebSocketApp(
            self.location,
            subprotocols=['listener.fmplapla.com'],
            on_open=self.on_open, on_message=self.on_message, on_close=self.on_close)
        try:
            self.ws.run_forever()
        except SystemExit:
            self.ws.close()

    def on_open(self, ws):
        self.log('websocket opened:', self.location)
        # 変換プロセスを開始する
        hls_file = os.path.join(self.HLS_CACHE, self.HLS_FILE)
        hls_time = self.HLS_TIME
        ws.process = ffmpeg.input('pipe:').output(hls_file, f='hls', hls_time=hls_time).run_async(pipe_stdin=True)
        ws.send(self.token)

    def on_message(self, ws, message):
        ws.process.stdin.write(message)
        # 再生中のコンテンツがwebsocket再生でない場合はwebsocketを終了する
        path = self.nowplaying()  # http://127.0.0.1:8088/?type=jcba&id=fmblueshonan
        if path:
            type_ = path.split('/')[3]
            if type_.find('type=jcba') != -1:
                return  # jcbaの場合は継続
            if type_.find('type=fmpp') != -1:
                return  # fmppの場合は継続
        raise SystemExit

    def on_close(self, ws, status, message):
        thread = self.server.queue.get()
        ident = ctypes.c_long(thread.ident)
        ws.process.kill()
        self.log('websocket closed:', status, message)
