# -*- coding: utf-8 -*-

import sys
import os
import shutil
import ffmpeg
import glob
import locale
import datetime
import re

from xml.sax.saxutils import escape

from resources.lib.common import Common
from resources.lib.directory import Directory
from resources.lib.holiday import Holiday

import xbmcplugin
import xbmcgui


class Download(Directory, Common):

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        super().__init__()

    def show(self, path):
        # path直下の番組情報ファイルを開始時間の逆順にリスト化する
        for item in sorted(glob.glob(os.path.join(path, '*.json')), reverse=True):
            self._add_download(item)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

    def _add_download(self, item):
        data = self.read_as_json(item)
        li = xbmcgui.ListItem(self._title(data))
        logo = os.path.join(self.LOGO_PATH, data['type'], '%s.png' % data['station'])
        li.setArt({'thumb': logo, 'icon': logo})
        li.setInfo(type='music', infoLabels={'title': data['title']})
        li.setProperty('IsPlayable', 'true')
        # コンテクストメニュー
        self.contextmenu = []
        self._contextmenu(self.STR(30109), {'action': 'open_folder', 'keyword': data['keyword']})
        self._contextmenu(self.STR(30100), {'action': 'settings'})
        li.addContextMenuItems(self.contextmenu, replaceItems=True)
        # 再生するファイルのパス
        stream = os.path.join(os.path.dirname(item), os.path.basename(item).replace('.json', '.mp3'))
        # リストアイテムを追加
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), stream, listitem=li, isFolder=False)

    def _title(self, data):
        # %Y年%m月%d日(%%s) %H:%M
        format = self.STR(30919)
        # 月,火,水,木,金,土,日
        weekdays = self.STR(30920)
        weekdays = weekdays.split(',')
        # 放送開始時刻
        d = datetime.datetime.strptime(data['START'], '%Y%m%d%H%M%S')
        w = d.weekday()
        # 放送終了時刻
        end = '%s:%s' % (data['END'][8:10], data['END'][10:12])
        # 8月31日(土)
        format = d.strftime(format)
        date1 = format % weekdays[w]
        # 2019-08-31
        date2 = d.strftime('%Y-%m-%d')
        # カラー
        if date2 in Holiday.HOLIDAYS or w == 6:
            title = '[COLOR red]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, data['title'])
        elif w == 5:
            title = '[COLOR blue]%s-%s[/COLOR]  [COLOR khaki]%s[/COLOR]' % (date1, end, data['title'])
        else:
            title = '%s-%s  [COLOR khaki]%s[/COLOR]' % (date1, end, data['title'])
        return title
    
    def _station(self, program):
        index = self.read_as_json(os.path.join(self.INDEX_PATH, '%s.json' % program['type']))
        #station = list(filter(lambda x: x['id'] == program['id'] and x['station'] == program['station'], index))[0]
        station = list(filter(lambda x: x['id'] == program['id'] and (x['id'][:3] != 'NHK' or x['station'] == program['station']), index))[0]
        return station

    def download(self, program, end, path, queue):
        # 放送局データ
        station = self._station(program)
        # ストリームURL
        stream = self._stream(station, download=True)
        # 時間
        duration = end - self.now()
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
        # 出力ファイル
        mp3path = os.path.join(self.DOWNLOAD_PATH, os.path.basename(path).replace('.json', '.mp3'))
        # ffmpeg実行
        kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
        process = ffmpeg.input(stream, t=duration).output(mp3path, **kwargs).run_async()
        # プロセスをキューに追加
        queue.put(process)
        # 開始通知
        self.notify('Download started "%s"' % program['title'])
        # ログ
        self.log(f'[{process.pid}] Download started.')
        # ダウンロード終了を待つ
        process.wait()
        # ダウンロード結果に応じて後処理
        if process.returncode == 0:
            # pathとmp3pathをfolder配下へ移動する
            root = self.GET('folder')
            if os.path.isdir(root):
                folder = os.path.join(root, program['keyword'])
                os.makedirs(folder, exist_ok=True)
                shutil.move(path, folder)
                shutil.move(mp3path, folder)
                # rssファイル生成
                if self.GET('rss') == 'true':
                    # 当該キーワードのrssファイル生成
                    RSS().create(program['keyword'])
            # 完了通知
            self.notify('Download completed "%s"' % program['title'])
            # ログ
            self.log(f'[{process.pid}] Download completed.')
        else:
            # 失敗したときはjsonファイルを削除
            os.remove(path)
            # 完了通知
            self.notify('Download failed "%s"' % program['title'], error=True)
            # ログ
            self.log(f'[{process.pid}] Download failed (returncode={process.returncode}).')

    def update_rss(self):
        dir_root = self.GET('folder')
        paths = list(filter(os.path.isdir, glob.glob(os.path.join(dir_root, '*'))))
        # キーワードのリスト
        keywords = list(map(lambda x: x.split('/')[-1], paths))
        # RSS作成
        for keyword in keywords:
            RSS().create(keyword)
        # インデクス作成
        RSS().create_index()
        # 官僚通知
        self.notify('RSS has been updated')


