# -*- coding: utf-8 -*-

import os

from resources.lib.common import Common
from resources.lib.db import ThreadLocal


class Common(Common):

    DOWNLOAD = 1
    TIMER = 2
    KEYWORD = 4
    ALL = DOWNLOAD | TIMER | KEYWORD

    SETTINGS_PATH = os.path.join(Common.PLUGIN_PATH, 'resources', 'data', 'settings')

    def __init__(self):
        # DBの共有インスタンス
        self.db = ThreadLocal.db
