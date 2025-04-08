# -*- coding: utf-8 -*-

import socket
import urllib.request
import urllib.parse
import json
import websocket  # https://github.com/websocket-client/websocket-client
import threading
import ffmpeg
import os
import shutil
import time
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler

import xbmc

from resources.lib.common import Common


class LocalProxy(HTTPServer, Common):

    def __init__(self):
        # ポート番号
        self.port = self.GET('port')
        # スレッドリスト
        self.threadlist = {}
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
            kwargs = {'cid': cid, 'protocol': protocol, 'key': key, 'token': token}
        elif protocol == 'SJ':
            kwargs = {'cid': cid, 'protocol': protocol, 'key': key}
        elif protocol == 'SP':
            kwargs = {'cid': cid, 'protocol': protocol, 'key': key}
        elif protocol == 'success':
            kwargs = {'cid': cid, 'protocol': protocol}
        else:
            return direct  # mmsプロトコルのurlを302でリダイレクトさせようとするとエラーになるので直接アクセスさせることにする
        port = Common.GET('port')
        query = urllib.parse.urlencode(kwargs)
        return f'http://127.0.0.1:{port}/play?{query}'


class LocalProxyHandler(SimpleHTTPRequestHandler, Common):

    def log_message(self, format, *args):
        # デフォルトのログ出力を抑制する
        # format: '"%s" %s %s'
        # args: ('GET /abort;pBVVfZdW HTTP/1.1', '200', '-')
        return

    def do_HEAD(self):
        try:
            # HTTPリクエストをパースする
            request = urllib.parse.urlparse(self.path)
            # パスに応じて処理
            if request.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
            elif request.path == '/play':
                self.send_response(302)
                self.end_headers()
            elif request.path.endswith('.m3u8'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-mpegurl')
                self.end_headers()
            elif request.path.endswith('.ts'):
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp2t')
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.log(e)


    def do_GET(self):
        try:
            # HTTPリクエストをパースする
            request = urllib.parse.urlparse(self.path)
            params = dict(map(lambda x: (x[0], x[1][0]), urllib.parse.parse_qs(request.query).items()))

            # self.path '/?cid=0&protocol=SP&key=kanazawaseasidefm'
            # params = {'cid': '0', 'protocol': 'SP', 'key': 'kanazawaseasidefm'}

            # パスに応じて処理
            if request.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                html = self.threadlist2html()
                self.wfile.write(html.encode())
            elif request.path == '/play':
                # protocolに応じて処理
                self.do_proxy(params['protocol'], params)
            elif request.path.endswith('.m3u8'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-mpegurl')
                self.end_headers()
                # .m3u8ファイルの内容を返す
                paths = request.path.split('/')
                with open(os.path.join(self.HLS_CACHE_PATH, paths[-2], paths[-1]), 'rb') as f:
                    self.wfile.write(f.read())
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
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'500 Internal Server Error')
            self.log(e)

    def do_proxy(self, protocol, params):
        # 競合する既存スレッドを停止
        cid = params['cid']
        item = self.server.threadlist.get(cid)
        if item and item['thread'].is_alive():
            self.log('new thread found and close websocket:', item['thread'].ident)
            item['ws'].ws.close()
            item['status'] = 'new player'
        # protocolに応じて処理
        if protocol == 'success':  # ↑で競合する既存スレッドを停止したのでそのまま終了
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'200 OK')
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
        elif protocol in ('SJ', 'SP'):
            key = params['key']
            cid = params['cid']
            if protocol == 'SJ':
                url = f'https://api.radimo.smen.biz/api/v1/select_stream?station={key}&channel=0&quality=high&burst=5'
                req = urllib.request.Request(url)
            if protocol == 'SP':
                url = f'https://fmplapla.com/api/select_stream?station={key}&burst=5'
                req = urllib.request.Request(url, headers={'Origin': 'https://fmplapla.com'}, method='POST')
            res = urllib.request.urlopen(req)
            data = json.loads(res.read())
            # websocketを作成
            ws = WebSocket(data['location'], data['token'], cid, self.server, self.path)
            # スレッドを作成
            thread = threading.Thread(target=ws.start, daemon=True)
            # スレッドリストに格納
            self.server.threadlist[cid] = {'key': key, 'protocol': protocol, 'thread': thread, 'ws': ws, 'cid': cid, 'status': ''}
            # スレッド起動
            thread.start()
            # HLS_FILEが生成されるまで3秒待つ
            time.sleep(3)
            # HLS_FILEへリダイレクト
            self.send_response(302)
            self.send_header('Location', f'http://127.0.0.1:{self.server.port}/{cid}/{self.HLS_FILE}')
            self.end_headers()
            self.wfile.write(b'302 Found')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def threadlist2html(self):
        # リスト化
        data = [['cid', 'key', 'protocol', 'thread.ident', 'thread.is_alive', 'ws.sock.connected', 'status']]
        for dir, item in self.server.threadlist.items():
            key = item.get('key')
            protocol = item.get('protocol')
            thread = item.get('thread')
            ws = item.get('ws')
            cid = item.get('cid')
            status = item.get('status')
            data.append([cid, key, protocol, thread.ident, thread.is_alive(), ws.ws.sock and ws.ws.sock.connected, status])
        # hrmlに変換
        html = ['<table>']
        html.append('<thead>')
        for row in data[:1]:
            html.append('<tr>')
            html.extend([f'<th>{cell}</th>' for cell in row])
            html.append('</tr>')
        html.append('</thead>')
        html.append('<tbody>')
        for row in data[1:]:
            html.append('<tr>')
            html.extend([f'<td>{cell}</td>' for cell in row])
            html.append('</tr>')
        html.append('</tbody>')
        html.append('</table>')
        # ページに埋め込む
        with open(os.path.join(self.DATA_PATH, 'html', 'template.html')) as f:
            template = f.read()
        return template.format(table='\n'.join(html))


