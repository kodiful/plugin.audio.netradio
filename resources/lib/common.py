# -*- coding: utf-8 -*-

import os
import sys
import calendar
import traceback
import inspect
import html
import re
import unicodedata
import warnings
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

import xbmc
import xbmcaddon
import xbmcvfs

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)


class Common:

    # addon
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')
    ADDON_NAME = ADDON.getAddonInfo('name')
    ADDON_VERSION = ADDON.getAddonInfo('version')

    # utilities
    GET = ADDON.getSetting
    SET = ADDON.setSetting
    STR = ADDON.getLocalizedString

    # addon paths
    PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    LIB_PATH = os.path.join(PLUGIN_PATH, 'resources', 'lib')
    DATA_PATH = os.path.join(PLUGIN_PATH, 'resources', 'data')

    # settings file
    DIALOG_FILE = os.path.join(PLUGIN_PATH, 'resources', 'settings.xml')
    SETTINGS_FILE = os.path.join(PROFILE_PATH, 'settings.xml')

    # db file
    DB_FILE = os.path.join(PROFILE_PATH, 'NetRadio.db')

    # image cache
    IMAGE_CACHE = os.path.join(xbmcvfs.translatePath('special://database'), 'Textures13.db')

    # contents directory
    CONTENTS_PATH = GET('folder')

    # 更新確認のインターバル（秒）
    CHECK_INTERVAL = 10

    # radiko認証のインターバル（秒）
    AUTH_INTERVAL = 3600

    # user-agent
    USER_AGENT = 'python'

    # hls
    HLS_CACHE_PATH = os.path.join(PROFILE_PATH, 'hls_cache')
    HLS_FILE = 'hls.m3u8'
    HLS_TIME = 5

    @staticmethod
    def notify(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ポップアップする時間
        time = options.get('time', 10000)
        # ポップアップアイコン
        image = options.get('image', None)
        if image:
            pass
        elif options.get('error', False):
            image = 'DefaultIconError.png'
        else:
            image = 'DefaultIconInfo.png'
        # メッセージ
        messages = ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        Common.log(messages, error=options.get('error', False))
        # ポップアップ通知
        xbmc.executebuiltin('Notification("%s","%s",%d,"%s")' % (addon.getAddonInfo('name'), messages, time, image))

    @staticmethod
    def log(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ログレベル、メッセージを設定
        if isinstance(messages[0], Exception):
            level = xbmc.LOGERROR
            message = '\n'.join(list(map(lambda x: x.strip(), traceback.TracebackException.from_exception(messages[0]).format())))
            if len(messages[1:]) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages[1:]))
        else:
            level = xbmc.LOGINFO
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            name = frame.f_code.co_name
            id = addon.getAddonInfo('id')
            message = f'Addon "{id}", File "{filename}", line {lineno}, in {name}'
            if len(messages) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        xbmc.log(message, level)

    @staticmethod
    def datetime(datetimestr):
        # 2023-04-20 05:00:00 -> datetime(2023, 4, 20, 5, 0, 0)
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, time = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        h, m, s = map(int, time.split(':'))
        return datetime(year, month, day, h, m, s)

    @staticmethod
    def weekday(datetimestr):
        # 2023-04-20 05:00:00 -> calendar.weekday(2023, 4, 20) -> 3
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, _ = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        return calendar.weekday(year, month, day)

    @staticmethod
    def now(hours=0, minutes=0):
        # 2025-02-22 05:35:43
        if hours > 0 or minutes > 0:
            now = datetime.now() + timedelta(hours=hours, minutes=minutes)
        else:
            now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def setArt(listitem, name):
        logo = os.path.join(Common.DATA_PATH, 'icons', f'{name}.png')
        listitem.setArt({'thumb': logo, 'icon': logo})

    @staticmethod
    def refresh(top=False):
        if top:
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('Container.Refresh')

    @staticmethod
    def normalize(text, unescape=False, parser=False):
        if text is None: return ''
        text = re.sub('＜', '&LT;', text)
        text = re.sub('＞', '&GT;', text)
        text = re.sub('～', '〜', text)  # 全角チルダ(U+FF5E) -> 波ダッシュ(U+301C)
        text = unicodedata.normalize('NFKC', text)  # 全角チルダは半角チルダ(~)に変換されるが波ダッシュは変換されない
        text = re.sub('&LT;', '＜', text)
        text = re.sub('&GT;', '＞', text)
        text = re.sub('🎤', ' ', text)  # レディオモモ
        if unescape:
            text = html.unescape(text)
        if parser:
            text = BeautifulSoup(text, 'html.parser').prettify()
        text = re.sub('[\r\n\t]', ' ', text)
        text = re.sub('[ ]{2,}', ' ', text)
        return text.strip()

    @staticmethod
    def sanitize(description):
        description = re.sub(r'<p class="(?:act|info|desc)">(.*?)</p>', r'\1\n\n', description)
        description = re.sub(r'<br */>', r'\n', description)
        description = re.sub(r'<.*?>', '', description)
        description = re.sub(r' *\n *', r'\n', description)
        description = re.sub(r'\n{3,}', r'\n\n', description)
        return description

    @staticmethod
    def is_enabled(key):
        download = Common.GET('download') == 'true' and os.path.exists(Common.GET('folder'))
        if key == 'download':
            return download
        if key == 'rss':
            return download and Common.GET('rss') == 'true' and Common.GET('rssurl') != ''
