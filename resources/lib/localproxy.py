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
import shutil
import time
import ctypes
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler

import xbmc


class LocalProxy(HTTPServer, Common):

    def __init__(self):
        # ポート番号
        self.port = self.GET('port')
        # スレッドリスト
        self.threads = {}
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
                self.notify('Localproxy port %s is busy' % self.port)
        else:
            self.notify('Localproxy port is not defined')

    @staticmethod
    def proxy(protocol, key='', direct='', token='', cid='0'):
        if protocol == 'RDK':
            kwargs = {'cid': cid, 'protocol': 'RDK', 'key': key, 'token': token}
        elif protocol == 'SJ':
            kwargs = {'cid': cid, 'protocol': 'SJ', 'key': key}
        elif protocol == 'SP':
            kwargs = {'cid': cid, 'protocol': 'SP', 'key': key}
        else:
            kwargs = {'cid': cid, 'protocol': 'redirect', 'url': direct}
        port = Common.GET('port')
        query = urllib.parse.urlencode(kwargs)
        return f'http://127.0.0.1:{port}/?{query}'


class LocalProxyHandler(SimpleHTTPRequestHandler, Common):

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
            params = dict(map(lambda x: (x[0], x[1][0]), urllib.parse.parse_qs(request.query).items()))
            # self.path '/?cid=0&protocol=SP&key=kanazawaseasidefm'
            # params = {'cid': '0', 'protocol': 'SP', 'key': 'kanazawaseasidefm'}
            # パスに応じて処理
            if request.path == '/':
                self.do_request_protocol(params)
            elif request.path.endswith('.m3u8'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-mpegurl')
                self.end_headers()
                # .m3u8ファイルの内容を返す
                paths = request.path.split('/')
                with open(os.path.join(self.HLS_CACHE_PATH, paths[-2], paths[-1])) as f:
                    self.wfile.write(f.read().encode())
            elif request.path.endswith('.ts'):
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp2t')
                self.end_headers()
                # .tsファイルの内容を返す
                paths = request.path.split('/')
                with open(os.path.join(self.HLS_CACHE_PATH, paths[-2], paths[-1]), 'rb') as f:
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

    def do_request_protocol(self, params):
        # 競合する既存スレッドを停止
        cid = params['cid']
        item = self.server.threads.get(cid)
        if item:
            thread = item['thread']
            self.log('competitive thread found:', thread.ident)
            item['ws'].ws.close()  # websocket停止 -> スレッド停止 -> スレッドリストから削除
        # protocolに応じて処理
        protocol = params['protocol']
        if protocol == 'redirect':
            url = params['url']
            # urlへリダイレクト
            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        elif protocol == 'RDK':
            key = params['key']
            url = f"https://f-radiko.smartstream.ne.jp/{key}/_definst_/simul-stream.stream/playlist.m3u"
            token = params['token']
            req = urllib.request.Request(url, headers={'x-radiko-authtoken': token})
            res = urllib.request.urlopen(req)
            data = res.read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)
        elif protocol == 'SJ':
            key = params['key']
            cid = params['cid']
            url = f'https://api.radimo.smen.biz/api/v1/select_stream?station={key}&channel=0&quality=high&burst=5'
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            data = json.loads(res.read())
            # websocketを作成
            ws = WebSocket(data['location'], data['token'], cid, self)
            # 別スレッドでwebsocketを起動
            thread = threading.Thread(target=ws.start)
            thread.start()
            # スレッドリストに格納
            self.server.threads[cid] = {'thread': thread, 'ws': ws}
            self.log('thread started:', thread.ident, 'number of threads:', len(self.server.threads))
            # m3u8が生成される時間を待つ
            time.sleep(3)
            # m3u8へリダイレクト
            self.send_response(302)
            self.send_header('Location', f'http://127.0.0.1:{self.server.port}/{cid}/hls.m3u8')
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        elif protocol == 'SP':
            key = params['key']
            cid = params['cid']
            url = f'https://fmplapla.com/api/select_stream?station={key}&burst=5'
            req = urllib.request.Request(url, headers={'Origin': 'https://fmplapla.com'}, method='POST')
            res = urllib.request.urlopen(req)
            data = json.loads(res.read())
            # websocketを作成
            ws = WebSocket(data['location'], data['token'], cid, self)
            # 別スレッドでwebsocketを起動
            thread = threading.Thread(target=ws.start)
            thread.start()
            # スレッドリストに格納
            self.server.threads[cid] = {'thread': thread, 'ws': ws}
            self.log('thread started:', thread.ident, 'number of threads:', len(self.server.threads))
            # m3u8が生成される時間を待つ
            time.sleep(3)
            # m3u8へリダイレクト
            self.send_response(302)
            self.send_header('Location', f'http://127.0.0.1:{self.server.port}/{cid}/hls.m3u8')
            self.end_headers()
            self.wfile.write(b'302 Moved Temporarily')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')


class WebSocket(Common):

    def __init__(self, location, token, cid, parent):
        self.location = location
        self.token = token
        self.cid = cid
        self.dir = os.path.join(self.HLS_CACHE_PATH, cid)
        self.parent = parent

    def start(self):
        # キャッシュをクリア
        self._cleanup()
        # キャッシュディレクトリを作成
        os.makedirs(self.dir, exist_ok=True)
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
        hls_file = os.path.join(self.dir, self.HLS_FILE)
        ws.process = ffmpeg.input('pipe:').output(hls_file, f='hls', hls_time=self.HLS_TIME).run_async(pipe_stdin=True)
        ws.send(self.token)

    def on_message(self, ws, message):
        ws.process.stdin.write(message)
        # 再生中コンテンツをチェック
        if self.cid == '0':
            if xbmc.Player().isPlaying():
                item = xbmc.Player().getPlayingItem()
                # item.getPath(): "http://127.0.0.1:8088/?cid=0&protocol=SJ&key=fmblueshonan"
                # self.parent.path: "/?cid=0&protocol=SJ&key=fmblueshonan"
                if item.getPath().find(self.parent.path) > -1:
                    return  # スレッドの処理対象と同じだったら何もしない
            # スレッドと違うコンテンツが再生されているのでwebsocket停止
            self.log('closing websocket due to the playing of:', item.getPath())
            ws.close()   # websocket停止 -> スレッド停止 -> スレッドリストから削除

    def on_close(self, ws, status, message):
        # websocket停止
        ws.process.kill()
        self.log('websocket closed:', status, message)
        # キャッシュをクリア
        self._cleanup()
        # スレッド
        data = self.parent.server.threads[self.cid]
        thread = data['thread']
        # スレッドリストから削除
        del self.parent.server.threads[self.cid]
        self.log('thread being killed:', thread.ident, 'number of threads:', len(self.parent.server.threads))
        # スレッド強制停止
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), ctypes.py_object(SystemExit))

    def _cleanup(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
