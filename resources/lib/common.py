# -*- coding: utf-8 -*-

import os
import inspect
import json
import requests
import datetime

import xbmc
import xbmcaddon
import xbmcvfs


class Common:

    # addon
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')
    ADDON_NAME = ADDON.getAddonInfo('name')

    # utilities
    GET = ADDON.getSetting
    SET = ADDON.setSetting
    STR = ADDON.getLocalizedString

    # addon paths
    PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')

    # directory
    DIRECTORY_ROOT = os.path.join(PROFILE_PATH, 'stations')
    DIRECTORY_PATH = os.path.join(DIRECTORY_ROOT, 'directory')
    INDEX_PATH = os.path.join(DIRECTORY_ROOT, 'index')
    LOGO_PATH = os.path.join(DIRECTORY_ROOT, 'logo')

    # timetable
    TIMETABLE_ROOT = os.path.join(PROFILE_PATH, 'timetable')
    TIMETABLE_PATH = os.path.join(TIMETABLE_ROOT, 'timetable')

    # keywords
    KEYWORDS_PATH = os.path.join(PROFILE_PATH, 'keywords')

    # queue, download
    PENDING_PATH = os.path.join(PROFILE_PATH, 'queue', 'pending')
    PROCESSING_PATH = os.path.join(PROFILE_PATH, 'queue', 'processing')
    DOWNLOAD_PATH = os.path.join(PROFILE_PATH, 'queue', 'download')

    # HLS chache
    HLS_CACHE_PATH = os.path.join(PROFILE_PATH, 'hls_cache')

    # radiko auth file
    AUTH_FILE = os.path.join(PROFILE_PATH, 'auth.json')

    # settings file
    SETTINGS_FILE = os.path.join(PROFILE_PATH, 'settings.xml')

    # image cache
    IMAGE_CACHE_DB = os.path.join(xbmcvfs.translatePath('special://database'), 'Textures13.db')


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
        # ログレベルを設定
        if options.get('error', False):
            level = xbmc.LOGERROR
        elif options.get('notice', False):
            level = xbmc.LOGINFO
        elif addon.getSetting('debug') == 'true':
            level = xbmc.LOGINFO
        else:
            level = None
        # メッセージ
        messages = ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        if level:
            frame = inspect.currentframe().f_back
            xbmc.log('%s: %s(%d): %s: %s' % (
                addon.getAddonInfo('id'),
                os.path.basename(frame.f_code.co_filename),
                frame.f_lineno,
                frame.f_code.co_name,
                messages
            ), level)

    @staticmethod
    def now():
        return datetime.datetime.now().timestamp()

    @staticmethod
    def nowplaying():
        path = None
        if xbmc.Player().isPlaying():
            item = xbmc.Player().getPlayingItem()
            path = item.getPath()  # http://127.0.0.1:8088/jcba?id=fmblueshonan
        return path
    
    @staticmethod
    def load(url):
        res = requests.get(url)
        return res.content.decode('utf-8')

    @staticmethod
    def write(path, data):
        with open(path, 'wb') as f:
            f.write(data.encode('utf-8'))

    @staticmethod
    def read(path):
        with open(path, 'rb') as f:
            return f.read().decode('utf-8')

    @staticmethod
    def read_as_json(path):
        return json.loads(Common.read(path))

    @staticmethod
    def write_as_json(path, data):
        Common.write(path, json.dumps(data, ensure_ascii=False, indent=4))
