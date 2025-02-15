# -*- coding: utf-8 -*-

import os
import threading
import time
import ffmpeg  # https://github.com/kkroening/ffmpeg-python
from mutagen.mp3 import MP3

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.localproxy import LocalProxy


class Download(Common):

    # ダウンロード予約のタイミング（秒）
    DOWNLOAD_PREPARATION = 180
    # ダウンロード開始の余裕（秒）
    DOWNLOAD_MARGIN = 5

    def maintain_download(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 保留中(cstatus=1)の番組、かつDOWNLOAD_PREPARATION以内に開始する番組を検索
        sql = '''SELECT c.cid, c.kid, c.filename, s.protocol, s.key, c.title, EPOCH(c.start) as t, EPOCH(c.end), s.direct, s.delay
        FROM contents c JOIN stations s ON c.sid = s.sid
        WHERE c.cstatus = 1 AND t - EPOCH(NOW()) < :threshold
        ORDER BY c.start'''
        db.cursor.execute(sql, {'threshold': self.DOWNLOAD_PREPARATION})
        # ダウンロードを予約
        for cid, kid, filename, protocol, key, title, start, end, direct, delay in db.cursor.fetchall():
            start = start + delay - self.DOWNLOAD_MARGIN  # 開始時刻
            end = end + delay + self.DOWNLOAD_MARGIN  # 終了時刻
            # ダウンロードを予約
            args = [cid, kid, filename, protocol, key, title, end, direct, self.queue]
            thread = threading.Timer(start - int(time.time()), downloader, args=args)
            thread.start()
            # 待機中(cstatus=2)に更新
            sql = 'UPDATE contents SET cstatus = 2 WHERE cid = :cid'
            db.cursor.execute(sql, {'cid': cid})


def downloader(cid, kid, filename, protocol, key, title, end, direct, queue):
    # スレッドのDBインスタンスを作成
    db = ThreadLocal.db = DB()
    # radiko認証
    sql = 'SELECT auth_token FROM auth'
    db.cursor.execute(sql)
    token, = db.cursor.fetchone()
    # ストリームURL
    url = LocalProxy.proxy(protocol, key=key, direct=direct, token=token, download=True)
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
    # 出力ディレクトリ
    sql = 'SELECT dirname FROM keywords WHERE kid = :kid'
    db.cursor.execute(sql, {'kid': kid})
    dirname, = db.cursor.fetchone()
    # 出力ファイル
    download_path = os.path.join(Common.CONTENTS_PATH, dirname)
    os.makedirs(download_path, exist_ok=True)
    mp3file = os.path.join(download_path, filename)
    # ffmpeg実行
    kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
    process = ffmpeg.input(url, f='hls', t=duration).output(mp3file, **kwargs).run_async(pipe_stderr=True)
    # プロセスをキューに追加
    queue.put(process)
    # ダウンロード中(cstatus=3)に更新
    sql = 'UPDATE contents SET cstatus = 3 WHERE cid = :cid'
    db.cursor.execute(sql, {'cid': cid})
    # 開始通知
    Common.notify(f'Download started "{title}"')
    # ログ
    Common.log(f'[{process.pid}] Download started.')
    # ダウンロード終了を待つ
    process.wait()
    # ダウンロード結果に応じて後処理
    if process.returncode == 0:
        # durationを抽出
        duration = int(MP3(mp3file).info.length)
        # DB更新
        sql = 'UPDATE contents SET cstatus = -1, duration = :duration WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid, 'duration': duration})
        # ID3タグを書き込む
        db.write_id3(mp3file, cid)
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
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
