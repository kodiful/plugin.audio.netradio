# -*- coding: utf-8 -*-

import os
import inspect
import json

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

    # paths
    PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    # directory
    DIRECTORY_ROOT = os.path.join(PROFILE_PATH, 'directory')
    DIRECTORY_PATH = os.path.join(DIRECTORY_ROOT, 'directory')
    LOGO_PATH = os.path.join(DIRECTORY_ROOT, 'logo')
    # timetable
    TIMETABLE_ROOT = os.path.join(PROFILE_PATH, 'timetable')
    TIMETABLE_PATH = os.path.join(TIMETABLE_ROOT, 'timetable')
    # HLS chache
    HLS_CACHE_PATH = os.path.join(PROFILE_PATH, 'hls_cache')
    # files
    AUTH_FILE = os.path.join(PROFILE_PATH, 'auth.json')

    @staticmethod
    def notify(message, **options):
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
        # ログ出力
        Common.log(message, error=options.get('error', False))
        # ポップアップ通知
        xbmc.executebuiltin('Notification("%s","%s",%d,"%s")' % (addon.getAddonInfo('name'), message, time, image))

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
        # ログ出力
        if level:
            frame = inspect.currentframe().f_back
            xbmc.log('%s: %s(%d): %s: %s' % (
                addon.getAddonInfo('id'),
                os.path.basename(frame.f_code.co_filename),
                frame.f_lineno,
                frame.f_code.co_name,
                ' '.join(map(lambda x: str(x), messages))
            ), level)

    @staticmethod
    def write_as_json(data, path):
        data = json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4)
        with open(path, 'w') as f:
            f.write(data)

    @staticmethod
    def read_as_json(path):
        with open(path, 'r') as f:
            data = json.loads(f.read())
        return data
