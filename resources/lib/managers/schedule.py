# -*- coding: utf-8 -*-

import time
import importlib
import threading
import json

import xbmc

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal


class Scheduler(Common):

    def __init__(self, protocol, sid):
        self.protocol = protocol
        self.sid = sid
        # DBの共有インスタンス
        self.db = ThreadLocal.db
        # Scraperのインスタンス
        module_name = f'resources.lib.scrapers.schedule.{protocol}'
        module = importlib.import_module(module_name)
        Scraper = getattr(module, 'Scraper')
        self.scraper = Scraper(sid)
        # nextaired初期値設定
        self.nextaired = self.scraper.get_nextaired()

    def update(self):
        # 番組データを取得
        count = self.scraper.update()
        if count > 0:
            self.nextaired = self.scraper.set_nextaired()
        if count < 0:
            # NHK, radiko以外はstationsテーブルのschedule, downloadを0に変更
            if  self.protocol not in ('NHK', 'RDK'):
                sql = 'UPDATE stations SET schedule = 0, download = 0 WHERE sid = :sid'
                self.db.cursor.execute(sql, {'sid': self.sid})
                self.log('schedule & download disabled:', self.protocol, self.sid)
        return count
   
    def _next_aired(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 更新予定時刻のデフォルト値
        epoch = 0
        # 更新予定時刻を検索
        if self.protocol in ('NHK', 'RDK'):
            sql = '''
            SELECT MIN(c.end)
            FROM contents c JOIN stations s ON c.sid = s.sid
            WHERE c.end > NOW() AND schedule = 1 AND s.protocol = :protocol
            '''
            db.cursor.execute(sql, {'protocol': self.protocol})
            end, = db.cursor.fetchone()
            if end is not None:
                epoch = self.datetime(end).timestamp()
                # DBに値を格納
                sql = 'UPDATE stations SET nextaired = :nextaired WHERE protocol = :protocol'
                db.cursor.execute(sql, {'nextaired': end, 'protocol': self.protocol})
        else:
            sql = '''
            SELECT MIN(c.end)
            FROM contents c JOIN stations s ON c.sid = s.sid
            WHERE c.end > NOW() AND schedule = 1 AND s.sid = :sid
            '''
            db.cursor.execute(sql, {'sid': self.sid})
            end, = db.cursor.fetchone()
            if end is not None:
                epoch = self.datetime(end).timestamp()
                # DBに値を格納
                sql = 'UPDATE stations SET nextaired = :nextaired WHERE sid = :sid'
                db.cursor.execute(sql, {'nextaired': end, 'sid': self.sid})
        return epoch


class ScheduleManager(Common):

    def __init__(self, region, pref):
        self.region = region
        self.pref = pref

    def maintain_schedule(self, visible_stations=None):
        # DBの共有インスタンス
        db = ThreadLocal.db
        if visible_stations is None:
            # 更新対象の放送局の指定がない場合（monitorによる定期実行の場合）は、更新対象の放送局のリストを作成する
            interesting_stations = []
            # 表示中の放送局をリストに追加
            sql = '''SELECT s.protocol, s.sid
            FROM status JOIN json_each(status.front) AS je ON je.value = s.sid JOIN stations AS s ON je.value = s.sid
            WHERE s.schedule = 1'''
            db.cursor.execute(sql)
            interesting_stations.extend([(protocol, sid, 1) for (protocol, sid) in db.cursor.fetchall()])
            # ダウンロード対象の放送局をリストに格納
            sql = 'SELECT protocol, sid FROM stations WHERE download = 1'
            db.cursor.execute(sql)
            interesting_stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
            # トップの放送局をリストに格納
            sql = 'SELECT protocol, sid FROM stations WHERE schedule = 1 AND top = 1'
            db.cursor.execute(sql)
            interesting_stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
            # ユニーク化する
            stations = self._filter(interesting_stations)
        else:
            # 表示中の放送局をstatusテーブルに格納
            sql = 'UPDATE status SET front = :front'
            self.db.cursor.execute(sql, {'front': json.dumps(list(map(lambda x: x[1], visible_stations)))})
            # 表示中の放送局を更新対象の放送局とする
            stations = self._filter(visible_stations)
        # 放送局毎に更新予定時刻を個別のスレッドで確認し必要があれば再描画する
        threads = []
        for protocol, sid, visible in stations:
            thread = threading.Thread(target=scheduler, args=[protocol, sid, visible], daemon=True)
            thread.start()
            threads.append(thread)
        # 更新対象の放送局の指定がない場合（monitorによる定期実行の場合）はすべてのスレッドが完了するまで待つ
        if visible_stations is None:
            for thread in threads:
                thread.join()

    def _filter(self, tuples):
        # [(protocol, sid, visible), ...] visible = 1 を優先、NHKとRDKはsidに関わらず一つだけ
        nhk = list(filter(lambda x: x[0] == 'NHK', tuples))
        rdk = list(filter(lambda x: x[0] == 'RDK', tuples))
        others = list(filter(lambda x: x[0] not in ('NHK', 'RDK'), tuples))
        # nfkとrdkからvisible=1を優先して一つだけ採用
        nhk = sorted(nhk, key=lambda x: x[2], reverse=True)[0:1]
        rdk = sorted(rdk, key=lambda x: x[2], reverse=True)[0:1]
        # othersをフィルタリング
        seen = set()
        result = []
        # まずvisible=1の要素を優先して追加
        for protocol, sid, visible in set(others):
            if visible == 1:
                seen.add((protocol, sid))  # (protocol, sid)を記録
                result.append((protocol, sid, visible))
        # visible=1の(protocol, sid)が追加されていない場合のみvisible=0を追加
        for protocol, sid, visible in set(others):
            if visible == 0 and (protocol, sid) not in seen:
                result.append((protocol, sid, visible))
        return nhk + rdk + result


def scheduler(protocol, sid, visible):
    # スレッドのDBインスタンスを作成
    db = ThreadLocal.db = DB()
    # 現在時刻
    now = time.time()
    # workerを初期化
    worker = Scheduler(protocol, sid)
    # 更新予定時刻を過ぎていたら
    nextaired = Common.datetime(worker.nextaired).timestamp()
    if now > nextaired:
        # 番組情報の更新を確認
        count = worker.update()
        # 表示中画面を確認
        path = xbmc.getInfoLabel('Container.FolderPath')
        argv = 'plugin://%s/' % Common.ADDON_ID
        # このスレッドの放送局が表示中、かつ表示中画面がこのアドオン画面だったら再描画する
        if visible == 1 and (path == argv or path.startswith(f'{argv}?action=show')):
            # 番組情報に更新があったら即時再描画する
            if count != 0:                    
                xbmc.executebuiltin('Container.Refresh')
                db.cursor.execute('UPDATE status SET refresh = NOW()')  # 再描画時刻を記録
            else:
                # 前回の再描画より1秒以上経過していたら再描画
                db.cursor.execute('SELECT refresh FROM status')
                refresh, = db.cursor.fetchone()
                if now > Common.datetime(refresh).timestamp() + 1:                    
                    xbmc.executebuiltin('Container.Refresh')
                    db.cursor.execute('UPDATE status SET refresh = NOW()')  # 再描画時刻を記録
    # スレッドのDBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