class RSS(Common):

    def __init__(self):
        # 時刻表記のロケール設定                                                                                                                                                             
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # テンプレート
        self.header = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'header.xml'))
        self.body = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'body.xml'))
        self.footer = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'footer.xml'))

    def create(self, keyword):
        rss_root = self.GET('rssurl')
        dir_root = self.GET('folder')
        paths = glob.glob(os.path.join(dir_root, keyword, '*.json'))
        # アイテム数
        limit = self.GET('rssnum') or 'unlimited'
        limit = None if limit == 'unlimited' else int(limit)
        # アイテムのリスト
        contents = list(map(lambda x: (self.read_as_json(x), x.replace('.json', '.mp3')), paths))
        contents = sorted(contents, key=lambda x: (int(x[0]['START'][:8]), -int(x[0]['START'][8:])), reverse=True)[:limit]  # 開始日の降順、同じ日の中では昇順にソート
        # RSS生成
        buf = []
        # header
        buf.append(
            self.header.format(
                title='%s | NetRadio Client' % keyword,
                image='icon.png',
                root=rss_root))
        # body
        for p, path in contents:
            # title
            title = escape(p['title'])
            # url
            url = p['url']
            # source
            source = '%s/%s' % (escape(p['keyword']), escape(os.path.basename(path)))
            # date
            date = datetime.datetime.strptime(p['START'], '%Y%m%d%H%M%S').strftime('%Y-%m-%d')
            # startdate
            startdate = datetime.datetime.strptime(p['START'], '%Y%m%d%H%M%S').strftime('%a, %d %b %Y %H:%M:%S +0900')
            # duration
            duration = p['end'] - p['start']
            duration = '%02d:%02d:%02d' % (duration // 3600, duration // 60 % 60, duration % 60)
            # filesize
            filesize = os.path.getsize(path)
            # description
            description = ''
            if p['act']:
                description += '<p class="act">%s</p>' % p['act']
            if p['desc']:
                description += '<p class="desc">%s</p>' % p['desc']
            if p['info']:
                description += '<p class="info">%s</p>' % p['info']
            description = re.sub(r'(<br>| )+', ' ', description)
            description = escape(description)
            # statio
            station = escape(p['station'])
            # 各番組情報を書き込む
            buf.append(
                self.body.format(
                    title=title,
                    url=url,
                    root=rss_root,
                    source=source,
                    date=date,
                    startdate=startdate,
                    station=station,
                    duration=duration,
                    filesize=filesize,
                    description=description
                )
            )
        # footer
        buf.append(self.footer)
        # ファイル書き込み
        rss_file = os.path.join(dir_root, keyword, 'rss.xml')
        if os.path.exists(rss_file):
            os.remove(rss_file)
        with open(rss_file, 'wb') as f:
            f.write('\n'.join(buf).encode('utf-8'))

    def create_index(self):
        rss_root = self.GET('rssurl')
        dir_root = self.GET('folder')
        paths = list(filter(os.path.isdir, glob.glob(os.path.join(dir_root, '*'))))
        # キーワードのリスト
        keywords = list(map(lambda x: x.split('/')[-1], paths))
        # RSS生成
        buf = []
        # header
        buf.append(
            self.header.format(
                title='NetRadio Client',
                image='icon.png',
                root=rss_root))
        # body
        for keyword in sorted(keywords):
            buf.append(
                self.body.format(
                    title=keyword,
                    url='%s/%s/rss.xml' % (rss_root, keyword),
                    root='',
                    source='',
                    date='',
                    startdate='',
                    station='',
                    duration='',
                    filesize='',
                    description=''
                )
            )
        # footer
        buf.append(self.footer)
        # ファイル書き込み
        index_file = os.path.join(dir_root, 'index.xml')
        if os.path.exists(index_file):
            os.remove(index_file)
        with open(index_file, 'wb') as f:
            f.write('\n'.join(buf).encode('utf-8'))
        # アイコン画像をダウンロードフォルダにコピーする
        icon = os.path.join(dir_root, 'icon.png')
        if os.path.isfile(icon):
            os.remove(icon)
        shutil.copy(os.path.join(self.PLUGIN_PATH, 'icon.png'), icon)
        # スタイルシートをダウンロードフォルダにコピーする
        stylesheet = os.path.join(dir_root, 'stylesheet.xsl')
        if os.path.isfile(stylesheet):
            os.remove(stylesheet)
        shutil.copy(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'stylesheet.xsl'), stylesheet)
