# Kodiアドオン：ネットラジオクライアント

![トップ画面](https://github.com/user-attachments/assets/73955277-28b1-4878-9833-d13b91c83ab4)

[NHKラジオ](http://www.nhk.or.jp/radio/)、[民放ラジオ（radiko.jp）](http://radiko.jp)、[コミュニティラジオ](#コミュニティラジオ放送局一覧)が提供するインターネットラジオ放送を聴いたり、番組をファイル保存できるKodiアドオンです。
Windows、macOSで動作検証しています。


## 目次

[概要](#概要)

[トップ画面](#トップ画面)

[コンテクストメニューからの保存設定](#コンテクストメニューからの保存設定)

[放送局設定画面](#放送局設定画面)

[タイマー設定画面](#タイマー設定画面)

[キーワード設定画面](#キーワード設定画面)

[アドオン設定画面-一般](#アドオン設定画面-一般)

[アドオン設定画面-番組保存](#アドオン設定画面-番組保存)

[アドオン設定画面-その他](#アドオン設定画面-その他)

[コミュニティラジオ放送局一覧](#コミュニティラジオ放送局一覧)


## 概要

### 番組再生

Kodi単体ではストリーム再生できない一部のコミュニティラジオに対応するために、アドオン内部に設けたプロキシ機能（ローカルプロキシ）を用いて必要な処理を行っています。

### 番組表示

NHKラジオ、民放ラジオ（radiko.jp）、および番組情報が配信されているコミュニティラジオについては、現在時刻の番組情報が自動的に取得され、画面が更新されます。
番組情報が定時から数十秒〜数分遅れて配信されているために、画面の更新も引きずられて遅れることがあります。

### 番組保存

以下の3通りの番組保存設定ができます。
* （番組設定）放送中の番組の番組情報に基づいて、番組を単位としてファイルに保存
* （タイマー設定）開始／終了時刻を指定してファイルに保存
* （キーワード設定）あらかじめ設定したキーワード情報と、配信される番組情報に基づいて、番組を単位としてファイルに保存

番組設定とキーワード設定は、NHKラジオ、民放ラジオ（radiko.jp）および番組情報が配信されているコミュニティラジオを対象に設定できます。
番組情報が配信されていないコミュニティラジオは、タイマー設定のみ対応しています。

番組保存は、放送局を右クリックして表示されるコンテクストメニューから「保存設定」を選択して設定します。
タイマー設定、キーワード設定は、「保存設定」を選択して表示されるダイアログで、さらに「詳細設定」を選択して設定します。

タイマー設定、キーワード設定は、アドオン設定画面から「タイマー設定を追加する」「キーワード設定を追加する」を選択して設定することもできます。

番組設定は、放送中の番組の保存が少ない手間で簡単にできます。
タイマー設定、キーワード設定は、選択した放送局の放送中の番組の情報が入力された状態で設定画面が立ち上がるので、文字入力や時刻入力の手間を省くことができます。

キーワード設定は、番組名や番組情報に含まれるキーワード、放送局、放送曜日を設定できます。帯番組の保存などに便利です。


### RSSの生成

保存済み番組のファイル情報を記述したポッドキャスト形式のRSSを生成できます。
RSSは番組が保存されるフォルダにrss.xmlとして生成されます。
RSSは番組保存の都度、自動的に更新されます。

番組が保存されるフォルダをHTTPでアクセスできるようにすることで、このRSSを介してポッドキャストクライアントとのファイル共有が容易になります。
ファイル共有は、Kodiと同じLANに接続された端末からのアクセスを想定しています。
番組保存したファイルを、不特定の端末からアクセスできる状態におくことは、著作権法に抵触する恐れがありますのでご注意ください。

### 外部プログラムのインストール

番組保存や、一部のコミュニティラジオのストリーム再生のために _ffmpeg_ が必要です。
_ffmpeg_ は[ffmpeg.org](https://ffmpeg.org)からダウンロードできます。

_ffmpeg_ がインストールされていない場合や、 _ffmpeg_ のインストール後にそのパスがKodiアドオンで正しく認識できない場合は、Kodi起動時にエラーが通知されます。
OS側でパスの修正ができない場合は、[アドオン設定画面-その他](#アドオン設定画面-その他)で _ffmpeg_ のパスを設定してください。


## トップ画面

起動するとトップ画面が表示されます。
トップ画面は、放送局表示部、ディレクトリ表示部、アーカイブ表示部から構成されます。
初期状態は、地域で受信可能なNHKラジオおよび民放ラジオ（radiko.jp）がリストアップされた放送局表示部、およびディレクトリ表示部が表示されます。アーカイブ表示部は保存設定を追加することで表示されます。

![トップ画面](https://github.com/user-attachments/assets/73955277-28b1-4878-9833-d13b91c83ab4)

### 放送局表示部

ディレクトリから選択した放送局や、[放送局設定画面](#放送局設定画面)で設定した放送局をこの部分に表示します。
放送局を選択して現在放送中の番組を聴くことができます。

### ディレクトリ表示部

以下の三つのディレクトリに分類された放送局から選択して、ストリーム再生したり、トップ画面に追加できます。

* NHKラジオ
  
  radikoの認証で判定された地域にしたがって、「東京」「札幌」「仙台」「名古屋」「大阪」「広島」「松山」「福岡」のいずれかのNHKラジオ第1とNHK-FM、およびNHKラジオ第2（全国共通）が選択できます。

  ![保存番組一覧](https://github.com/user-attachments/assets/158e90a1-2a68-4356-aea0-ce12b2255c7d)

* 民放ラジオ（radiko.jp）
  
  radikoの認証で判定された地域にしたがって、受信可能な民放ラジオが選択できます。

  ![保存番組一覧](https://github.com/user-attachments/assets/29f7d637-6535-466a-aa06-abd32ccbc753)

* コミュニティラジオ
  
  あらかじめ設定されているコミュニティラジオ（[コミュニティラジオ放送局一覧](#コミュニティラジオ放送局一覧)）を、地域ごとに検索して選択できます。
  
  ![保存番組一覧](https://github.com/user-attachments/assets/17918eb8-0797-47d5-8919-7736d881c950)

  ![保存番組一覧](https://github.com/user-attachments/assets/6747a4f6-df98-41e1-817f-90372dcff824)

  ![保存番組一覧](https://github.com/user-attachments/assets/ec8bd092-ca37-4040-aa0e-601ca8fcba38)

ディレクトリの配下にある各放送局を選択して現在放送中の番組をストリーム再生できます。
ディレクトリの配下にある各放送局を右クリックして表示されるコンテクストメニューから「トップ画面に追加する」を選択して、選択した放送局をトップ画面の放送局表示部に追加できます。

### アーカイブ表示部

以下の三つのディレクトリに分類された放送局から選択して、ストリーム再生したり、トップ画面に追加できます。

* キーワード別
  
  あらかじめ指定したキーワード情報に基づいて自動保存された番組をキーワードごとに表示します。
  RSS生成をオンにすると、キーワードに対応するRSSのURLを埋め込んだQRコードがアイコン/サムネイルとして表示されます。
  キーワードを選択してこのキーワードに基づいて自動保存された番組の一覧を表示、一覧から番組を選択して再生します。

* 放送局別

  保存された番組を放送局別に表示します。
  放送局を選択してこの放送局から配信された保存番組の一覧を表示、一覧から番組を選択して再生します。

* 日付別

  保存された番組を日付別に表示します。
  日付を選択してこの日付に配信された保存番組の一覧を表示、一覧から番組を選択して再生します。


## コンテクストメニューからの保存設定

![番組保存画面](https://github.com/user-attachments/assets/cc385704-d9db-4420-b4d8-1d94e0b12a26)
![番組選択画面](https://github.com/user-attachments/assets/c182450e-827a-4121-92a1-686a95a9c461)
![番組設定画面](https://github.com/user-attachments/assets/c83c0529-e12e-467d-96ed-302ef16ca511)
![タイマー設定画面](https://github.com/user-attachments/assets/4d8f2808-ed94-4627-b45d-18ff2ed9ed3b)
![キーワード設定画面](https://github.com/user-attachments/assets/9872b295-bdcc-41d8-8b76-3f46ec37695e)


## 放送局設定画面

ディレクトリに配置された放送局と同様に、それ以外の放送局についても、局名と配信ストリームのURLを登録してトップ画面に追加できます。

[アドオン設定画面-一般](#アドオン設定画面-一般)から開くことができます。

![放送局設定画面](https://github.com/user-attachments/assets/0b6e4649-8120-41d2-8e3d-6f2bb5044f1a)

### 放送局名

画面に表示する放送局名を入力します。

### ストリームURL

配信ストリームのURLを入力します。

### 画像URL（オプション）

画面に表示するアイコン/サムネイル画像のURLを入力します。
指定しない場合はデフォルト画像が用いられます。

### サイトURL（オプション）

放送局の公式ホームページのURLを入力します。
RSS生成のための情報として使われます。

### 説明（オプション）

任意の情報が入力できます。入力した情報は放送局名に続いて画面に表示されます。

## タイマー設定画面

![タイマー設定画面](https://github.com/user-attachments/assets/f2c8ea62-c4e9-4bce-9ccb-0ac90c4c4adf)


## キーワード設定画面

番組保存のためのキーワードを設定します。

NHKラジオまたは民放ラジオ（radiko.jp）の放送局を右クリックして表示されるコンテクストメニューから「キーワードを追加する」を選択して開くことができます。
[アドオン設定画面-一般](#アドオン設定画面-一般)からも開くことができます。

![キーワード設定画面](https://github.com/user-attachments/assets/b537f73c-db77-49fc-8409-f6d9c801d804)

### キーワード

番組情報に含まれるキーワードを設定します。
ここで設定したキーワードを番組情報に含む番組が自動的に保存されます。

### 検索対象

上記で設定したキーワードを照合する番組情報の範囲を設定します。
「番組名のみ」「番組名と詳細情報」のいずれかを選択してください。

### 曜日

上記で設定したキーワードに加えて、番組が放送される曜日を指定できます。

### 放送局を指定する

オンにした場合、上記で設定したキーワードに加えて、放送局を指定できます。

### 指定する放送局のID

「放送局を指定する」がオンの場合に、保存の対象とする放送局をIDで指定します。


## アドオン設定画面-一般

![アドオン設定画面-一般](https://github.com/user-attachments/assets/f1957ab6-d74d-4e05-b157-0e8b8bb1392b)

### 放送局を追加する

[放送局設定画面](#放送局設定画面)を開いてキーワードを設定します。

### キーワードを追加する

[キーワード設定画面](#キーワード設定画面)を開いてキーワードを設定します。


## アドオン設定画面-番組保存

![アドオン設定画面-番組保存](https://github.com/user-attachments/assets/f7337dbe-d57a-427d-b7f6-8007aa226f9b)

### 番組保存

番組保存する場合はオンにしてください。

### ビットレート

mp3エンコード時のビットレートを指定してください。
ビットレートはauto/192k/160k/128k/96k/64kから選択できます。
autoを指定すると、mp3エンコード後のファイルサイズを100MB以下とする（できるだけ高い）ビットレートを自動選択します。
iOSのPodcastアプリでダウンロードできる最大サイズは100MBまでとされていますので、Podcastアプリと同期する場合はビットレートをautoとしてください。

### 保存フォルダのパス

ファイルを保存するフォルダを指定してください。

### RSS生成

RSSを生成する場合はオンにしてください。

### 保存フォルダのURL

RSSは保存フォルダに _rss.xml_ として生成されます。
保存フォルダに対応するURLを設定してください。

図のように、保存フォルダのURLを _http\://127.0.0.1/NetRadio/_ とした場合、
RSSは _http\://127.0.0.1/NetRadio/(キーワード)/rss.xml_ から取得できます。
キーワード一覧は、RSS形式で _http\://127.0.0.1/NetRadio/index.xml_ から取得できます。

保存フォルダのURLを指定しない場合は、RSSに記述されるファイル（コンテンツファイル、アイコン/サムネイル画像ファイル、スタイルシートファイル）のパスはRSSファイルからの相対パスとして出力されます。
ポッドキャストクライアントによっては絶対パスとして指定する必要があるので注意してください（macOS、iOSのPodcastアプリは絶対パスの指定が必要のようです）。

### アイテム数

RSSに格納するファイル情報の数を指定してください。
ファイル情報の数は5/10/20/50/100/unlimitedから選択できます。
すべてのファイル情報を格納する場合はunlimitedを指定してください。

### RSSを更新する

番組保存したファイル情報に基づいてRSSを更新します。
通常は番組保存の完了時に自動更新されます。


## アドオン設定画面-その他

![アドオン設定画面-その他](https://github.com/user-attachments/assets/43795a43-c602-4530-85ef-f078a9df3c04)

### ffmpegのパス

番組保存や、一部のコミュニティラジオのストリーム再生のために _ffmpeg_ が必要です。
[外部プログラムのインストール](#外部プログラムのインストール)にしたがってインストールしてください。

_ffmpeg_ をインストールした後、そのパスがKodiアドオンで正しく認識できない場合、Kodi起動時にエラーが通知されます。
OS側でパスの修正ができない場合は、ここに _ffmpeg_ のパスを設定してください。

### ポート番号

アドオン内部に設けたプロキシ機能（ローカルプロキシ）により、放送局から各種情報を取得する際に必要な処理を行っています。
このローカルプロキシが使用するポート番号を設定します（デフォルトは8088）。

他のアプリケーションが同じポート番号を使用しているなどで、Kodi起動時にエラーが通知される場合は他の番号に変更してください。
ポート番号の変更後はKodiを再起動してください。

### デバッグ

デバッグ用の設定です。 動作に関する情報をKodiのログファイルに書き出します。


## コミュニティラジオ放送局一覧

以下のサイトに掲載されているコミュニティラジオ（独自方式配信の一部を除く）があらかじめ設定されています。

* [ListenRadio（LR）](http://listenradio.jp)
* [一般社団法人日本コミュニティ放送協会（JCBA）](https://www.jcbasimul.com)
* [エフエムプラプラ（FM++）](https://fmplapla.com)
* [コミュニティ・サイマルラジオ・アライアンス（CSRA）](https://csra.fm)

複数のサイトに掲載されている場合は、下表で最も左側のサイトに掲載されている情報に基づいてストリーミング再生します。

|都道府県（市区町村）|放送局|LR|JCBA|FM++|CSRA|その他|
|:---|:---|:---|:---|:---|:---|:---|
|北海道(札幌市中央区)|[ラジオカロスサッポロ](https://radiokaros.com/)|○|-|-|○|-|
|北海道(札幌市東区)|[さっぽろ村ラジオ](https://www.fm813.jp/)|○|-|-|-|-|
|北海道(札幌市白石区)|[エフエムしろいし](https://www.830.fm/)|-|-|-|-|○|
|北海道(札幌市豊平区)|[FMアップル](http://765fm.com/)|○|-|-|-|-|
|北海道(札幌市西区)|[三角山放送局](https://www.sankakuyama.co.jp/)|○|-|-|-|-|
|北海道(札幌市厚別区)|[RADIOワンダーストレージ FMドラマシティ](https://776.fm/)|○|-|-|-|-|
|北海道(函館市)|[FMいるか](https://www.fmiruka.co.jp/)|-|○|-|-|-|
|北海道(小樽市)|[FMおたる](https://fmotaru.jp/)|○|-|-|○|-|
|北海道(旭川市)|[FMりべーる](https://fm837.com/)|○|-|-|○|-|
|北海道(室蘭市)|[FMびゅー](https://fmview.jp/)|-|○|-|-|-|
|北海道(釧路市)|[FMくしろ](https://www.fm946.com/)|○|-|-|○|-|
|北海道(帯広市)|[FM WING](https://fmwing.com/)|○|-|-|○|-|
|北海道(帯広市)|[JAGA](https://www.jaga.fm/)|○|-|-|-|-|
|北海道(岩見沢市)|[FMはまなす](https://fm761.jp/)|○|-|-|-|-|
|北海道(網走市)|[FMあばしり](https://www.lia-abashiri.com/)|○|-|-|-|-|
|北海道(留萌市)|[エフエムもえる](https://www.moeru.co.jp/)|-|○|-|-|-|
|北海道(苫小牧市)|[FMとまこまい](https://837.jp/)|-|○|-|-|-|
|北海道(稚内市)|[FMわっぴ～](http://www.wappy761.jp/)|-|-|-|○|-|
|北海道(名寄市)|[AIRてっし](http://www.nayoro.fm/)|-|○|-|-|-|
|北海道(根室市)|[FMねむろ](https://www.fmnemuro.com/)|○|-|-|-|-|
|北海道(恵庭市)|[e-niwa](http://www.e-niwa.tv/)|-|-|-|○|-|
|北海道(伊達市)|[wi-radio](https://date-kanko.jp/wi_radio/)|○|-|-|-|-|
|北海道(北広島市)|[FMメイプル](https://fm-maple.com/)|○|-|-|-|-|
|北海道(ニセコ町)|[ラジオニセコ](https://radioniseko.jp/)|-|○|-|○|-|
|北海道(栗山町)|[エフエムくりやま](https://fm-kuriyama.com/)|-|○|-|-|-|
|北海道(中標津町)|[FMはな](https://fmhana.jp/)|-|○|-|-|-|
|青森県(弘前市)|[FMアップルウェーブ](https://applewave.co.jp/)|-|○|-|-|-|
|青森県(八戸市)|[BeFM](https://www.befm.co.jp/)|○|-|-|○|-|
|青森県(五所川原市)|[ジーラジ FMごしょがわら](https://fm767.jp/)|-|○|-|-|-|
|青森県(むつ市)|[FM AZUR](https://www.fmazur.jp/)|-|○|-|-|-|
|岩手県(盛岡市)|[ラヂオもりおか](https://radiomorioka.co.jp/)|○|-|-|-|-|
|岩手県(宮古市)|[みやこハーバーラジオ](http://miyakofm.com/)|○|-|-|○|-|
|岩手県(大船渡市)|[FMねまらいん](https://fm-nemaline.com/)|-|-|○|-|-|
|岩手県(花巻市)|[FM One](https://fm-one.net/)|-|○|-|-|-|
|岩手県(北上市)|[きたかみE&Beエフエム](https://fm888.jp/)|-|-|○|-|-|
|岩手県(一関市)|[FMあすも](https://fm-asmo.com/)|-|-|○|-|-|
|岩手県(二戸市)|[カシオペアFM](http://779.jp/)|○|-|-|-|-|
|宮城県(仙台市青葉区)|[ラジオ3](https://www.radio3.jp/)|○|-|-|-|-|
|宮城県(仙台市宮城野区)|[Rakuten.FM TOHOKU](https://www.rakuteneagles.jp/radio/)|-|-|-|-|○|
|宮城県(仙台市太白区)|[エフエムたいはく](https://www.fm-t.net/)|-|-|-|○|-|
|宮城県(仙台市泉区)|[fmいずみ](https://www.fm797.co.jp/)|○|-|-|-|-|
|宮城県(石巻市)|[ラジオ石巻](http://www.fm764.jp/)|○|-|-|○|-|
|宮城県(塩竈市)|[BAY WAVE](https://www.bay-wave.co.jp/)|○|-|-|-|-|
|宮城県(気仙沼市)|[ぎょっとエフエム](https://kfm775.co.jp/)|○|-|-|-|-|
|宮城県(名取市)|[なとらじ801](https://www.natori801.jp/)|○|-|-|○|-|
|宮城県(岩沼市)|[エフエムいわぬま](https://www.fm779.net/)|-|○|-|-|-|
|宮城県(登米市)|[H@!FM](https://hat-fm.net/)|-|○|-|-|-|
|宮城県(大崎市)|[OCR FM 83.5](https://oosaki-fm.or.jp/)|-|-|○|-|-|
|秋田県(秋田市)|[エフエム椿台](https://www.fm796.com/)|○|-|-|-|-|
|秋田県(横手市)|[横手かまくらFM](https://fmyokote.com/)|○|-|-|○|-|
|秋田県(大館市)|[ラジオおおだて](https://odate-fm.com/)|-|-|○|-|-|
|秋田県(湯沢市)|[エフエムゆーとぴあ](http://www.yutopia.or.jp/~fm763/)|○|-|-|○|-|
|秋田県(鹿角市)|[鹿角きりたんぽFM](https://fm791.net/)|○|-|-|○|-|
|秋田県(大仙市)|[FMはなび](http://fmhanabi.com/)|-|-|○|-|-|
|山形県(山形市)|[ラジオモンスター](http://www.fm762.co.jp/)|-|○|-|-|-|
|山形県(米沢市)|[エフエムNCV おきたまGO!](https://fm834.jp/)|-|○|-|-|-|
|山形県(酒田市)|[ハーバーラジオ](https://www.sakatafm.com/)|-|○|-|-|-|
|山形県(長井市)|[エフエムい～じゃん おらんだラジオ](https://oranda-radio.jp/)|-|○|-|-|-|
|福島県(福島市)|[FMポコ](https://fm-poco.co.jp/)|-|○|-|-|-|
|福島県(会津若松市)|[FM愛’S](http://www.fmaizu.com/)|-|○|-|-|-|
|福島県(郡山市)|[ココラジ](https://www.fm791.co.jp/)|○|-|-|○|-|
|福島県(いわき市)|[FMいわき](https://www.fm-iwaki.co.jp/)|○|-|-|○|-|
|福島県(須賀川市)|[ULTRA FM](http://ultrafm868.jp/)|-|○|-|-|-|
|福島県(喜多方市)|[FMきたかた](http://www.fm-kitakata.co.jp/)|-|○|-|-|-|
|福島県(本宮市)|[FMモットコム](http://www.fm-mot.com/)|○|-|-|○|-|
|茨城県(水戸市)|[FMぱるるん](https://www.fmpalulun.co.jp/)|○|-|-|○|-|
|茨城県(日立市)|[FMひたち](https://www.fmhitachi.jp/)|○|-|-|○|-|
|茨城県(高萩市)|[たかはぎFM](https://t768.net/)|○|-|-|○|-|
|茨城県(牛久市)|[FMうしくうれしく放送](http://fmuu.jp/)|○|-|-|○|-|
|茨城県(つくば市)|[ラヂオつくば](https://radio-tsukuba.net/)|-|-|-|○|-|
|茨城県(鹿嶋市)|[FMかしま](http://www.767fm.com/)|-|○|-|-|-|
|茨城県(大子町)|[FMだいご](https://www.fmdaigo775.jp/)|-|○|-|-|-|
|栃木県(宇都宮市)|[ミヤラジ](https://www.miyaradi.com/)|-|-|○|-|-|
|栃木県(足利市)|[FM DAMONO](https://www.damono.jp/)|-|-|○|-|-|
|栃木県(栃木市)|[FMくらら857](https://www.fmkulala857.jp/)|-|-|○|-|-|
|栃木県(小山市)|[おーラジ](https://www.o-radi775.jp/)|-|-|○|-|-|
|栃木県(真岡市)|[FMもおか](https://www.fm-moka874.co.jp/)|-|-|○|-|-|
|栃木県(下野市)|[FMゆうがお](https://fmyugao879.jp/)|-|-|○|-|-|
|群馬県(前橋市)|[M-wave](https://maebashi.fm/)|○|-|-|-|-|
|群馬県(高崎市)|[ラジオ高崎](http://www.takasaki.fm/)|-|○|-|-|-|
|群馬県(桐生市)|[FM桐生](https://www.fmkiryu.jp/)|-|-|○|-|-|
|群馬県(太田市)|[エフエム太郎](https://www.fmtaro.co.jp/)|-|○|-|-|-|
|群馬県(沼田市)|[FM OZE](https://www.fm-oze.co.jp/)|-|○|-|-|-|
|群馬県(玉村町)|[ラヂオななみ](https://www.fm773.co.jp/)|-|○|-|-|-|
|埼玉県(さいたま市浦和区)|[REDS WAVE](http://redswave.com/)|○|-|-|○|-|
|埼玉県(川越市)|[ラジオ川越](https://radiokawagoe.com/)|-|○|-|-|-|
|埼玉県(熊谷市)|[FMクマガヤ](https://fmkumagaya.com/)|-|-|○|-|-|
|埼玉県(川口市)|[FM Kawaguchi](https://www.fm856.co.jp/)|○|-|-|○|-|
|埼玉県(秩父市)|[ちちぶエフエム](https://chichibufm.com/)|-|-|○|-|-|
|埼玉県(加須市)|[FMわたらせ](https://fm-watarase.com/)|○|-|-|-|-|
|埼玉県(本庄市)|[ほんじょうFM](https://honjofm.jp/)|-|-|○|-|-|
|埼玉県(鴻巣市)|[フラワーラジオ](https://fm767.com/)|○|-|-|○|-|
|埼玉県(深谷市)|[FMふっかちゃん](https://www.fukaya-fm.com/)|○|-|-|-|-|
|埼玉県(越谷市)|[こしがやエフエム](https://koshigayafm.co.jp/)|○|-|-|-|-|
|埼玉県(入間市)|[FMチャッピー](https://fmchappy.jp/)|-|○|-|-|-|
|埼玉県(朝霞市)|[775ライブリーFM](https://775fm.co.jp/)|○|-|-|○|-|
|埼玉県(三芳町)|[発するFM](https://fm840.com/)|-|○|-|-|-|
|千葉県(千葉市)|[SKYWAVE FM](https://www.892fm.com/)|-|○|-|-|-|
|千葉県(市川市)|[市川うららFM](http://www.fmu.co.jp/)|-|○|-|-|-|
|千葉県(木更津市)|[かずさエフエム](https://www.kazusafm.net/)|-|○|-|-|-|
|千葉県(成田市)|[ラジオ成田](https://www.narita.fm/)|-|○|-|-|-|
|千葉県(柏市)|[かしみんFM](https://kashimin.tacomin.com)|○|-|-|-|-|
|千葉県(八千代市)|[FMふくろう](https://296.fm/)|-|○|-|-|-|
|千葉県(多古町)|[たこみんFM](https://tacomin.com)|○|-|-|-|-|
|東京都()|[関東臨時災害放送局訓練](https://www.soumu.go.jp/soutsu/kanto/bc/rinsai/index.html)|-|○|-|-|-|
|東京都(中央区)|[ラジオシティ](http://fm840.jp/)|-|○|-|-|-|
|東京都(江東区)|[レインボータウンFM](https://885fm.jp/)|○|-|-|○|-|
|東京都(品川区)|[FMしながわ](https://fm-shinagawa.co.jp/)|-|○|-|-|-|
|東京都(世田谷区)|[エフエム世田谷](https://fmsetagaya.com/)|○|-|-|-|-|
|東京都(渋谷区)|[渋谷のラジオ](https://shiburadi.com/)|-|○|-|-|-|
|東京都(葛飾区)|[かつしかFM](https://kfm789.co.jp/)|-|○|-|○|-|
|東京都(江戸川区)|[FMえどがわ](https://www.fm843.co.jp/)|-|○|-|-|-|
|東京都(八王子市)|[Tokyo Star Radio](https://775fm.com/)|○|-|-|-|-|
|東京都(立川市)|[エフエムたちかわ](http://fm844.co.jp/)|○|-|-|○|-|
|東京都(武蔵野市)|[むさしのFM](https://www.musashino-fm.co.jp/)|-|○|-|-|-|
|東京都(府中市)|[ラジオフチューズ](https://radio-fuchues.tokyo/)|-|-|○|-|-|
|東京都(調布市)|[調布FM](https://www.chofu-fm.com/)|○|-|-|○|-|
|東京都(狛江市)|[コマラジ](https://www.komae.fm/)|-|○|-|-|-|
|東京都(東久留米市)|[TOKYO854 くるめラ](https://tokyo854.com/)|-|-|○|-|-|
|東京都(西東京市)|[エフエム西東京](https://842fm.com/)|-|-|○|-|-|
|神奈川県(横浜市中区)|[マリンFM](https://www.marine-fm.com/)|-|○|-|-|-|
|神奈川県(横浜市金沢区)|[金沢シーサイドFM](https://kanazawa-seasidefm.co.jp/)|-|-|○|-|-|
|神奈川県(横浜市戸塚区)|[エフエム戸塚](https://www.fm-totsuka.com/)|-|○|-|○|-|
|神奈川県(横浜市青葉区)|[FMサルース](https://www.fm-salus.jp/)|-|○|○|-|-|
|神奈川県(川崎市川崎区)|[FM大師](https://fmdaishi.jp/)|-|-|○|-|-|
|神奈川県(川崎市中原区)|[かわさきFM](https://www.kawasakifm.co.jp/)|○|-|-|○|-|
|神奈川県(相模原市中央区)|[FM HOT 839](https://fm839.com/)|-|-|○|○|-|
|神奈川県(横須賀市)|[FMブルー湘南](https://www.yokosukafm.com/)|-|○|-|-|-|
|神奈川県(平塚市)|[FM湘南ナパサ](http://www.fmshonan783.co.jp/)|-|○|-|-|-|
|神奈川県(鎌倉市)|[鎌倉FM](https://www.kamakurafm.co.jp/)|-|○|-|-|-|
|神奈川県(藤沢市)|[レディオ湘南](https://www.radioshonan.co.jp/)|-|○|○|-|-|
|神奈川県(小田原市)|[FMおだわら](https://fm-odawara.com/)|-|○|-|-|-|
|神奈川県(茅ヶ崎市)|[茅ヶ崎FM](https://chigasaki-fm.com/)|-|○|-|-|-|
|神奈川県(逗子市)|[湘南ビーチFM](https://www.beachfm.co.jp/)|-|-|-|-|○|
|神奈川県(大和市)|[FMやまと](https://www.fmyamato.co.jp/)|-|○|-|-|-|
|神奈川県(海老名市)|[FMカオン](https://www.fmkaon.com/)|○|-|-|○|-|
|神奈川県(大磯町)|[湘南マジックウェイブ](https://fm-smw.jp/)|-|○|-|-|-|
|新潟県(新潟市中央区)|[FM KENTO](https://fmkento.com/)|-|○|-|-|-|
|新潟県(新潟市秋葉区)|[ラジオチャット](https://www.chat761.com/)|-|○|-|-|-|
|新潟県(長岡市)|[FMながおか](http://www.fmnagaoka.com/)|-|○|-|-|-|
|新潟県(三条市)|[ラヂオは～と](http://www.heart768.com/)|-|-|○|-|-|
|新潟県(柏崎市)|[FMピッカラ](https://fm-pikkara.com/)|-|○|-|-|-|
|新潟県(新発田市)|[シバラジ](https://shibaradi769.com/)|-|○|-|-|-|
|新潟県(十日町市)|[エフエムとおかまち](http://www.fm-tokamachi.com/)|-|-|○|-|-|
|新潟県(妙高市)|[FMみょうこう](https://fm-myoko785.jp/)|-|-|○|-|-|
|新潟県(上越市)|[FM-J エフエム上越](https://www.fmj761.com/)|-|○|-|-|-|
|新潟県(魚沼市)|[FMうおぬま](https://fm-u814.com/)|-|○|-|-|-|
|新潟県(南魚沼市)|[FMゆきぐに](https://www.fm762.jp/)|-|○|-|-|-|
|富山県(富山市)|[富山シティエフエム](https://city-fm.co.jp/)|-|○|-|-|-|
|富山県(高岡市)|[ラジオたかおか](http://www.radiotakaoka.co.jp/)|-|○|-|-|-|
|富山県(黒部市)|[ラジオ・ミュー](https://www.fm761.co.jp/)|○|-|-|-|-|
|富山県(砺波市)|[エフエムとなみ](https://www.fmtonami.jp/)|-|○|-|-|-|
|石川県(金沢市)|[ラジオかなざわ](https://www.radiokanazawa.co.jp/)|-|○|-|-|-|
|石川県(七尾市)|[ラジオななお](https://www.radionanao.co.jp/)|-|○|-|-|-|
|石川県(小松市)|[ラジオこまつ](https://www.radio-komatsu-new.com/)|-|○|-|-|-|
|石川県(かほく市)|[FMかほく](https://fm.kahoku.net/)|-|-|-|-|○|
|石川県(野々市市)|[FM-N1](https://www.fmn1.jp/)|○|-|-|-|-|
|福井県(敦賀市)|[ハーバーステーション](http://harbor779.com/)|○|-|-|-|-|
|福井県(鯖江市)|[たんなんFM](http://tannan.fm/)|-|-|-|-|○|
|山梨県(甲府市)|[エフエム甲府](https://www.fm-kofu.co.jp/)|-|○|-|-|-|
|山梨県(富士吉田市)|[エフエムふじごこ](https://www.fm2255.jp/)|-|○|-|-|-|
|山梨県(北杜市)|[エフエム八ヶ岳](https://yatsugatake.ne.jp/)|-|○|-|-|-|
|山梨県(富士河口湖町)|[FMふじやま](https://fujiyama776.jp/)|-|○|-|-|-|
|長野県(松本市)|[FMまつもと](https://fmmatsumoto.jp/)|-|-|○|-|-|
|長野県(飯田市)|[いいだFM iステーション](https://iida.fm/)|-|-|○|-|-|
|長野県(諏訪市)|[エルシーブイFM769](https://lcvfm769.jp/)|-|○|○|-|-|
|長野県(伊那市)|[伊那谷FM](https://fm867.jp/)|-|○|-|-|-|
|長野県(塩尻市)|[高ボッチ高原FM](https://fm894.jp/)|-|○|-|-|-|
|長野県(佐久市)|[fmさくだいら](http://www.fmsakudaira.co.jp/)|-|-|○|-|-|
|長野県(東御市)|[はれラジ](https://fmtomi785.jp/)|-|-|○|-|-|
|長野県(安曇野市)|[あづみ野エフエム](https://azuminofm.co.jp/)|-|○|-|○|-|
|長野県(軽井沢町)|[FM軽井沢](https://fm-karuizawa.co.jp/)|-|○|-|-|-|
|岐阜県(岐阜市)|[FMわっち](https://www.fm-watch.net/)|-|○|-|-|-|
|岐阜県(高山市)|[HitsFM](https://hitsfm.jp/)|-|○|-|-|-|
|岐阜県(多治見市)|[FM PiPi](https://fmpipi.co.jp/)|-|○|-|-|-|
|岐阜県(可児市)|[FMらら](http://fm768.jp/)|-|-|○|-|-|
|静岡県(静岡市葵区)|[FM-Hi!](http://www.fmhi.co.jp/)|-|○|-|-|-|
|静岡県(静岡市清水区)|[マリンパル](https://mrn-pal.com/)|-|○|-|-|-|
|静岡県(浜松市中央区)|[FM Haro!](https://www.fmharo.co.jp/)|-|○|-|-|-|
|静岡県(沼津市)|[コーストエフエム](https://www.coast-fm.com/)|-|○|-|-|-|
|静岡県(熱海市)|[Ciao!](https://www.ciao796.com/)|-|○|-|-|-|
|静岡県(三島市)|[ボイス・キュー](https://777fm.com/)|-|○|-|-|-|
|静岡県(伊東市)|[FMなぎさステーション](https://www.fmito.com/)|-|○|-|-|-|
|静岡県(島田市)|[g-sky76.5](https://www.gsky765.jp/)|-|○|-|-|-|
|静岡県(富士市)|[Radio-f](https://radio-f.jp/)|-|○|-|-|-|
|静岡県(焼津市)|[RADIO LUSH](https://radiolush.jp/)|-|○|-|-|-|
|静岡県(御殿場市)|[富士山GOGOエフエム](https://www.863.fm/)|-|○|-|-|-|
|静岡県(伊豆市)|[みらいずステーション](https://fmis.jp/)|-|○|-|-|-|
|静岡県(伊豆の国市)|[FMいずのくに](https://www.fmizunokuni.jp/)|-|○|-|-|-|
|愛知県(名古屋市中区)|[MID-FM761](https://midfm761.com/)|-|-|○|-|-|
|愛知県(名古屋市中区)|[Heart FM](https://heartfm.jp/)|-|○|-|-|-|
|愛知県(豊橋市)|[やしの実FM](https://843fm.co.jp/)|-|-|○|-|-|
|愛知県(岡崎市)|[エフエムEGAO](https://fm-egao.jp/)|○|-|-|○|-|
|愛知県(一宮市)|[i-wave 76.5FM](https://iwave765.com/)|-|○|-|-|-|
|愛知県(瀬戸市)|[RADIO SANQ](http://845.fm/)|-|○|-|-|-|
|愛知県(刈谷市)|[Pitch FM](https://838.fm/)|-|-|○|-|-|
|愛知県(豊田市)|[RADIO LOVEAT](https://www.loveat.co.jp/)|-|-|○|-|-|
|愛知県(犬山市)|[United North](https://842fm.jp/)|-|○|-|-|-|
|愛知県(東海市)|[メディアスエフエム](https://www.medias.fm/)|-|-|○|-|-|
|愛知県(蟹江町)|[エフエムななみ](https://fm773.jp/)|-|○|-|-|-|
|三重県(四日市市)|[CTY-FM](https://cty-fm.com/)|-|-|○|-|-|
|三重県(鈴鹿市)|[Suzuka Voice FM](https://suzuka-voice.fm/)|-|○|-|-|-|
|三重県(いなべ市)|[いなべエフエム](https://fm861.com/)|-|○|-|-|-|
|滋賀県(大津市)|[FMおおつ](https://fmotsu.com/)|-|-|○|-|-|
|滋賀県(彦根市)|[エフエムひこね](https://www.fmhikone.jp/)|-|-|○|-|-|
|滋賀県(草津市)|[えふえむ草津](https://fm785.jp/)|-|○|-|-|-|
|滋賀県(甲賀市)|[エフエム花](https://fm-hana.net/)|○|-|-|-|-|
|滋賀県(東近江市)|[Radio Sweet FMひがしおうみ](http://www.sweet815.com/)|○|-|-|-|-|
|京都府(京都市北区)|[RADIO MIX KYOTO](https://radiomix.kyoto/)|○|-|-|○|-|
|京都府(京都市中京区)|[京都三条ラジオカフェ](https://radiocafe.jp/)|○|-|-|○|-|
|京都府(京都市伏見区)|[FM845](https://www.fm-845.com/)|-|○|-|-|-|
|京都府(福知山市)|[FM丹波](http://fukuchiyama.fm-tanba.jp/)|-|-|-|○|-|
|京都府(舞鶴市)|[FMまいづる](https://775maizuru.jp/)|-|○|-|-|-|
|京都府(綾部市)|[FMいかる](https://fmikaru.jp/)|-|○|-|-|-|
|京都府(宇治市)|[FMうじ](https://www.fmuji.com/)|-|○|-|-|-|
|京都府(長岡京市)|[FMおとくに](https://fm-otokuni.com/)|○|-|-|-|-|
|京都府(京丹後市)|[FMたんご](https://fm-tango.jp/)|○|-|-|-|-|
|大阪府(大阪市北区)|[ウメダFM Be Happy!789](https://www.be-happy789.com/)|-|○|-|-|-|
|大阪府(大阪市中央区)|[YES-fm](https://www.yesfm.jp/)|-|-|○|-|-|
|大阪府(岸和田市)|[ラヂオきしわだ](https://www.radiokishiwada.jp/)|-|-|-|-|○|
|大阪府(豊中市)|[FM千里](http://www.senri-fm.jp/)|-|○|-|-|-|
|大阪府(泉大津市)|[FMいずみおおつ](https://fmizumiotsu.jp/)|-|-|○|-|-|
|大阪府(箕面市)|[タッキー816みのおエフエム](https://fm.minoh.net/)|-|○|-|-|-|
|兵庫県(神戸市中央区)|[FM MOOV](https://www.fm-moov.com/)|-|-|-|○|-|
|兵庫県(姫路市)|[FMゲンキ](https://fmgenki.jp/)|-|○|-|-|-|
|兵庫県(尼崎市)|[みんなのあま咲き放送局](https://amasaki-fm.com/)|-|-|○|-|-|
|兵庫県(西宮市)|[さくらFM](https://sakura-fm.co.jp/)|-|○|-|-|-|
|兵庫県(伊丹市)|[エフエムいたみ](https://www.itami.fm/)|-|○|-|-|-|
|兵庫県(豊岡市)|[FMジャングル](http://www.764.fm/)|○|-|-|○|-|
|兵庫県(加古川市)|[BAN-BANラジオ](https://www.banban.jp/radio/)|○|-|-|○|-|
|兵庫県(宝塚市)|[エフエム宝塚](https://835.jp/)|-|○|-|-|-|
|兵庫県(三木市)|[エフエムみっきぃ](http://www.fm-miki.jp/)|-|○|-|-|-|
|兵庫県(丹波市)|[805たんば](https://805.tanba.info/)|-|○|-|○|-|
|奈良県(奈良市)|[ならどっとFM](http://narafm.jp/)|-|○|-|-|-|
|奈良県(大和高田市)|[FMヤマト](https://fmyamato.jp/)|-|-|○|-|-|
|奈良県(五條市)|[FM五條](http://shousuien.or.jp/fm_gojo/)|-|○|-|-|-|
|奈良県(田原本町)|[FMまほろば](https://tawaramoton.com/fm_mahoroba/)|-|○|-|-|-|
|奈良県(王寺町)|[FMハイホー](https://www.fm814.co.jp/)|-|○|-|-|-|
|和歌山県(和歌山市)|[Banana FM](https://877.fm/)|-|○|-|-|-|
|和歌山県(橋本市)|[FMはしもと](http://816.fm/)|-|○|-|○|-|
|和歌山県(田辺市)|[FM TANABE](https://www.fm885.jp/)|-|○|-|-|-|
|和歌山県(白浜町)|[ビーチステーション](https://www.fm764.com/)|-|○|-|-|-|
|鳥取県(鳥取市)|[RADIO BIRD](https://www.radiobird.net/)|-|○|-|-|-|
|鳥取県(米子市)|[DARAZ FM](http://www.darazfm.com/)|○|-|-|○|-|
|岡山県(岡山市北区)|[レディオモモ](http://www.fm790.co.jp/)|-|○|-|-|-|
|岡山県(倉敷市)|[FMくらしき](https://fmkurashiki.com/)|-|○|-|-|-|
|岡山県(津山市)|[エフエムつやま](https://www.fm-tsuyama.jp/)|-|-|-|-|○|
|岡山県(笠岡市)|[エフエムゆめウェーブ](https://www.yumewave.net/)|-|-|○|-|-|
|広島県(広島市中区)|[FMちゅーピー](https://chupea.fm/)|-|○|-|-|-|
|広島県(三原市)|[FMみはら](https://www.fm-mihara.jp/)|-|○|-|-|-|
|広島県(尾道市)|[FMおのみち](https://www.fmo.co.jp/)|-|○|-|-|-|
|広島県(福山市)|[FMふくやま](https://fm777.co.jp/)|-|○|-|-|-|
|広島県(東広島市)|[FM東広島](https://fmhigashi.jp/)|-|○|-|-|-|
|広島県(廿日市市)|[FMはつかいち](https://761.jp/)|-|○|-|-|-|
|山口県(下関市)|[カモンエフエム](https://www.c-fm.co.jp/)|-|○|-|-|-|
|山口県(防府市)|[FMわっしょい](http://www.fm-wassyoi.jp/)|-|-|○|-|-|
|山口県(周南市)|[しゅうなんFM](https://www.fms784.co.jp/)|-|○|-|-|-|
|山口県(山陽小野田市)|[FMスマイルウェ～ブ](http://www.sw897.jp/)|-|-|○|-|-|
|徳島県(徳島市)|[B・FM791](http://www.bfm.jp/)|○|-|-|○|-|
|香川県(高松市)|[FM815](https://www.fm815.com/)|○|-|-|○|-|
|香川県(坂出市)|[FM SUN](https://fm-sun.jp/)|-|○|-|-|-|
|愛媛県(今治市)|[FMラヂオバリバリ](http://www.baribari789.com/)|-|○|-|-|-|
|愛媛県(宇和島市)|[FMがいや](http://www.gaiya769.jp/)|-|○|-|-|-|
|愛媛県(新居浜市)|[新居浜 FM78.0](https://www.hello78.jp/)|-|○|-|-|-|
|高知県(四万十市)|[FMはたらんど](https://fmhataland.jp/)|-|-|○|-|-|
|福岡県(北九州市若松区)|[AIR STATION HIBIKI](https://www.hibiki882.jp/)|○|-|-|○|-|
|福岡県(北九州市小倉北区)|[FM KITAQ](https://www.fm-kitaq.com/)|-|-|○|-|-|
|福岡県(福岡市中央区)|[コミュニティラジオ天神（コミてん）](https://radio.comiten.jp/)|-|-|○|○|-|
|福岡県(大牟田市)|[FMたんと](https://www.fmtanto.jp/)|-|-|○|-|-|
|福岡県(久留米市)|[Dreams FM](https://www.dreamsfm.co.jp/)|-|○|-|-|-|
|福岡県(直方市)|[チョクラジ](https://choku861.jp/)|○|-|-|-|-|
|福岡県(八女市)|[FM八女](https://www.fmyame.jp/)|-|○|-|-|-|
|福岡県(築上町)|[スターコーンFM](http://www.starcornfm.com/)|-|-|-|○|-|
|佐賀県(佐賀市)|[えびすFM](https://ebisufm.com/)|-|-|○|-|-|
|佐賀県(唐津市)|[FMからつ](http://www.fmkaratsu.com/)|-|○|-|-|-|
|長崎県(佐世保市)|[はっぴぃ!FM](https://happyfm873.com/)|-|-|○|-|-|
|長崎県(島原市)|[FMしまばら](https://www.shimabara.fm/)|-|-|○|○|-|
|長崎県(諫早市)|[レインボーエフエム](http://www.771fm.co.jp/)|-|-|○|-|-|
|長崎県(対馬市)|[エフエム対馬](https://fmtsushima.ne.jp/)|-|-|○|-|-|
|長崎県(南島原市)|[FMひまわり](http://himawarinet.ne.jp/?page_id=2700)|-|-|○|-|-|
|熊本県(熊本市中央区)|[熊本シティエフエム](https://fm791.jp/)|-|○|-|-|-|
|熊本県(八代市)|[KappaFM](https://kappafm.com/)|-|○|-|-|-|
|熊本県(天草市)|[みつばちラジオ](https://www.acn-tv.co.jp/radio.html)|-|-|○|-|-|
|大分県(中津市)|[NOAS FM](https://789.co.jp/)|-|○|-|-|-|
|大分県(由布市)|[ゆふいんラヂオ局](http://874.fm/)|-|○|-|-|-|
|宮崎県(宮崎市)|[宮崎サンシャインFM](http://www.sunfm.co.jp/)|-|-|○|-|-|
|宮崎県(延岡市)|[FMのべおか](https://www.fmnobeoka.jp/)|○|-|-|○|-|
|宮崎県(日向市)|[FMひゅうが](https://767.fm/)|-|-|○|-|-|
|鹿児島県(鹿児島市)|[FMぎんが](http://fm786.jp/)|-|-|○|○|-|
|鹿児島県(鹿児島市)|[フレンズFM762](https://www.friendsfm.co.jp/)|-|-|○|-|-|
|鹿児島県(鹿屋市)|[FMかのや](https://www.772fm.net/)|-|-|○|-|-|
|鹿児島県(薩摩川内市)|[FMさつませんだい](https://fm871.com/)|-|-|○|-|-|
|鹿児島県(霧島市)|[プラスきりしま](http://plakiri.com/fm769/)|-|-|○|-|-|
|鹿児島県(奄美市)|[あまみエフエム ディ!ウェイヴ](http://www.npo-d.org/)|○|-|-|○|-|
|鹿児島県(龍郷町)|[エフエムたつごう](https://tatsugo.fm-s.org/)|○|-|-|-|-|
|沖縄県(那覇市)|[FM那覇](https://www.fmnaha.jp/)|○|-|-|-|-|
|沖縄県(那覇市)|[FMレキオ](https://www.fmlequio.com/)|-|-|○|○|-|
|沖縄県(宜野湾市)|[FMぎのわん](https://fmginowan.com/)|○|-|-|-|-|
|沖縄県(宜野湾市)|[ぎのわんシティFM](https://gcfm818.com/)|○|-|-|-|-|
|沖縄県(石垣市)|[FMいしがき サンサンラジオ](https://www.fmishigaki.jp/)|○|-|-|-|-|
|沖縄県(浦添市)|[FM21](https://www.fm21.net/)|-|-|○|○|-|
|沖縄県(名護市)|[FMやんばる](https://fmyanbaru.co.jp/)|○|-|-|-|-|
|沖縄県(沖縄市)|[オキラジ](https://fm854.fun/)|○|-|-|-|-|
|沖縄県(豊見城市)|[FMとよみ](https://www.fm-toyomi.com/)|○|-|-|-|-|
|沖縄県(うるま市)|[FMうるま](https://fmuruma.com/)|-|-|○|-|-|
|沖縄県(宮古島市)|[FMみやこ](https://www.fm-miyako.com/)|-|-|○|-|-|
|沖縄県(本部町)|[ちゅらハート FMもとぶ](https://www.motob.net/)|-|-|○|○|-|
|沖縄県(久米島町)|[FMくめじま](http://fmkumejima.com/)|-|-|○|○|-|

上記以外の放送局も、Kodi/ffmpegが対応する配信方式であれば、放送局名と配信ストリームのURLを登録することで、他の放送局と同様に画面から選択して利用できます。
詳しくは[放送局設定画面](#放送局設定画面)をご覧ください。

上表の作成にあたっては以下のページを参考にしました。
放送局名の表記は[コミュニティFM放送局のLink集](https://channellists.tokyo/161.html)にしたがいました。

* [コミュニティ放送局一覧](https://ja.wikipedia.org/wiki/コミュニティ放送局一覧)
* [コミュニティ放送事業者一覧](https://www.tele.soumu.go.jp/j/adm/system/bc/now/index.htm)
* [コミュニティFM放送局のLink集](https://channellists.tokyo/161.html)

