# -*- coding: utf-8 -*-

import os
import shutil
from resources.lib.settings.common import Common
from resources.lib.settings.modules.content import Content
from resources.lib.settings.modules.timer import Timer
from resources.lib.settings.modules.keyword import Keyword

import xbmc
import xbmcgui


class Settings(Common):

    def __init__(self, flags=Common.ALL):
        super().__init__()
        self.content = flags & self.CONTENT
        self.timer = flags & self.TIMER
        self.keyword = flags & self.KEYWORD

    def open(self, kid=0, sid=0):
        kid = kid
        sid = sid
        cid = 0
        title = ''
        station = ''
        if sid > 0:
            # 番組情報からキーワード設定
            sql = 'SELECT cid, title, station FROM contents WHERE sid = :sid AND end > NOW() AND kid > -1 ORDER BY start LIMIT 2'
            self.db.cursor.execute(sql, {'sid': sid})
            choices = [(cid, title, station) for cid, title, station in self.db.cursor.fetchall()]
            if len(choices) > 0:
                # 選択ダイアログを表示
                titlelist = [title for _, title, _ in choices]
                index = xbmcgui.Dialog().select(self.STR(30528), titlelist)
                if index == -1:
                    return
                cid, title, station = choices[index]
            else:
                self.content = self.keyword = 0
        # template processing
        content = timer = keyword = ''
        # content
        if self.content:
            inst = Content()
            inst.prep(title)
            inst.get(cid)
            content = inst.template
        # timer
        if self.timer:
            inst = Timer()
            inst.prep()
            inst.get(station)
            timer = inst.template
        # keyword
        if self.keyword:
            inst = Keyword()
            inst.prep()
            inst.get(kid, sid, title, station)
            keyword = inst.template
        # apply to template
        self.replace(content, timer, keyword)
        # キーワード設定画面を開く
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        xbmc.sleep(1000)
        self.restore()

    def replace(self, content, timer, keyword):
        with open(os.path.join(self.SETTINGS_PATH, 'template.xml')) as f:
            template = f.read()
        template = template.format(content=content, timer=timer, keyword=keyword)
        # 設定画面として書き出す
        with open(self.DIALOG_FILE, 'w', encoding='utf-8') as f:
            f.write(template)

    def restore(self):
        shutil.copy(os.path.join(self.SETTINGS_PATH, 'default.xml'), self.DIALOG_FILE)
                    
    def save(self, action):
        if action == 'set_download':
            Content().set()
        elif action == 'set_timer':
            Timer().set()
        elif action == 'set_keyword':
            Keyword().set()
        elif action == 'delete_keyword':
            Keyword().set()
        else:
            self.log('undefined action:', action)
        # 設定画面をデフォルトに戻す
        self.restore()
