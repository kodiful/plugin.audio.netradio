### Kodiアドオン：ネットラジオクライアント

![トップ画面](https://user-images.githubusercontent.com/12268536/233762697-6339fd83-a782-43e2-bb28-b47f844913a8.png)

[NHKラジオ](http://www.nhk.or.jp/radio/)、[民放ラジオ（radiko.jp）](http://radiko.jp)ほかが提供するインターネットラジオ放送局を聴いたり、番組をファイル保存できるKodiアドオンです。
Windows、macOSで動作検証しています。

以下を参考にしました。

* [http://xbmc.inpane.com/main/heavy_user/script_radiko.php](http://xbmc.inpane.com/main/heavy_user/script_radiko.php)

@xbmc_nowさん、ありがとうございます。

---
### 目次

[概要](#概要)

[トップ画面](#トップ画面)

[放送局設定画面](#放送局設定画面)

[キーワード設定画面](#キーワード設定画面)

[アドオン設定画面-一般](#アドオン設定画面-一般)

[アドオン設定画面-番組保存](#アドオン設定画面-番組保存)

[アドオン設定画面-その他](#アドオン設定画面-その他)

---
### 概要

#### 番組再生

Kodi単体で対応できない一部のコミュニティラジオをストリーム再生するために、アドオン内部に設けたプロキシ機能（ローカルプロキシ）を用いて必要な処理を行っています。

#### 番組表示

現在時刻の番組情報が自動的に取得され、画面が更新されます。
番組情報が定時から0分〜数分遅れて配信されているために、画面の更新も引きずられて遅れることがあります。

#### 番組保存

番組保存は、あらかじめ設定したキーワード情報と、NHKラジオおよび民放ラジオ（radiko.jp）について配信される番組情報に基づいて、番組を単位としてファイルに保存します。
開始／終了時間を指定した保存には対応してしません。

キーワード設定は、NHKラジオまたは民放ラジオ（radiko.jp）の放送局を右クリックして表示されるコンテクストメニューから「キーワードを追加する」を選択して設定します。
この場合は、選択した放送局の放送中の番組の情報が入力された状態で設定画面が立ち上がるので、文字入力の手間を省くことができます。
アドオン設定画面から「キーワードを追加する」を選択して設定することもできます。

#### RSSの生成

保存済み番組のファイル情報を記述したポッドキャスト形式のRSSを生成することができます。
RSSは番組が保存されるフォルダにrss.xmlとして生成されます。
RSSは番組保存の都度、自動的に更新されます。

番組が保存されるフォルダをHTTPでアクセスできるようにすることで、このRSSを介してポッドキャストクライアントとのファイル共有が容易になります。
ファイル共有は、Kodiと同じLANに接続された端末からのアクセスを想定しています。
番組保存したファイルを、不特定の端末からアクセスできる状態におくことは、著作権法に抵触する恐れがありますのでご注意ください。

#### 外部プログラムのインストール

番組保存や、一部のコミュニティラジオのストリーム再生のために _ffmpeg_ が必要です。
_ffmpeg_ は以下のページからダウンロードできます。

* [ffmpeg.org](https://ffmpeg.org)

_ffmpeg_ がインストールされていない場合や、 _ffmpeg_ のインストール後にそのパスがKodiアドオンで正しく認識できない場合は、Kodi起動時にエラーが通知されます。
OS側でパスの修正ができない場合は、[アドオン設定画面-その他](#アドオン設定画面-その他)で _ffmpeg_ のパスを設定してください。

---
### トップ画面

起動するとトップ画面が表示されます。
トップ画面は、放送局表示部、ディレクトリ表示部、キーワード表示部から構成されます。
初期状態はディレクトリ表示部のみで、これに対して放送局やキーワードを追加することで、放送局表示部、キーワード表示部を含むトップ画面が構成されます。

![トップ画面](https://user-images.githubusercontent.com/12268536/233762697-6339fd83-a782-43e2-bb28-b47f844913a8.png)

#### 放送局表示部

ディレクトリから選択した放送局や、[放送局設定画面](#放送局設定画面)で設定した放送局をこの部分に表示します。
放送局を選択して現在放送中の番組を聴くことができます。

#### ディレクトリ表示部

以下の三つのディレクトリに分類された放送局から選択して、ストリーム再生したり、トップ画面に追加できます。

* NHKラジオ
  
  radikoの認証で判定された地域にしたがって、「東京」「札幌」「仙台」「名古屋」「大阪」「広島」「松山」「福岡」のいずれかのNHKラジオ第1とNHK-FM、およびNHKラジオ第2（全国共通）が選択できます。

* 民放ラジオ（radiko.jp）
  
  radikoの認証で判定された地域にしたがって、その地域で受信可能な民放ラジオが選択できます。

* コミュニティラジオ
  
  以下のサイトに掲載されているコミュニティラジオ（一部を除く）を地域別に検索して選択できます。

  * [ListenRadio](http://listenradio.jp)
  
  * [コミュニティ・サイマルラジオ・アライアンス](https://csra.fm)
  
  * [エフエムプラプラ](https://fmplapla.com)
  
  * [一般社団法人日本コミュニティ放送協会](https://www.jcbasimul.com)

ディレクトリの配下にある各放送局を選択して現在放送中の番組をストリーム再生できます。

ディレクトリの配下にある各放送局を右クリックして表示されるコンテクストメニューから「トップ画面に追加する」を選択して、選択した放送局をトップ画面の放送局表示部に追加できます。

#### キーワード表示部

あらかじめ指定したキーワード情報に基づいて自動保存された番組をキーワードごとに表示します。
キーワードを選択してこのキーワードに基づいて自動保存された番組の一覧を表示します。

![保存番組一覧](https://user-images.githubusercontent.com/12268536/233771889-21c31b83-6d30-4d57-ad88-ab74a7e37ebd.png)

一覧から番組を選択して聴くことができます。

---
### 放送局設定画面

ディレクトリに配置された放送局と同様に、それ以外の放送局についても、局名と配信ストリームのURLを登録してトップ画面に追加できます。
[アドオン設定画面-一般](#アドオン設定画面-一般)から開くことができます。

![放送局設定画面](https://user-images.githubusercontent.com/12268536/233768184-05564b82-c68e-45a7-8bfd-f2d6ce911645.png)

#### 放送局名

画面に表示する放送局名を入力します。

#### ストリームURL

配信ストリームのURLを入力します。

#### 画像URL（オプション）

画面に表示するサムネイル画像のURLを入力します。
指定しない場合はデフォルト画像が用いられます。

#### サイトURL（オプション）

放送局の公式ホームページのURLを入力します。
RSS生成のための情報として使われます。

#### 説明（オプション）

任意の情報が入力できます。入力した情報は放送局名に続いて画面に表示されます。

---
### キーワード設定画面

番組保存のためのキーワードを設定します。
NHKラジオまたは民放ラジオ（radiko.jp）の放送局を右クリックして表示されるコンテクストメニューから「キーワードを追加する」を選択して開くことができます。
[アドオン設定画面-一般](#アドオン設定画面-一般)から開くこともできます。

![キーワード設定画面](https://user-images.githubusercontent.com/12268536/233762692-fa24cd8c-74b0-46e0-8402-0c9b709b776a.png)

#### キーワード

番組情報に含まれるキーワードを設定します。
ここで設定したキーワードを番組情報に含む番組が自動的に保存されます。

#### 検索対象

上記で設定したキーワードを照合する番組情報の範囲を設定します。
「番組名のみ」「番組名と詳細情報」のいずれかを選択してください。

#### 曜日

上記で設定したキーワードに加えて、番組が放送される曜日を指定できます。

#### 放送局を指定する

オンにした場合、上記で設定したキーワードに加えて、放送局を指定できます。

#### 指定する放送局のID

「放送局を指定する」がオンの場合に、保存の対象とする放送局をIDで指定します。

---
### アドオン設定画面-一般

![アドオン設定画面-一般](https://user-images.githubusercontent.com/12268536/233762691-24d39333-be79-48f5-9898-fa8e61373753.png)

#### 放送局を追加する

[放送局設定画面](#放送局設定画面)を開いてキーワードを設定します。

#### キーワードを追加する

[キーワード設定画面](#キーワード設定画面)を開いてキーワードを設定します。

---
### アドオン設定画面-番組保存

![アドオン設定画面-番組保存](https://user-images.githubusercontent.com/12268536/233762688-cbb80db9-3fba-4815-a98a-29523bce7b20.png)

#### 番組保存

番組保存する場合はオンにしてください。

#### ビットレート

mp3エンコード時のビットレートを指定してください。
ビットレートはauto/192k/160k/128k/96k/64kから選択できます。
autoを指定すると、mp3エンコード後のファイルサイズを100MB以下とする（できるだけ高い）ビットレートを自動選択します。
iOSのPodcastアプリでダウンロードできる最大サイズは100MBまでとされていますので、Podcastアプリと同期する場合はビットレートをautoとしてください。

#### 保存フォルダのパス

ファイルを保存するフォルダを指定してください。

#### RSS生成

RSSを生成する場合はオンにしてください。

#### 保存フォルダのURL

RSSは保存フォルダに _rss.xml_ として生成されます。
保存フォルダに対応するURLを設定してください。

図のように、保存フォルダのURLを _http\://127.0.0.1/NetRadio/_ とした場合、
RSSは _http\://127.0.0.1/NetRadio/rss.xml_ から取得できます。

保存フォルダのURLを指定しない場合は、RSSに記述されるファイル（コンテンツファイル、アイコン画像ファイル、スタイルシートファイル）のパスはRSSファイルからの相対パスとして出力されます。
ポッドキャストクライアントによっては絶対パスとして指定する必要があるので注意してください（macOS、iOSのPodcastアプリは絶対パスの指定が必要のようです）。

#### アイテム数

RSSに格納するファイル情報の数を指定してください。
ファイル情報の数は5/10/20/50/100/unlimitedから選択できます。
すべてのファイル情報を格納する場合はunlimitedを指定してください。

#### RSSを更新する

番組保存したファイル情報に基づいてRSSを更新します。
通常は番組保存の完了時に自動更新されます。

---
### アドオン設定画面-その他

![アドオン設定画面-その他](https://user-images.githubusercontent.com/12268536/233762691-24d39333-be79-48f5-9898-fa8e61373753.png)

#### ffmpegのパス

番組保存や、一部のコミュニティラジオのストリーム再生のために _ffmpeg_ が必要です。
[外部プログラムのインストール](#外部プログラムのインストール)にしたがってインストールしてください。

_ffmpeg_ をインストールした後、そのパスがKodiアドオンで正しく認識できない場合、Kodi起動時にエラーが通知されます。
OS側でパスの修正ができない場合は、ここに _ffmpeg_ のパスを設定してください。

#### ローカルプロキシのポート

アドオン内部に設けたプロキシ機能（ローカルプロキシ）により、放送局から各種情報を取得する際に必要な処理を行っています。
このローカルプロキシが使用するポート番号を設定します（デフォルトは8088）。

他のアプリケーションが同じポート番号を使用しているなどで、Kodi起動時にエラーが通知される場合は他の番号に変更してください。
ポート番号の変更後はKodiを再起動してください。

#### デバッグ

デバッグ用の設定です。 動作に関する情報をKodiのログファイルに書き出します。

