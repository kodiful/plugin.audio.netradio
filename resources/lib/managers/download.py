# -*- coding: utf-8 -*-

import os
import threading
import time
import urllib.request
import ffmpeg  # https://github.com/kkroening/ffmpeg-python
from mutagen.mp3 import MP3

import xbmc

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.localproxy import LocalProxy
from resources.lib.contents import Contents


class DownloadManager(Common):

    # ダウンロード予約のタイミング（秒）
    DOWNLOAD_PREPARATION = 180
    # ダウンロード開始の余裕（秒）
    DOWNLOAD_MARGIN = 5

    def maintain_download(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 保留中(cstatus=1)の番組、かつDOWNLOAD_PREPARATION以内に開始する番組を検索
        sql = '''SELECT c.cid, EPOCH(c.start) as t, EPOCH(c.end), s.delay
        FROM contents c JOIN stations s ON c.sid = s.sid
        WHERE c.cstatus = 1 AND t - EPOCH(NOW()) < :threshold
        ORDER BY c.start'''
        db.cursor.execute(sql, {'threshold': self.DOWNLOAD_PREPARATION})
        # ダウンロードを予約
        for cid, start, end, delay in db.cursor.fetchall():
            start = start + delay - self.DOWNLOAD_MARGIN  # 開始時刻
            end = end + delay + self.DOWNLOAD_MARGIN  # 終了時刻
            # ダウンロードを予約
            args = [cid, end, self.queue]
            thread = threading.Timer(start - int(time.time()), downloader, args=args)
            thread.start()
            # 待機中(cstatus=2)に更新
            sql = 'UPDATE contents SET cstatus = 2 WHERE cid = :cid'
            db.cursor.execute(sql, {'cid': cid})


def downloader(cid, end, queue):
    # スレッドのDBインスタンスを作成
    db = ThreadLocal.db = DB()
    # 番組情報
    sql = '''SELECT c.title, c.filename, s.protocol, s.station, s.key, s.direct, k.dirname
    FROM contents AS c
    JOIN stations AS s ON c.sid = s.sid
    JOIN keywords AS k ON c.kid = k.kid
    WHERE c.cid = :cid'''
    db.cursor.execute(sql, {'cid': cid})
    title, filename, protocol, station, key, direct, dirname = db.cursor.fetchone()
    # radiko認証
    sql = 'SELECT auth_token FROM auth'
    db.cursor.execute(sql)
    token, = db.cursor.fetchone()
    # ストリームURL
    url = LocalProxy.proxy(protocol, key=key, direct=direct, token=token, cid=cid)
    # 時間
    duration = end - int(time.time())
    # ビットレート
    bitrate = Common.GET('bitrate')
    if bitrate == 'auto':
        if duration <= 3600:
            bitrate = '192k'
        elif duration <= 4320:
            bitrate = '160k'
        elif duration <= 5400:
            bitrate = '128k'
        elif duration <= 7200:
            bitrate = '96k'
        else:
            bitrate = '64k'
    # 出力ファイル
    mp3_file = os.path.join(Common.CONTENTS_PATH, dirname, protocol, station, filename)
    os.makedirs(os.path.dirname(mp3_file), exist_ok=True)
    # ffmpeg実行
    kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
    # RDKでは-fオプションを明示的に指定しないとエラーになる
    # localproxyからはapplication/vnd.apple.mpegurlが返る模様
    format = 'hls' if protocol == 'RDK' else ''
    process = ffmpeg.input(url, t=duration, f=format).output(mp3_file, **kwargs).run_async(pipe_stderr=True)
    # プロセスをキューに追加
    queue.put(process)
    # ダウンロード中(cstatus=3)に更新
    sql = 'UPDATE contents SET cstatus = 3 WHERE cid = :cid'
    db.cursor.execute(sql, {'cid': cid})
    # 開始通知
    Common.notify(f'Download started "{title}"')
    # ログ
    Common.log(f'Download started (pid={process.pid}).')
    # ダウンロード終了を待つ
    process.wait()
    # ダウンロード結果に応じて後処理
    if process.returncode == 0:
        # durationを抽出
        duration = int(MP3(mp3_file).info.length)
        # DB更新
        sql = 'UPDATE contents SET cstatus = -1, duration = :duration WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid, 'duration': duration})
        # ID3タグを書き込む
        db.write_id3(mp3_file, cid)
        # RSSを更新する
        Contents().update_rss()
        # websocket停止
        url = LocalProxy.proxy('success', cid=cid)
        try:
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req)
            data = res.read()
        except urllib.error.HTTPError as e:
            Common.log(f'request error (code={e.code}):', url)
        except Exception as e:
            Common.log(e)
        # 表示中画面がこのアドオン画面だったら再描画する
        path = xbmc.getInfoLabel('Container.FolderPath')
        argv = 'plugin://%s/' % Common.ADDON_ID
        if path == argv or path.startswith(f'{argv}?action=show_downloads'):
            Common.refresh()
        # 完了通知
        Common.notify('Download complete "%s"' % title)
        # ログ
        Common.log(f'[{process.pid}] Download complete.')
    else:
        # エラーメッセージ
        err = process.stderr.read().decode('utf-8')
        # DB更新
        sql = 'UPDATE contents SET cstatus = -2, description = :err WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid, 'err': err})
        # 完了通知
        Common.notify('Download failed "%s"' % title, error=True)
        # ログ
        Common.log(f'[{process.pid}] Download failed (returncode={process.returncode}).')
        Common.log(err)
    # スレッドのDBインスタンスを終了
    ThreadLocal.db.cursor.close()
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
