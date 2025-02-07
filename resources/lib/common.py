# -*- coding: utf-8 -*-

import os
import inspect

import xbmc
import xbmcaddon
import xbmcvfs


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
    DB_FILE = os.path.join(PROFILE_PATH, 'download.db')

    # image cache
    IMAGE_CACHE = os.path.join(xbmcvfs.translatePath('special://database'), 'Textures13.db')

    # HLS chache
    HLS_CACHE_PATH = os.path.join(PROFILE_PATH, 'hls_cache')

    # contents directory
    CONTENTS_PATH = GET('folder')

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
    def nowplaying():
        path = None
        if xbmc.Player().isPlaying():
            item = xbmc.Player().getPlayingItem()
            path = item.getPath()  # http://127.0.0.1:8088/jcba?id=fmblueshonan
        return path
