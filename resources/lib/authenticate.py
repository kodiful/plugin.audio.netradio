# -*- coding: utf-8 -*-

from resources.lib.common import Common
import urllib.request
from base64 import b64encode


class Authenticate(Common):

    # キー
    AUTH_KEY = 'bcd151073c03b352e1ef2fd66c32209da9ca0afa'
    # URL
    AUTH1_URL = 'https://radiko.jp/v2/api/auth1'
    AUTH2_URL = 'https://radiko.jp/v2/api/auth2'

    def __init__(self, renew=True):
        # responseを初期化
        self.response = response = {'auth_key': self.AUTH_KEY, 'auth_token': '', 'area_id': '', 'authed': 0}
        # auth_tokenを取得
        response = self.appIDAuth(response)
        if response and response['auth_token']:
            # area_idを取得
            response = self.challengeAuth(response)
            if response and response['area_id']:
                response['authed'] = 1
                # インスタンス変数に格納
                self.response = response
            else:
                self.log('challengeAuth failed.')
        else:
            self.log('appIDAuth failed.')

    # auth_tokenを取得
    def appIDAuth(self, response):
        # ヘッダ
        headers = {
            'x-radiko-device': 'pc',
            'x-radiko-app-version': '0.0.1',
            'x-radiko-user': 'dummy_user',
            'x-radiko-app': 'pc_html5'
        }
        try:
            # リクエスト
            req = urllib.request.Request(self.AUTH1_URL, headers=headers)
            # レスポンス
            auth1 = urllib.request.urlopen(req).info()
        except Exception as e:
            self.log(str(e), error=True)
            return
        response['auth_token'] = auth1['X-Radiko-AuthToken']
        response['key_offset'] = int(auth1['X-Radiko-KeyOffset'])
        response['key_length'] = int(auth1['X-Radiko-KeyLength'])
        return response

    # partialkeyを取得
    def createPartialKey(self, response):
        partial_key = response['auth_key'][response['key_offset']:response['key_offset'] + response['key_length']]
        return b64encode(partial_key.encode()).decode()

    # area_idを取得
    def challengeAuth(self, response):
        # ヘッダ
        response['partial_key'] = self.createPartialKey(response)
        headers = {
            'x-radiko-authtoken': response['auth_token'],
            'x-radiko-device': 'pc',
            'x-radiko-partialkey': response['partial_key'],
            'x-radiko-user': 'dummy_user'
        }
        try:
            # リクエスト
            req = urllib.request.Request(self.AUTH2_URL, headers=headers)
            # レスポンス
            auth2 = urllib.request.urlopen(req).read().decode()
        except Exception as e:
            self.log(str(e), error=True)
            return
        response['area_id'] = auth2.split(',')[0].strip()
        return response