class WebSocket(Common):

    def __init__(self, location, token, cid, server, path):
        self.location = location
        self.token = token
        self.cid = cid
        self.dir = os.path.join(self.HLS_CACHE_PATH, cid)
        self.server = server
        self.path = path

    def start(self):
        self.threaddata = self.server.threadlist.get(self.cid)
        self.thread = self.threaddata['thread']
        self.log('start websocket:', self.thread.ident)
        # キャッシュをクリア
        self._cleanup()
        # キャッシュディレクトリを作成
        os.makedirs(self.dir, exist_ok=True)
        # websocketを開始する
        websocket.setdefaulttimeout(5)
        self.ws = websocket.WebSocketApp(
            self.location,
            subprotocols=['listener.fmplapla.com'],
            on_open=self.on_open, on_message=self.on_message, on_close=self.on_close, on_error=self.on_error)
        try:
            self.ws.run_forever()
        except SystemExit:
            self.ws.close()
        # キャッシュをクリア
        self._cleanup()
        self.log('websocket ended:', self.thread.ident)

    def _cleanup(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

    def on_open(self, ws):
        self.log('websocket opened:', self.thread.ident, self.location)
        # 変換プロセスを開始
        hls_file = os.path.join(self.dir, self.HLS_FILE)
        self.ffmpeg = ffmpeg.input('pipe:').output(hls_file, f='hls', hls_time=self.HLS_TIME).run_async(pipe_stdin=True)
        ws.send(self.token)

    def on_message(self, ws, message):
        self.ffmpeg.stdin.write(message)
        # 再生中コンテンツをチェック
        if self.cid == '0':
            if xbmc.Player().isPlaying():
                item = xbmc.Player().getPlayingItem()
                # item.getPath(): "http://127.0.0.1:8088/?cid=0&protocol=SJ&key=fmblueshonan"
                # self.path: "/?cid=0&protocol=SJ&key=fmblueshonan"
                if item.getPath().find(self.path) < 0:
                    # スレッドと違うコンテンツが再生されているのでwebsocket停止
                    self.log('new player found and close websocket:', item.getPath())
                    ws.close()
                    self.threaddata['status'] = 'new player'
            else:
                # 再生されているコンテンツがないのでwebsocket停止
                self.log('no player and close websocket')
                ws.close()
                self.threaddata['status'] = 'no player'

    def on_close(self, ws, status, message):
        # 変換プロセスを停止
        self.ffmpeg.kill()  # ffmpegのPopenオブジェクトを停止
        self.log('websocket closed:', self.thread.ident)

    def on_error(self, ws, err):
        self.log('websocket error:', self.thread.ident, err)
