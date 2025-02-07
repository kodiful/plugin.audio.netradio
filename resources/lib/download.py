# -*- coding: utf-8 -*-

import sys
import os
import ffmpeg  # https://github.com/kkroening/ffmpeg-python
import locale
import datetime
import time

from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.db import DB
from resources.lib.localproxy import LocalProxy
from resources.lib.holiday import Holiday

import xbmcplugin
import xbmcgui


class Download(Common):

    def __init__(self):
        # ロケール設定
        locale.setlocale(locale.LC_ALL, '')

    def show(self, kid):
        # DBへ接続
        self.db = DB()
        sql = '''SELECT * FROM contents c 
        JOIN keywords k ON c.kid = k.kid
        JOIN stations s ON c.sid = s.sid
        WHERE c.kid = :kid and c.status = -1
        ORDER BY c.start DESC'''
        self.db.cursor.execute(sql, {'kid': kid})
        for cksdata in self.db.cursor.fetchall():
            # リストアイテムを追加
            self._add_download(cksdata)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        # DBから切断
        self.db.conn.close()

    def _add_download(self, cksdata):
        li = xbmcgui.ListItem(self._title(cksdata))
        logo = os.path.join(self.PROFILE_PATH, 'stations', 'logo', str(cksdata['type']), str(cksdata['station']) + '.png')
        li.setArt({'thumb': logo, 'icon': logo})
        li.setInfo(type='music', infoLabels={'title': cksdata['title']})
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30109), {'action': 'open_folder', 'kid': cksdata['kid']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # 再生するファイルのパス
        url = os.path.join(self.CONTENTS_PATH, cksdata['dirname'], cksdata['filename'])
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li, isFolder=False)

    def _title(self, ckdata):
        # %Y年%m月%d日(%%s) %H:%M
        format = self.STR(30919)
        # 月,火,水,木,金,土,日
        weekdays = self.STR(30920)
        weekdays = weekdays.split(',')
        # 放送開始時刻
        d = datetime.datetime.strptime(ckdata['start'], '%Y-%m-%d %H:%M:%S')
        w = d.weekday()
        # 放送終了時刻
        end = ckdata['end'][11:16]
        # 8月31日(土)
        format = d.strftime(format)
        date1 = format % weekdays[w]
        # 2019-08-31
        date2 = d.strftime('%Y-%m-%d')
        # カラー
        if date2 in Holiday.HOLIDAYS or w == 6:
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        elif w == 5:
            title = '[COLOR blue]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        else:
            title = '%s-%s  [COLOR khaki]%s[/COLOR]' % (date1, end, ckdata['title'])
        return title

    def _contextmenu(self, name, args):
        self.contextmenu.append((name, 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))

    def download(self, cid, kid, filename, type, abbr, title, end, direct, queue):
        # DBへ接続
        db = DB()
        # radiko認証
        sql = 'SELECT auth_token FROM auth'
        db.cursor.execute(sql)
        token, = db.cursor.fetchone()
        # ストリームURL
        url = LocalProxy.proxy(type, abbr=abbr, direct=direct, token=token, download=True)
        # 時間
        duration = end - int(time.time())
        # ビットレート
        bitrate = self.GET('bitrate')
        if bitrate == 'auto':
            if duration <= 3600:
                bitrate = '192k'
            elif duration <= 4320:
                bitrate = '160k'
            elif duration <= 5400:
                bitrate = '128k'
            elif duration <= 7200:
                bitrate = '96k'
            else:
                bitrate = '64k'
        # 出力ディレクトリ
        sql = 'SELECT dirname FROM keywords WHERE kid = :kid'
        db.cursor.execute(sql, {'kid': kid})
        dirname, = db.cursor.fetchone()
        # 出力ファイル
        download_path = os.path.join(self.CONTENTS_PATH, dirname)
        os.makedirs(download_path, exist_ok=True)
        mp3file = os.path.join(download_path, filename)
        # ffmpeg実行
        kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
        process = ffmpeg.input(url, f='hls', t=duration).output(mp3file, **kwargs).run_async(pipe_stderr=True)
        # プロセスをキューに追加
        queue.put(process)
        # DB更新
        sql = 'UPDATE contents SET status = 3 WHERE cid = :cid'
        db.cursor.execute(sql, {'cid': cid})
        # 開始通知
        self.notify(f'Download started "{title}"')
        # ログ
        self.log(f'[{process.pid}] Download started.')
        # ダウンロード終了を待つ
        process.wait()
        # ダウンロード結果に応じて後処理
        if process.returncode == 0:
            # DB更新
            sql = 'UPDATE contents SET status = -1 WHERE cid = :cid'
            db.cursor.execute(sql, {'cid': cid})
            # ID3タグを書き込む
            db.write_id3(mp3file, cid)
            # 完了通知
            self.notify('Download completed "%s"' % title)
            # ログ
            self.log(f'[{process.pid}] Download completed.')
        else:
            # エラーメッセージ
            err = process.stderr.read().decode('utf-8')
            # DB更新
            sql = 'UPDATE contents SET status = -2, description = :err WHERE cid = :cid'
            db.cursor.execute(sql, {'cid': cid, 'err': err})
            # 完了通知
            self.notify('Download failed "%s"' % title, error=True)
            # ログ
            self.log(f'[{process.pid}] Download failed (returncode={process.returncode}).')
            self.log(err)
        # DBから切断
        db.conn.close()

    def update_rss(self):
        # RSS作成
        sql = 'SELECT kid, dirname FROM keywords WHERE status = -1'
        self.db.cursor.execute(sql)
        for kid, keyword, dirname in self.db.cursor.fetchall():
            self.db.create_rss(kid, keyword, dirname)
        # インデクス作成
        self.db.create_index()
        # 完了通知
        self.notify('RSS has been updated')

