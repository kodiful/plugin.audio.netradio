# -*- coding: utf-8 -*-

import time
import importlib
import threading
import json
import queue

import xbmc

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.scrapers.schedule.common import DummyScraper


class ScheduleManager(Common):

    def __init__(self, region, pref):
        self.region = region
        self.pref = pref

    def maintain_schedule(self, vis=None):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # まずNHK、RDKを更新
        self.maintain_nhk_and_rdk()
        # 番組情報を更新する放送局のリストを作成
        stations = []
        if vis is None:
            # 表示中の放送局
            front_stations = db.front_stations()
            # 表示中の放送局をリストに格納
            sql = f'SELECT protocol, sid FROM stations WHERE sid IN {front_stations}'
            db.cursor.execute(sql)
            stations.extend([(protocol, sid, 1) for (protocol, sid) in db.cursor.fetchall()])
            # 表示されていない放送局のうちトップ（ダウンロード対象）の放送局をリストに格納
            sql = f'SELECT protocol, sid FROM stations WHERE top = 1 AND vis = 1 AND sid NOT IN {front_stations}'
            db.cursor.execute(sql)
            stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
        else:
            # 表示中の放送局をリストに格納
            stations.extend(vis)
            # 表示中の放送局をDBに格納
            sql = 'UPDATE status SET front = :front'
            self.db.cursor.execute(sql, {'front': json.dumps(list(map(lambda x: x[1], vis)))})
        # 更新実行
        for protocol, sid, visible in stations:
            thread = threading.Thread(target=scheduler, args=[protocol, sid, visible], daemon=True)
            thread.start()

    def maintain_nhk_and_rdk(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 番組情報を更新する放送局のリストを作成
        stations = []
        # NHKから一つリストに追加
        sql = '''SELECT protocol, sid FROM stations
        WHERE protocol = 'NHK' AND region = :region ORDER BY sid LIMIT 1'''
        db.cursor.execute(sql, {'region': self.region})
        stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
        # RDKから一つリストに追加
        sql = '''SELECT protocol, sid FROM stations
        WHERE protocol = 'RDK' AND pref = :pref ORDER BY sid LIMIT 1'''
        db.cursor.execute(sql, {'pref': self.pref})
        stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
        # 更新実行
        threads = []
        for protocol, sid, visible in stations:
            thread = threading.Thread(target=scheduler, args=[protocol, sid, visible], daemon=True)
            thread.start()
            threads.append(thread)
        # すべてのスレッドが完了するまで待つ
        for thread in threads:
            thread.join()


def scheduler(protocol, sid, visible):
    # スレッドのDBインスタンスを作成
    ThreadLocal.db = DB()
    # scraperを初期化
    try:
        module_name = f'resources.lib.scrapers.schedule.{protocol}'
        module = importlib.import_module(module_name)
        Scraper = getattr(module, 'Scraper')
        scraper = Scraper(sid)
    except ModuleNotFoundError:
        scraper = DummyScraper(sid)
    nextaired0, nextaired1 = scraper.get_nextaired()
    # 現在時刻
    now = Common.now()
    # 再描画フラグ
    refresh = False
    # 番組情報の更新予定時刻を超えていたら実行
    if now > nextaired0:
        # 番組データを取得
        count = scraper.update()
        if count > 0:
            refresh = visible
            scraper.set_nextaired0()  # DBを更新
        if count == -1:
            # エラーで取得できなかった場合、NHK, RDK以外は24時間後に再実行
            if protocol not in ('NHK', 'RDK'):
                refresh = visible
                scraper.set_nextaired0(hours=24)  # DBを更新
                nextaired1 = scraper.set_nextaired1(hours=24)  # DBを更新
    # 表示中の放送局で表示時刻を超えていたら実行
    if now > nextaired1:
        # 表示中の時刻を確認
        nearest = scraper.search_nextaired1()
        # 記録されている時刻と異なっていたら再描画する
        if nearest != nextaired1:
            refresh = visible
            scraper.set_nextaired1()  # DBを更新
    # 再描画
    if refresh:
        # 表示中画面がこのアドオン画面だったら再描画する
        path = xbmc.getInfoLabel('Container.FolderPath')
        argv = 'plugin://%s/' % Common.ADDON_ID
        if path == argv or path.startswith(f'{argv}?action=show_stations'):
            Common.refresh()
    # スレッドのDBインスタンスを終了
    ThreadLocal.db.cursor.close()
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
