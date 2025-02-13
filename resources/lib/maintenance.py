# -*- coding: utf-8 -*-

import time
import importlib

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Maintainer(Common):

    def __init__(self, protocol, region='', pref='', sid=0):
        self.protocol = protocol
        self.region = region
        self.pref = pref
        self.sid = sid
        module_name = f'resources.lib.schedule.{protocol}'
        module = importlib.import_module(module_name)
        Scraper = getattr(module, 'Scraper')
        self.scraper = Scraper(region=region, pref=pref, sid=sid)
        self.next_aired = self._next_aired()

    def update(self):
        # 番組データを取得
        count = self.scraper.update()
        if count > 0:
            self.next_aired = self._next_aired()  # 更新予定時刻を更新
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
            WHERE c.end > NOW() AND c.cstatus > -1 AND s.protocol = :protocol AND region = :region AND pref = :pref
            '''
            db.cursor.execute(sql, {'protocol': self.protocol, 'region': self.region, 'pref': self.pref})
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
            WHERE c.end > NOW() AND c.cstatus > -1 AND s.protocol = :protocol AND s.sid = :sid
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
        self.maintainer = {}

    def maintain_schedule(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 現在時刻
        now = time.time()
        # 更新する放送局のリスト
        stations = []
        # NHK、radikoをリストに格納
        sql = '''SELECT sid, protocol, schedule
        FROM stations WHERE
        (protocol = 'NHK' AND region = :region) OR
        (protocol = 'RDK' AND region = :region AND pref = :pref)'''
        db.cursor.execute(sql, {'region': self.region, 'pref': self.pref})
        stations.extend([(sid, protocol, schedule) for (sid, protocol, schedule) in db.cursor.fetchall()])
        # NHK, radiko以外のダウンロード対象の放送局をリストに格納
        sql = '''SELECT sid, protocol, schedule
        FROM stations WHERE
        protocol NOT IN ('NHK', 'RDK') AND download = 1'''
        db.cursor.execute(sql)
        stations.extend([(sid, protocol, schedule) for (sid, protocol, schedule) in db.cursor.fetchall()])
        # トップ表示の放送局をリストに格納
        sql = "SELECT sid, protocol, schedule FROM stations WHERE top = 1"
        db.cursor.execute(sql)
        stations.extend([(sid, protocol, schedule) for (sid, protocol, schedule) in db.cursor.fetchall()])
        # 表示中の放送局をリストに格納
        sql = '''SELECT s.sid, s.protocol, s.schedule
        FROM status
        JOIN json_each(status.front) AS je ON je.value = s.sid
        JOIN stations AS s ON je.value = s.sid
        '''
        db.cursor.execute(sql)
        stations.extend([(sid, protocol, schedule) for (sid, protocol, schedule) in db.cursor.fetchall()])
        # 更新対象の放送局の更新予定時刻を一つずつチェックする
        for sid, protocol, schedule in set(stations):
            maintainer = None
            # NHKは無条件で更新対象
            if protocol in 'NHK':
                maintainer = self.maintainer.get(protocol)
                if maintainer is None:
                    maintainer = self.maintainer[protocol] = Maintainer(protocol, region=self.region)
            # radikoは無条件で更新対象
            elif protocol in 'RDK':
                maintainer = self.maintainer.get(protocol)
                if maintainer is None:
                    maintainer = self.maintainer[protocol] = Maintainer(protocol, region=self.region, pref=self.pref)
            # 更新設定がある放送局は更新対象
            elif schedule == 1:
                maintainer = self.maintainer.get(sid)
                if maintainer is None:
                    maintainer = self.maintainer[sid] = Maintainer(protocol, sid=sid)
            # 更新対象であれば更新予定時刻をチェックする
            if maintainer is not None:
                # 更新予定時刻を過ぎていて、かつ番組情報挿入があればTrueを返す
                if now > maintainer.next_aired and maintainer.update() > 0:
                    return True
        return False
 