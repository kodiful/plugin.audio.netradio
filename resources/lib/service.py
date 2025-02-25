# -*- coding: utf-8 -*-

import os
import shutil
import threading
import queue
import time

import xbmc

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.localproxy import LocalProxy
from resources.lib.managers.authentication import AuthenticationManager
from resources.lib.managers.schedule import ScheduleManager
from resources.lib.managers.download import DownloadManager


class Service(AuthenticationManager, ScheduleManager, DownloadManager):

    def __init__(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # authテーブルを初期化
        db.cursor.executescript(db.sql_auth_init)
        # statusテーブルを初期化
        db.cursor.executescript(db.sql_status_init)
        # ダウンロード済み以外の番組情報を削除
        db.cursor.execute('''SELECT k.dirname, c.filename
                          FROM contents AS c JOIN keywords as k ON c.kid = k.kid
                          WHERE c.cstatus != -1 or c.end > NOW()''')
        for dirname, filename in db.cursor.fetchall():
            mp3_file = os.path.join(self.CONTENTS_PATH, dirname, filename)
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
        db.cursor.execute('''DELETE FROM contents
                          WHERE cstatus != -1 or end > NOW()''')
        # 番組表更新予定時間を初期化
        db.cursor.execute("UPDATE stations SET nextaired = '1970-01-01 09:00:00'")
        # 設定画面をデフォルトに設定
        shutil.copy(os.path.join(Common.DATA_PATH, 'settings', 'default.xml'), Common.DIALOG_FILE)
        # PROFILE_PATH/scheduleを初期化
        if os.path.exists(os.path.join(self.PROFILE_PATH, 'schedule')) is False:
            os.makedirs(os.path.join(self.PROFILE_PATH, 'schedule'), exist_ok=True)
        # HLS_CACHE_PATHをクリア
        if os.path.isdir(self.HLS_CACHE_PATH) is True:
            shutil.rmtree(self.HLS_CACHE_PATH)
        os.makedirs(self.HLS_CACHE_PATH)
        # ローカルプロキシを初期化
        self.httpd = LocalProxy()
        # 別スレッドでローカルプロキシを起動
        thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        thread.start()

    def monitor(self):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', time=3000)
        # スレッドのDBインスタンスを作成
        db = ThreadLocal.db = DB()
        # 認証予定時刻
        self.update_auth = 0
        # ダウンロードプロセスを格納するキューを初期化
        self.queue = queue.Queue()
        # 監視を開始
        monitor = xbmc.Monitor()
        while monitor.abortRequested() is False:
            # radiko認証更新
            self.maintain_auth()
            # 番組表更新
            self.maintain_schedule()
            # ダウンロード開始判定
            self.maintain_download()
            # CHECK_INTERVALの間待機
            t = time.time()
            dt = t - int(t)
            dt += int(t) % self.CHECK_INTERVAL
            monitor.waitForAbort(self.CHECK_INTERVAL - dt)  # 更新時刻がCHECK_INTERVALの倍数になるように端数を調整
        # ローカルプロキシを終了
        self.log('shutting down local proxy.')
        self.httpd.shutdown()
        # スレッドのプロセスを終了
        self.log('shutting down thread processes.')
        while self.queue.qsize() > 0:
            process = self.queue.get()
            if process.poll() is None:  # 実行中だったら
                process.kill()
        # スレッドのDBインスタンスを終了
        db.conn.close()
        # 監視終了を通知
        self.log('exit monitor.')
