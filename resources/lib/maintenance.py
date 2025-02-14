# -*- coding: utf-8 -*-

import time
import importlib
import threading

import xbmc

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal


class Maintainer(Common):

    def __init__(self, protocol, sid):
        self.protocol = protocol
        self.sid = sid
        # DBの共有インスタンス
        db = ThreadLocal.db
        # Scraperのインスタンス
        module_name = f'resources.lib.schedule.{protocol}'
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
        return count
   
    def _next_aired(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 更新予定時刻のデフォルト値
        epoch = 0
        if self.protocol in ('NHK', 'RDK'):
            # 更新予定時刻を検索
            sql = '''
            SELECT MIN(c.end)
            FROM contents c JOIN stations s ON c.sid = s.sid
            WHERE c.end > NOW() AND c.cstatus > -1 AND s.protocol = :protocol AND schedule = 1
            '''
            db.cursor.execute(sql, {'protocol': self.protocol})
            end, = db.cursor.fetchone()
            if end is not None:
                epoch = self.datetime(end).timestamp()
                # DBに値を格納
                sql = 'UPDATE stations SET nextaired = :nextaired WHERE protocol = :protocol'
                db.cursor.execute(sql, {'nextaired': end, 'protocol': self.protocol})
        else:
            # 次の更新予定時刻を検索
            sql = '''
            SELECT MIN(c.end)
            FROM contents c JOIN stations s ON c.sid = s.sid
            WHERE c.end > NOW() AND c.cstatus > -1 AND s.sid = :sid AND schedule = 1
            '''
            db.cursor.execute(sql, {'protocol': self.protocol, 'sid': self.sid})
            end, = db.cursor.fetchone()
            if end is not None:
                epoch = self.datetime(end).timestamp()
                # DBに値を格納
                sql = 'UPDATE stations SET nextaired = :nextaired WHERE sid = :sid'
                db.cursor.execute(sql, {'nextaired': end, 'sid': self.sid})
        return epoch


class Maintenance(Common):

    def __init__(self, region, pref):
        self.region = region
        self.pref = pref

    def maintain_schedule(self, interval):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 更新対象とする放送局のセット
        stations = []
        # 表示中の放送局をリストに追加
        sql = '''SELECT s.protocol, s.sid
        FROM status JOIN json_each(status.front) AS je ON je.value = s.sid JOIN stations AS s ON je.value = s.sid
        WHERE s.schedule = 1'''
        db.cursor.execute(sql)
        stations.extend([(protocol, sid, 1) for (protocol, sid) in db.cursor.fetchall()])
        # ダウンロード対象の放送局をリストに格納
        sql = 'SELECT protocol, sid FROM stations WHERE download = 1'
        db.cursor.execute(sql)
        stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
        # トップの放送局をリストに格納
        sql = 'SELECT protocol, sid FROM stations WHERE schedule = 1 AND top = 1'
        db.cursor.execute(sql)
        stations.extend([(protocol, sid, 0) for (protocol, sid) in db.cursor.fetchall()])
        # 放送局毎に更新予定時刻を個別のスレッドで確認し、必要があれば再描画する
        for protocol, sid, visible in self._filter(stations):
            thread = threading.Thread(target=updater, args=[protocol, sid, visible, interval])
            thread.start()

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

def updater(protocol, sid, visible, interval):
    # スレッドのDBインスタンスを作成
    ThreadLocal.db = DB()
    # 現在時刻
    now = time.time()
    # maintainerを初期化
    maintainer = Maintainer(protocol, sid)
    # 更新予定時刻を過ぎていたら
    nextaired = Common.datetime(maintainer.nextaired).timestamp()
    if now > nextaired:
        # 更新情報を確認
        count = maintainer.update()
        # 時間経過直後、または更新があったら再描画する
        if now < nextaired + interval or count > 0:
            # 表示中画面がこのアドオン画面、かつaction=showだったら再描画する
            path = xbmc.getInfoLabel('Container.FolderPath')
            argv = 'plugin://%s/' % Common.ADDON_ID
            if path == argv or path.startswith(f'{argv}?action=show'):
                # このスレッド処理している放送局が表示中だったら再描画する
                if visible:
                    xbmc.executebuiltin('Container.Refresh')
    # スレッドのDBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
