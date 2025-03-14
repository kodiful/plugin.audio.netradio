# -*- coding: utf-8 -*-

import os
import shutil

from .common import Common
from .download import Download
from .timer import Timer
from .keyword import Keyword

import xbmc
import xbmcgui


class Settings(Common):

    def __init__(self, flags=Common.ALL):
        super().__init__()
        self.download = flags & self.DOWNLOAD
        self.timer = flags & self.TIMER
        self.keyword = flags & self.KEYWORD

    def get(self, kid=0, sid=0):
        if sid > 0:
            # 放送中の番組を検索
            sql = 'SELECT * FROM contents WHERE sid = :sid AND end > NOW() AND kid > -1 ORDER BY start'
            self.db.cursor.execute(sql, {'sid': sid})
            onair = [data for data in self.db.cursor.fetchall()]
            # 放送中の番組保存をconfirm
            if len(onair) > 0:
                yesno = xbmcgui.Dialog().yesnocustom(self.STR(30491), self.STR(30163) % onair[0]['title'], self.STR(30492))
            else:
                yesno = xbmcgui.Dialog().yesnocustom(self.STR(30491), self.STR(30164), self.STR(30492))
            if yesno == 0:
                # キャンセル
                pass
            elif yesno == 1:
                if len(onair) > 0:
                    # 放送中の番組を保存
                    self.get1_download(onair[0]['cid'])
                else:
                    # 番組情報が取得できないときの処理を選択
                    yesno = xbmcgui.Dialog().yesnocustom(self.STR(30491), self.STR(30162) % self.GET('period'), self.STR(30492))
                    if yesno == 0:
                        # キャンセル
                        pass
                    elif yesno == 1:
                        # デフォルト値でタイマー保存
                        sql = 'SELECT station FROM stations WHERE sid = :sid'
                        self.db.cursor.execute(sql, {'sid': sid})
                        station, = self.db.cursor.fetchone()
                        start = self.now()
                        end = self.now(minutes=int(self.GET('period')))
                        self.get1_timer(station, station, start, end)
                    elif yesno == 2:
                        # 詳細設定
                        self.get2(kid, sid)
            elif yesno == 2:
                # 詳細設定
                self.get2(kid, sid)
        else:
            # 詳細設定
            self.get2(kid, sid)

    def get1_download(self, cid=0):
        download = Download()
        download.get(cid)
        download.set()

    def get1_timer(self, station, title, start, end):
        timer = Timer()
        timer.get( station, title, start, end)
        timer.set()

    def get2(self, kid=0, sid=0):
        kid = kid
        sid = sid
        cid = 0
        title = ''
        station = ''
        start = ''
        end = ''
        if sid > 0:
            # 番組情報からキーワード設定
            sql = 'SELECT title, station, cid, start, end FROM contents WHERE sid = :sid AND end > NOW() AND kid > -1 ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': sid})
            choices = [(title, station, cid, start, end) for title, station, cid, start, end in self.db.cursor.fetchall()]
            if len(choices) > 0:
                # 選択ダイアログを表示
                titlelist = [title for title, station, cid, start, end in choices]
                index = xbmcgui.Dialog().select(self.STR(30528), titlelist)
                if index == -1:
                    return
                title, station, cid, start, end = choices[index]
            else:
                sql = 'SELECT station FROM stations WHERE sid = :sid'
                self.db.cursor.execute(sql, {'sid': sid})
                station, = self.db.cursor.fetchone()
                self.download = self.keyword = 0
        # 各パーツのテンプレートを生成する
        download = timer = keyword = ''
        # download
        if self.download:
            builder = Download()
            builder.prep(title)
            builder.get(cid)
            download = builder.template
        # timer
        if self.timer:
            builder = Timer()
            builder.prep()
            builder.get(station, title, start, end)
            timer = builder.template
        # keyword
        if self.keyword:
            builder = Keyword()
            builder.prep()
            builder.get(kid, sid, title, station)
            keyword = builder.template
        # 設定画面のテンプレートを読み込む
        with open(os.path.join(self.SETTINGS_PATH, 'template.xml')) as f:
            template = f.read()
        # 設定画面のテンプレートに各パーツのテンプレートを適用
        template = template.format(download=download, timer=timer, keyword=keyword)
        # 設定画面として書き出す
        with open(self.DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(template)
        # 設定画面を開く
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        # 1秒待って設定画面をデフォルトに戻す
        xbmc.sleep(1000)
        shutil.copy(os.path.join(self.SETTINGS_PATH, 'default.xml'), self.DIALOG_FILE)

    def set(self, action):
        if action == 'set_download':
            Download().set()
        elif action == 'set_timer':
            Timer().set()
        elif action == 'set_keyword':
            Keyword().set()
        elif action == 'delete_keyword':
            Keyword().delete()
        else:
            self.log('undefined action:', action)
