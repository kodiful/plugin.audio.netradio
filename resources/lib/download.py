# -*- coding: utf-8 -*-

import os
import shutil
import json
import ffmpeg
import glob
import locale
import datetime

from xml.sax.saxutils import escape

from resources.lib.common import Common
from resources.lib.directory import Directory


class Download(Directory, Common):

    def __init__(self):
        super().__init__()
      
    def _converted_stream(self, program):
        if program['type'] in ('nhk1', 'nhk2', 'nhk3'):
            type_ = 'nhkr'
        else:
            type_ = program['type']
        index = self.read_as_json(os.path.join(self.INDEX_PATH, '%s.json' % type_))
        station = list(filter(lambda x: x['name'] == program['name'], index))[0]
        return self._stream(station)

    def download(self, program, path, queue):
        # ストリームURL
        stream = self._converted_stream(program)
        # 時間
        duration = program['end'] - self.now()
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
        mp3path = os.path.join(self.DOWNLOAD_PATH, '%s.mp3' % os.path.basename(path))
        # ffmpeg実行
        kwargs = {'acodec': 'libmp3lame', 'b:a': bitrate, 'v': 'warning'}
        process = ffmpeg.input(stream, t=duration).output(mp3path, **kwargs).run_async()
        # プロセスをキューに追加
        queue.put(process)
        # 開始通知
        self.notify('Download started "%s"' % program['title'])
        # ログ
        self.log(f'[{p.pid}] Download started.')
        # ダウンロード終了を待つ
        p.wait()
        # ダウンロード結果に応じて後処理
        if p.returncode == 0:
            # pathとmp3pathをfolder配下へ移動する
            root = self.GET('folder')
            if os.path.isdir(root):
                folder = os.path.join(root, program['keyword'])
                os.makedirs(folder, exist_ok=True)
                shutil.move(path, folder)
                shutil.move(mp3path, folder)
                # rssファイル生成
                if self.GET('rss') == 'true':
                    # 全キーワードのrssファイル生成
                    RSS().create()
                    # 当該キーワードのrssファイル生成
                    RSS(program['keyword']).create()
            # 完了通知
            self.notify('Download completed "%s"' % program['title'])
            # ログ
            self.log(f'[{p.pid}] Download completed.')
        else:
            # 失敗したときはjsonファイルを削除
            os.remove(path)
            # 完了通知
            self.notify('Download failed "%s"' % program['title'], error=True)
            # ログ
            self.log(f'[{p.pid}] Download failed (returncode={p.returncode}).')

    def update_rss(self):
        # 全キーワードのrssファイル生成
        RSS().create()
        # キーワードごとのrssファイル生成
        for path in glob.glob(os.path.join(self.GET('folder'), '*')):
            if os.path.isdir(path):
                keyword = path.split('/')[-1]
                RSS(keyword).create()


class RSS(Common):

    def __init__(self, keyword=None):
        # RSSのルートパス
        self.rss_root = self.GET('rssurl')  # http://127.0.0.1/NetRadio
        self.dir_root = self.GET('folder')  # /Library/WebServer/Documents/www/NetRadio
        if keyword is None:
            self.rss_file = os.path.join(self.dir_root, 'rss.xml')
            contents = glob.glob(os.path.join(self.dir_root, '*', '*.mp3'))
        else:
            self.rss_root = '%s/%s/' % (self.rss_root, keyword) 
            self.dir_root = os.path.join(self.dir_root, keyword)
            self.rss_file = os.path.join(self.dir_root, 'rss.xml')
            contents = glob.glob(os.path.join(self.dir_root, '*.mp3'))
        # アイテム数
        limit = self.GET('rssnum') or 'unlimited'
        limit = None if limit == 'unlimited' else int(limit)
        # アイテムのリスト
        buf = []
        for path in contents:
            buf.append((self.read_as_json(path.replace('.mp3', '')), path))
        self.contents = sorted(buf, key=lambda x: x[0]['start'], reverse=True)[:limit]  # 開始時間の降順にソート
    
    def create(self):
        # 時刻表記のロケール設定                                                                                                                                                             
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # テンプレート
        header = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'header.xml'))
        body = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'body.xml'))
        footer = self.read(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'footer.xml'))
        #
        # RSS生成
        #
        buf = []
        # header
        buf.append(
            header.format(
                title='NetRadio Client',
                image='icon.png',
                root=self.rss_root))
        # body
        for p, path in self.contents:
            # title
            title = escape(p['title'])
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
            if p['subtitle']:
                description += '<p>%s</p>' % p['subtitle']
            if p['act']:
                description += '<p>%s</p>' % p['act']
            if p['info']:
                description += '<p>%s</p>' % p['info']
            if p['desc']:
                description += '<p>%s</p>' % p['desc']
            description = escape(description)
            # station
            station = escape(p['name'])
            # 各番組情報を書き込む
            buf.append(
                body.format(
                    title=title,
                    url='',
                    root=self.rss_root,
                    source=source,
                    date=date,
                    startdate=startdate,
                    name=station,
                    duration=duration,
                    filesize=filesize,
                    description=description))
        # footer
        buf.append(footer)
        # ファイル書き込み
        if os.path.exists(self.rss_file):
            os.remove(self.rss_file)
        with open(self.rss_file, 'wb') as f:
            f.write('\n'.join(buf).encode('utf-8'))
        #
        # 関係するファイルをダウンロードフォルダにコピーする
        #
        # アイコン画像
        icon = os.path.join(self.dir_root, 'icon.png')
        if os.path.isfile(icon):
            os.remove(icon)
        shutil.copy(os.path.join(self.PLUGIN_PATH, 'icon.png'), icon)
        # スタイルシート
        stylesheet = os.path.join(self.dir_root, 'stylesheet.xsl')
        if os.path.isfile(stylesheet):
            os.remove(stylesheet)
        shutil.copy(os.path.join(self.RESOURCES_PATH, 'data', 'rss', 'stylesheet.xsl'), stylesheet)