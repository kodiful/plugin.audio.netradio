# Kodiアドオン：ネットラジオクライアント

![トップ画面](https://user-images.githubusercontent.com/12268536/233762697-6339fd83-a782-43e2-bb28-b47f844913a8.png)

[NHKラジオ](http://www.nhk.or.jp/radio/)、[民放ラジオ（radiko.jp）](http://radiko.jp)ほかが提供するインターネットラジオ放送局を聴いたり、番組をファイル保存できるKodiアドオンです。
Windows、macOSで動作検証しています。


## 目次

[概要](#概要)

[トップ画面](#トップ画面)

[放送局設定画面](#放送局設定画面)

[キーワード設定画面](#キーワード設定画面)

[アドオン設定画面-一般](#アドオン設定画面-一般)

[アドオン設定画面-番組保存](#アドオン設定画面-番組保存)

[アドオン設定画面-その他](#アドオン設定画面-その他)

[コミュニティラジオ放送局一覧](#コミュニティラジオ放送局一覧)


## 概要

### 番組再生

Kodi単体ではストリーム再生できない一部のコミュニティラジオに対応するために、アドオン内部に設けたプロキシ機能（ローカルプロキシ）を用いて必要な処理を行っています。

### 番組表示

NHKラジオおよび民放ラジオ（radiko.jp）については、現在時刻の番組情報が自動的に取得され、画面が更新されます。
番組情報が定時から0分〜数分遅れて配信されているために、画面の更新も引きずられて遅れることがあります。

### 番組保存

番組保存は、あらかじめ設定したキーワード情報と、NHKラジオおよび民放ラジオ（radiko.jp）について配信される番組情報に基づいて、番組を単位としてファイルに保存します。
NHKラジオおよび民放ラジオ（radiko.jp）以外の番組保存、開始／終了時間を指定した保存には対応してしません。

キーワード設定は、NHKラジオまたは民放ラジオ（radiko.jp）の放送局を右クリックして表示されるコンテクストメニューから「キーワードを追加する」を選択して設定します。
この場合は、選択した放送局の放送中の番組の情報が入力された状態で設定画面が立ち上がるので、文字入力の手間を省くことができます。
アドオン設定画面から「キーワードを追加する」を選択して設定することもできます。

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
トップ画面は、放送局表示部、ディレクトリ表示部、キーワード表示部から構成されます。
初期状態はディレクトリ表示部のみで、これに対して放送局やキーワードを追加することで、放送局表示部、キーワード表示部を含むトップ画面が構成されます。

![トップ画面](https://user-images.githubusercontent.com/12268536/233762697-6339fd83-a782-43e2-bb28-b47f844913a8.png)

### 放送局表示部

ディレクトリから選択した放送局や、[放送局設定画面](#放送局設定画面)で設定した放送局をこの部分に表示します。
放送局を選択して現在放送中の番組を聴くことができます。

### ディレクトリ表示部

以下の三つのディレクトリに分類された放送局から選択して、ストリーム再生したり、トップ画面に追加できます。

* NHKラジオ
  
  radikoの認証で判定された地域にしたがって、「東京」「札幌」「仙台」「名古屋」「大阪」「広島」「松山」「福岡」のいずれかのNHKラジオ第1とNHK-FM、およびNHKラジオ第2（全国共通）が選択できます。

  ![保存番組一覧](https://user-images.githubusercontent.com/12268536/233762678-236ddbc7-4fbf-427d-8be9-eddd50b9a27b.png)

* 民放ラジオ（radiko.jp）
  
  radikoの認証で判定された地域にしたがって、受信可能な民放ラジオが選択できます。

  ![保存番組一覧](https://user-images.githubusercontent.com/12268536/233762687-cb2ee081-abe8-4bc7-90e5-4db85c2ef5ab.png)

* コミュニティラジオ
  
  あらかじめ設定されているコミュニティラジオ（[コミュニティラジオ放送局一覧](#コミュニティラジオ放送局一覧)）を、地域ごとに検索して選択できます。
  
  ![保存番組一覧](https://user-images.githubusercontent.com/12268536/233762685-46b45470-1578-409d-9c10-b0bd9622c62d.png)

  ![保存番組一覧](https://user-images.githubusercontent.com/12268536/233762683-fe57572c-bf47-4d50-8c61-b2341dc58c6d.png)

  ![保存番組一覧](https://user-images.githubusercontent.com/12268536/233762681-be0c8631-e5e9-407e-a074-fac0ca738206.png)

ディレクトリの配下にある各放送局を選択して現在放送中の番組をストリーム再生できます。

ディレクトリの配下にある各放送局を右クリックして表示されるコンテクストメニューから「トップ画面に追加する」を選択して、選択した放送局をトップ画面の放送局表示部に追加できます。

### キーワード表示部

あらかじめ指定したキーワード情報に基づいて自動保存された番組をキーワードごとに表示します。
RSS生成をオンにすると、キーワードに対応するRSSのURLを埋め込んだQRコードがアイコン/サムネイルとして表示されます。
キーワードを選択してこのキーワードに基づいて自動保存された番組の一覧を表示します。

![保存番組一覧](https://user-images.githubusercontent.com/12268536/233771889-21c31b83-6d30-4d57-ad88-ab74a7e37ebd.png)

一覧から番組を選択して聴くことができます。


## 放送局設定画面

ディレクトリに配置された放送局と同様に、それ以外の放送局についても、局名と配信ストリームのURLを登録してトップ画面に追加できます。

[アドオン設定画面-一般](#アドオン設定画面-一般)から開くことができます。

![放送局設定画面](https://user-images.githubusercontent.com/12268536/233768184-05564b82-c68e-45a7-8bfd-f2d6ce911645.png)

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


## キーワード設定画面

番組保存のためのキーワードを設定します。

NHKラジオまたは民放ラジオ（radiko.jp）の放送局を右クリックして表示されるコンテクストメニューから「キーワードを追加する」を選択して開くことができます。
[アドオン設定画面-一般](#アドオン設定画面-一般)からも開くことができます。

![キーワード設定画面](https://user-images.githubusercontent.com/12268536/233762692-fa24cd8c-74b0-46e0-8402-0c9b709b776a.png)

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

![アドオン設定画面-一般](https://user-images.githubusercontent.com/12268536/233762691-24d39333-be79-48f5-9898-fa8e61373753.png)

### 放送局を追加する

[放送局設定画面](#放送局設定画面)を開いてキーワードを設定します。

### キーワードを追加する

[キーワード設定画面](#キーワード設定画面)を開いてキーワードを設定します。


## アドオン設定画面-番組保存

![アドオン設定画面-番組保存](https://user-images.githubusercontent.com/12268536/233762688-cbb80db9-3fba-4815-a98a-29523bce7b20.png)

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
RSSは _http\://127.0.0.1/NetRadio/rss.xml_ から取得できます。

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

![アドオン設定画面-その他](https://user-images.githubusercontent.com/12268536/233762694-28515723-a670-494f-93e1-364c18ab4793.png)

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

 以下のサイトに掲載されているコミュニティラジオ（一部を除く）があらかじめ設定されています。これ以外の放送局も、放送局名と配信ストリームのURLを登録することで、他の放送局と同様に画面から選択して利用できます。詳しくは[放送局設定画面](#放送局設定画面)をご覧ください。

  * [ListenRadio（LR）](http://listenradio.jp)
  * [エフエムプラプラ（FM++）](https://fmplapla.com)
  * [一般社団法人日本コミュニティ放送協会（JCBA）](https://www.jcbasimul.com)
  * [コミュニティ・サイマルラジオ・アライアンス（CSRA）](https://csra.fm)

複数のサイトに掲載されている場合は、最も左側のサイトに掲載されている情報に基づいてストリーミング再生します。

|都道府県（市区町村）|放送局|LR|FM++|JCBA|CSRA|
|:---|:---|:---|:---|:---|:---|
|北海道|[ラジオニセコ](https://radioniseko.jp/)|-|-|○|○|
|北海道（札幌市）|FMアップル|○|-|-|○|
|北海道（札幌市）|RADIOワンダーストレージ FMドラマシティ|○|-|-|-|
|北海道（札幌市）|さっぽろ村ラジオ|○|-|-|○|
|北海道（札幌市）|[ラジオカロスサッポロ](http://www.radiokaros.com/)|○|-|-|○|
|北海道（札幌市）|三角山放送局(札幌市西区)|○|-|-|-|
|北海道（函館市）|[FMいるか](http://www.fmiruka.co.jp/)|-|-|○|-|
|北海道（小樽市）|[FMおたる](http://fmotaru.jp/)|-|-|-|○|
|北海道（旭川市）|[FMりべーる](http://www.fm837.com/)|○|-|-|○|
|北海道（釧路市）|[FMくしろ](http://www.fm946.com)|○|-|-|○|
|北海道（帯広市）|FM JAGA|○|-|-|○|
|北海道（帯広市）|[FM WING](http://www.fmwing.com/index.html)|○|-|-|○|
|北海道（網走市）|FM ABASHIRI|○|-|-|-|
|北海道（留萌市）|[エフエムもえる](http://www.moeru.fm/)|-|-|○|-|
|北海道（稚内市）|[FMわっぴ〜](http://wappy761.jp)|-|-|-|○|
|北海道（名寄市）|[Airてっし](http://www.nayoro.fm/)|-|-|○|-|
|北海道（根室市）|FMねむろ|○|-|-|○|
|北海道（恵庭市）|[e-niwaFM](http://www.e-niwa.tv/)|-|-|-|○|
|北海道（伊達市）|wi-radio|○|-|-|○|
|北海道（北広島市）|FMメイプル|○|-|-|○|
|北海道（中標津町）|[FMはな](http://fmhana.jp/)|-|-|○|-|
|青森県|[BeFM](http://www.befm.co.jp/)|○|-|-|○|
|青森県|[FM AZUR](http://www.fmazur.jp/)|-|-|○|-|
|青森県|[アップルウェーブ](http://www.applewave.co.jp/)|-|-|○|-|
|青森県（五所川原市）|[FMごしょがわら](https://fm767.jp/)|-|-|○|-|
|岩手県（盛岡市）|ラヂオもりおか|○|-|-|○|
|岩手県（宮古市）|[みやこハーバーラジオ](http://miyakofm.com)|○|-|-|○|
|岩手県（大船渡市）|FMねまらいん|-|○|-|-|
|岩手県（花巻市）|[FMONE](https://fm-one.net/)|-|-|○|-|
|岩手県（北上市）|きたかみE&Beエフエム|-|○|-|-|
|岩手県（一関市）|FMあすも|-|○|-|-|
|岩手県（陸前高田市）|[陸前高田災害FM](http://rikuzentakata-fm.blogspot.com/)|-|-|-|○|
|岩手県（釜石市）|[釜石災害FM](http://www.city.kamaishi.iwate.jp/index.cfm/12,18557,121,html)|-|-|-|○|
|岩手県（二戸市）|カシオペアFM|○|-|-|○|
|宮城県|BAY WAVE|○|-|-|○|
|宮城県（仙台市）|fmいずみ|○|-|-|○|
|宮城県（仙台市）|[FMたいはく](http://www.fm-t.net/)|-|-|-|○|
|宮城県（仙台市）|RADIO3|○|-|-|-|
|宮城県（石巻市）|[ラジオ石巻](http://www.fm764.jp/)|○|-|-|○|
|宮城県（気仙沼市）|ラヂオ気仙沼|○|-|-|-|
|宮城県（名取市）|[なとらじ](http://www.natori801.jp/)|-|-|-|○|
|宮城県（名取市）|なとらじ801|○|-|-|-|
|宮城県（岩沼市）|[エフエムいわぬま](http://fm779.com/)|-|-|○|-|
|宮城県（登米市）|[H@!FM](http://hat-fm.net/)|-|-|○|-|
|宮城県（大崎市）|OCRFM835|-|○|-|-|
|宮城県（亘理町）|FMあおぞら|-|○|-|-|
|宮城県（亘理町）|[亘理臨時災害FM局(FMあおぞら)](http://www.town.watari.miyagi.jp/index.cfm/22,21308,126,html)|-|-|-|○|
|宮城県（山元町）|[りんごFM](http://ringo-radio.cocolog-nifty.com/)|-|-|-|○|
|秋田県（秋田市）|エフエム椿台|○|-|-|○|
|秋田県（横手市）|[横手かまくらエフエム](http://www.fmyokote.com/)|○|-|-|○|
|秋田県（大館市）|FMラジオおおだて|-|○|-|-|
|秋田県（湯沢市）|[FMゆーとぴあ](http://www.yutopia.or.jp/%7Efm763/)|○|-|-|○|
|秋田県（鹿角市）|[鹿角きりたんぽFM](http://fm791.net/)|○|-|-|○|
|秋田県（大仙市）|FMはなび|-|○|-|-|
|山形県（山形市）|[ラジオ モンスター](http://www.fm762.co.jp/)|-|-|○|-|
|山形県（米沢市）|[エフエムNCV](https://fm834.jp/)|-|-|○|-|
|山形県（酒田市）|[ハーバーラジオ](https://www.sakatafm.com/)|-|-|○|-|
|山形県（長井市）|[えふえむい〜じゃんおらんだらじお](https://oranda-radio.jp/)|-|-|○|-|
|福島県（福島市）|[FMポコ](http://fm-poco.co.jp/)|-|-|○|-|
|福島県（会津若松市）|[FM愛'S](http://www.fmaizu.com/)|-|-|○|-|
|福島県（郡山市）|KOCOラジ|○|-|-|-|
|福島県（郡山市）|[郡山コミュニティ放送](http://www.kocofm.jp/)|-|-|-|○|
|福島県（いわき市）|[FMいわき](http://www.fm-iwaki.co.jp/cgi-bin/WebObjects/1201dac04a1.woa/)|○|-|-|○|
|福島県（須賀川市）|[ウルトラFM](http://ultrafm868.jp/)|-|-|○|-|
|福島県（喜多方市）|[エフエムきたかた](http://www.fm-kitakata.co.jp/)|-|-|○|-|
|福島県（南相馬市）|[南相馬ひばりエフエム](http://minamisomasaigaifm.hostei.com/index.html)|-|-|-|○|
|福島県（本宮市）|FM Mot.com|○|-|-|-|
|福島県（本宮市）|[エフエム モットコム](http://www.fm-mot.com/)|-|-|-|○|
|福島県（富岡町）|[富岡臨時災害FM局(おだがいさまFM)](http://www.gurutto-koriyama.com/detail/index_213.html)|-|-|-|○|
|茨城県|[FMかしま](http://www.767fm.com/)|-|-|○|-|
|茨城県（水戸市）|[FMぱるるん](http://www.fmpalulun.co.jp/)|○|-|-|○|
|茨城県（日立市）|[FMひたち](http://www.hfm.or.jp/)|○|-|-|○|
|茨城県（高萩市）|[たかはぎFM](http://www.t768.net)|○|-|-|○|
|茨城県（牛久市）|[FM-UU](http://fmuu.jp/)|-|-|-|○|
|茨城県（牛久市）|FMうしくうれしく放送|○|-|-|-|
|茨城県（つくば市）|[ラヂオつくば](http://radio-tsukuba.net)|-|-|-|○|
|茨城県（大子町）|[FMだいご](http://www.fmdaigo775.jp/)|-|-|○|-|
|栃木県（宇都宮市）|ミヤラジ|-|○|-|-|
|栃木県（栃木市）|FMくらら857|-|○|-|-|
|栃木県（小山市）|おーラジ|-|○|-|-|
|栃木県（真岡市）|FMもおか|-|○|-|-|
|栃木県（下野市）|FMゆうがお|-|○|-|-|
|群馬県|[FM OZE](http://www.fm-oze.co.jp/)|-|-|○|-|
|群馬県|[エフエム太郎](http://www.fmtaro.co.jp/)|-|-|○|-|
|群馬県|[ラジオ高崎](http://www.takasaki.fm/)|-|-|○|-|
|群馬県（前橋市）|まえばしCITYエフエム|○|-|-|-|
|群馬県（桐生市）|FM桐生|-|○|-|-|
|群馬県（玉村町）|[ラヂオななみ](http://www.fm773.co.jp/)|-|-|○|-|
|埼玉県|[FMチャッピー](https://fmchappy.jp/)|-|-|○|-|
|埼玉県|[ラジオ川越](https://radiokawagoe.com)|-|-|○|-|
|埼玉県（さいたま市）|[REDS WAVE](http://redswave.com)|○|-|-|○|
|埼玉県（熊谷市）|FMクマガヤ|-|○|-|-|
|埼玉県（川口市）|[FM Kawaguchi](http://www.fm856.co.jp/)|○|-|-|○|
|埼玉県（秩父市）|ちちぶFM|-|○|-|-|
|埼玉県（本庄市）|ほんじょうFM|-|○|-|-|
|埼玉県（鴻巣市）|[フラワーラジオ](https://www.fm767.com/)|○|-|-|○|
|埼玉県（深谷市）|FMふっかちゃん|○|-|-|○|
|埼玉県（越谷市）|ハローハッピー・こしがやエフエム|○|-|-|-|
|埼玉県（朝霞市）|[775ライブリーFM](https://775fm.co.jp/)|○|-|-|○|
|埼玉県（富士見市）|[発するFM](http://fm840.com/)|-|-|○|-|
|千葉県|[ラジオ成田](https://www.narita.fm/)|-|-|○|-|
|千葉県（千葉市）|[SKYWAVE FM](https://www.892fm.com/)|-|-|○|-|
|千葉県（市川市）|[市川うららFM(I&U-LaLaFM)](http://www.fmu.co.jp/)|-|-|○|-|
|千葉県（木更津市）|[かずさFM](https://www.kazusafm.net/)|-|-|○|-|
|千葉県（八千代市）|[ふくろうFM](http://296.fm/)|-|-|○|-|
|東京都|[FMえどがわ](https://www.fm843.co.jp/)|-|-|○|-|
|東京都|[かつしかFM](https://kfm789.co.jp/)|-|-|○|○|
|東京都|[むさしのFM](https://www.musashino-fm.co.jp/)|-|-|○|-|
|東京都|[渋谷のラジオ](https://shiburadi.com/)|-|-|○|-|
|東京都（中央区）|RadioCity 中央エフエム|○|-|-|-|
|東京都（江東区）|[レインボータウンFM](http://www.792fm.com/)|○|-|-|○|
|東京都（品川区）|[FMしながわ](https://fm-shinagawa.co.jp/)|-|-|○|-|
|東京都（世田谷区）|エフエム世田谷|○|-|-|○|
|東京都（練馬区）|練馬放送|○|-|-|-|
|東京都（八王子市）|Tokyo Star Radio(八王子FM)|○|-|-|-|
|東京都（立川市）|FMたちかわ|○|-|-|-|
|東京都（立川市）|[エフエムたちかわ](http://www.fm844.co.jp/)|-|-|-|○|
|東京都（府中市）|ラジオフチューズ|○|○|-|○|
|東京都（調布市）|[調布FM](http://www.chofu-fm.com/)|○|-|-|○|
|東京都（狛江市）|コマラジ|○|-|-|○|
|東京都（東久留米市）|TOKYO854 くるめラ|-|○|-|-|
|東京都（西東京市）|エフエム西東京|-|○|-|-|
|神奈川県|[FMブルー湘南](http://www.yokosukafm.com/)|-|-|○|-|
|神奈川県|[FM湘南ナパサ](http://www.fmshonan783.co.jp/)|-|-|○|-|
|神奈川県|[FM湘南マジックウェイブ](https://fm-smw.jp/)|-|-|○|-|
|神奈川県|[鎌倉FM](https://www.kamakurafm.co.jp/)|-|-|○|-|
|神奈川県（横浜市）|[FMサルース](http://www.fm-salus.jp/)|-|○|○|-|
|神奈川県（横浜市）|[FM戸塚](http://www.fm-totsuka.com)|-|-|-|○|
|神奈川県（横浜市）|エフエム戸塚|○|-|-|-|
|神奈川県（横浜市）|マリンFM|○|-|-|○|
|神奈川県（横浜市）|金沢シーサイドFM|-|○|-|-|
|神奈川県（川崎市）|[かわさきFM](http://www.kawasakifm.co.jp/)|○|-|-|○|
|神奈川県（相模原市）|FM HOT 839|-|○|-|-|
|神奈川県（相模原市）|[エフエムさがみ](http://www.fmsagami.co.jp/)|-|-|-|○|
|神奈川県（藤沢市）|[レディオ湘南](https://www.radioshonan.co.jp/index.html)|-|○|○|-|
|神奈川県（小田原市）|[FMおだわら](https://fm-odawara.com/)|-|-|○|-|
|神奈川県（大和市）|[FMやまと](http://www.fmyamato.co.jp/)|-|-|○|-|
|神奈川県（海老名市）|[FM kaon](http://www.fmkaon.com/)|-|-|-|○|
|神奈川県（海老名市）|FMカオン|○|-|-|-|
|新潟県|[FM KENTO](https://fmkento.com/)|-|-|○|-|
|新潟県|[FMうおぬま](https://fm-u814.com/)|-|-|○|-|
|新潟県（新潟市）|[ラジオチャット・FMにいつ](http://www.chat761.com/index.html)|-|-|○|-|
|新潟県（長岡市）|[エフエムながおか](http://www.fmnagaoka.com/)|-|-|○|-|
|新潟県（柏崎市）|[FMピッカラ](http://www.kisnet.or.jp/pikkara/)|-|-|○|-|
|新潟県（新発田市）|[エフエムしばた](http://www.agatt769.co.jp/)|-|-|○|-|
|新潟県（十日町市）|FMとおかまち|-|○|-|-|
|新潟県（燕市）|ラヂオは〜と|-|○|-|-|
|新潟県（妙高市）|FMみょうこう|-|○|-|-|
|新潟県（上越市）|[FMじょうえつ](https://www.fmj761.com/)|-|-|○|-|
|新潟県（南魚沼市）|[FMゆきぐに](http://www.fm762.jp/)|-|-|○|-|
|富山県|[ラジオたかおか](http://www.radiotakaoka.co.jp/)|-|-|○|-|
|富山県|[富山シティエフエム株式会社](http://www.city-fm.co.jp/)|-|-|○|-|
|富山県（黒部市）|ラジオ・ミュー|○|-|-|○|
|富山県（砺波市）|[エフエムとなみ](https://www.fmtonami.jp/)|-|-|○|-|
|石川県|[ラジオかなざわ](https://www.radiokanazawa.co.jp/)|-|-|○|-|
|石川県|[ラジオこまつ](https://www.radio-komatsu-new.com/)|-|-|○|-|
|石川県|[ラジオななお](https://www.radionanao.co.jp/)|-|-|○|-|
|石川県（野々市市）|FM N1|○|-|-|-|
|福井県（敦賀市）|敦賀FM|○|-|-|-|
|山梨県|[FMふじやま](http://fujiyama776.jp/)|-|-|○|-|
|山梨県|[FM八ヶ岳](https://yatsugatake.ne.jp/)|-|-|○|-|
|山梨県|[エフエム ふじごこ](https://www.fm2255.jp/)|-|-|○|-|
|山梨県|[エフエム甲府](http://www.fm-kofu.co.jp/)|-|-|○|-|
|長野県|[FM軽井沢](https://fm-karuizawa.co.jp/)|-|-|○|-|
|長野県|[LCV FM](https://lcvfm769.jp/)|-|-|○|-|
|長野県|[エフエムあづみの](https://www.azuminofm.co.jp/)|-|-|○|-|
|長野県|[高ボッチ高原FM](https://fm894.jp/)|-|-|○|-|
|長野県（松本市）|FMまつもと|-|○|-|-|
|長野県（飯田市）|いいだFM|-|○|-|-|
|長野県（諏訪市）|LCV-FM769|-|○|-|-|
|長野県（佐久市）|fmさくだいら|-|○|-|-|
|長野県（東御市）|はれラジ|-|○|-|-|
|長野県（安曇野市）|[あづみ野FM](http://www.azuminofm.co.jp/)|-|-|-|○|
|岐阜県|[FMPiPi](https://fmpipi.co.jp/)|-|-|○|-|
|岐阜県（岐阜市）|[FMわっち](https://www.fm-watch.jp/)|-|-|○|-|
|岐阜県（高山市）|[Hits FM](http://www.hidanet.ne.jp/~hitsfm/)|-|-|○|-|
|岐阜県（可児市）|FMらら76.8|-|○|-|-|
|静岡県|[FM Haro!](https://www.fmharo.co.jp/)|-|-|○|-|
|静岡県|[FM-Hi!](http://www.fmhi.co.jp/)|-|-|○|-|
|静岡県|[FMいずのくに](https://www.fmizunokuni.jp/)|-|-|○|-|
|静岡県|[エフエムなぎさステーション](https://www.fmito.com/)|-|-|○|-|
|静岡県|[マリンパル](https://mrn-pal.com/)|-|-|○|-|
|静岡県（沼津市）|[COAST-FM76.7MH z](http://www.coast-fm.com/)|-|-|○|-|
|静岡県（熱海市）|[Ciao!](http://www.ciao796.com/)|-|-|○|-|
|静岡県（三島市）|[ボイスキュー](http://777fm.com/)|-|-|○|-|
|静岡県（島田市）|[g-sky76.5](http://www.gsky765.jp/)|-|-|○|-|
|静岡県（富士市）|[Radio-f](https://radio-f.jp)|-|-|○|-|
|静岡県（御殿場市）|[富士山GOGOFM](https://www.863.fm/)|-|-|○|-|
|静岡県（伊豆市）|[FM ISみらいずステーション](https://fmis.jp/)|-|-|○|-|
|愛知県|[RADIO SANQ](http://845.fm/)|-|-|○|-|
|愛知県|[エフエム ななみ](https://www.clovernet.co.jp/nanami/)|-|-|○|-|
|愛知県（名古屋市）|Heart FM|○|-|-|-|
|愛知県（名古屋市）|名古屋市防災ラジオ|-|○|-|-|
|愛知県（豊橋市）|TEES-843FM|-|○|-|-|
|愛知県（岡崎市）|[FMおかざき](http://www.fmokazaki.jp/)|-|-|-|○|
|愛知県（岡崎市）|[エフエムEGAO](http://fm-egao.jp/)|○|-|-|○|
|愛知県（一宮市）|[i-wave](https://iwave765.com/)|-|-|○|-|
|愛知県（刈谷市）|KATCH&Pitch 地域情報|-|○|-|-|
|愛知県（豊田市）|ラジオ・ラブィート|-|○|-|-|
|愛知県（犬山市）|[United North](https://842fm.jp/)|-|-|○|-|
|愛知県（東海市）|メディアスFM|-|○|-|-|
|三重県|[Suzuka Voice FM 78.3MHz](https://suzuka-voice.fm/)|-|-|○|-|
|三重県（四日市市）|CTY-FM|-|○|-|-|
|三重県（いなべ市）|[いなべエフエム](https://fm861.com/)|-|-|○|-|
|滋賀県（大津市）|FMおおつ|-|○|-|-|
|滋賀県（彦根市）|78.2エフエムひこね|-|○|-|-|
|滋賀県（草津市）|[えふえむ草津](https://fm785.jp/)|-|-|○|-|
|滋賀県（東近江市）|ラジオスイート|○|-|-|-|
|京都府|[FM845](https://www.fm-845.com/)|-|-|○|-|
|京都府|FMおとくに|○|-|-|○|
|京都府|[FMまいづる](https://775maizuru.jp/)|-|-|○|-|
|京都府（京都市）|FM87.0 RADIO MIX KYOTO|○|-|-|-|
|京都府（京都市）|[RADIO MIX KYOTO](http://radiomix.kyoto/)|-|-|-|○|
|京都府（京都市）|[京都三条ラジオカフェ](http://radiocafe.jp/)|○|-|-|○|
|京都府（福知山市）|[FM丹波](http://fukuchiyama.fm-tanba.jp/)|-|-|-|○|
|京都府（綾部市）|[FMいかる](http://fmikaru.jp/)|-|-|○|-|
|京都府（宇治市）|[FMうじ](https://www.fmuji.com/)|-|-|○|-|
|京都府（京丹後市）|FMたんご|○|-|-|○|
|大阪府|[ウメダFM Be Happy!789](https://www.be-happy789.com/)|-|-|○|-|
|大阪府（大阪市）|YES-fm|-|○|-|-|
|大阪府（吹田市）|[FM千里](http://www.senri-fm.jp/)|-|-|○|-|
|大阪府（泉大津市）|FMいずみおおつ|-|○|-|-|
|大阪府（八尾市）|[FMちゃお](http://792.jp/)|-|-|○|-|
|大阪府（箕面市）|[タッキー816みのおエフエム](https://fm.minoh.net/)|-|-|○|-|
|兵庫県|[805たんば](http://805.tanba.info/)|-|-|○|○|
|兵庫県|[エフエムみっきぃ](http://www.fm-miki.jp/)|-|-|○|-|
|兵庫県（神戸市）|[FM MOOV KOBE](http://www.fm-moov.com/)|-|-|-|○|
|兵庫県（神戸市）|[エフエムわいわい](http://tcc117.jp/fmyy/)|-|-|-|○|
|兵庫県（姫路市）|[FM GENKI](https://fmgenki.jp/)|-|-|○|-|
|兵庫県（西宮市）|[さくらFM](https://sakura-fm.co.jp/)|-|-|○|-|
|兵庫県（伊丹市）|[エフエムいたみ](https://www.itami.fm/)|-|-|○|-|
|兵庫県（豊岡市）|FM ジャングル|○|-|-|-|
|兵庫県（豊岡市）|[FMジャングル](http://www.764.fm/)|-|-|-|○|
|兵庫県（加古川市）|[BAN-BANラジオ](http://www.banban.jp/radio/)|○|-|-|○|
|兵庫県（宝塚市）|[ハミングFM宝塚](http://835.jp/)|-|-|○|-|
|奈良県|[FM五條](http://shousuien.or.jp/fm_gojo/)|-|-|○|-|
|奈良県|[エフエムハイホー](http://www.fm814.co.jp/)|-|-|○|-|
|奈良県（奈良市）|[なら どっと FM](http://narafm.jp/)|-|-|○|-|
|奈良県（大和市）|[FMヤマト](n/a)|-|○|-|-|
|和歌山県|[FM TANABE](https://www.fm885.jp/index.php)|-|-|○|-|
|和歌山県|[FMビーチステーション](https://www.fm764.com/)|-|-|○|-|
|和歌山県（和歌山市）|[バナナエフエム](https://877.fm/)|-|-|○|-|
|和歌山県（橋本市）|[FMはしもと](http://816.fm/)|-|-|○|○|
|鳥取県（鳥取市）|[RADIO BIRD](http://www.radiobird.net/)|-|-|○|-|
|鳥取県（米子市）|[DARAZ FM](http://www.darazfm.com/)|○|-|-|○|
|岡山県（岡山市）|[レディオ モモ](http://www.fm790.co.jp/)|-|-|○|-|
|岡山県（倉敷市）|[FMくらしき](http://www.fmkurashiki.com/)|-|-|○|-|
|岡山県（笠岡市）|ゆめウェーブ|-|○|-|-|
|広島県|[FM東広島](http://fmhigashi.jp/)|-|-|○|-|
|広島県|[エフエムおのみち](http://www.fmo.co.jp/)|-|-|○|-|
|広島県（広島市）|[FMちゅーピー](https://chupea.fm/)|-|-|○|-|
|広島県（三原市）|[FOR LIFE RADIO](https://www.fm-mihara.jp/index.html)|-|-|○|-|
|広島県（福山市）|[FMふくやま](https://fm777.co.jp/)|-|-|○|-|
|広島県（廿日市市）|[FMはつかいち](https://761.jp/)|-|-|○|-|
|山口県|[COME ON ! FM](https://www.c-fm.co.jp/index.php)|-|-|○|-|
|山口県（防府市）|FMわっしょい|-|○|-|-|
|山口県（光市）|[しゅうなんFM](https://www.fms784.co.jp/index.php)|-|-|○|-|
|山口県（山陽小野田市）|FMスマイルウェ〜ブ|-|○|-|-|
|徳島県（徳島市）|[FMびざん](http://www.bfm.jp/)|○|-|-|○|
|香川県（高松市）|FM815(高松)|○|-|-|-|
|香川県（高松市）|[FM高松](http://www.fm815.com/)|-|-|-|○|
|香川県（坂出市）|[FM SUN](http://www.kbn.ne.jp/fm/)|○|-|-|○|
|愛媛県（今治市）|[FMラヂオバリバリ](http://www.baribari789.com/)|-|-|○|-|
|愛媛県（宇和島市）|[FMがいや](http://www.gaiya769.jp/)|-|-|○|-|
|愛媛県（新居浜市）|[Hello! NEW 新居浜 FM](http://www.hello78.jp/)|-|-|○|-|
|福岡県（北九州市）|[AIR STATION HIBIKI](http://www.hibiki882.jp/)|○|-|-|○|
|福岡県（北九州市）|FM KITAQ|-|○|-|-|
|福岡県（福岡市）|COMI×TEN|○|-|-|-|
|福岡県（福岡市）|[コミュニティラジオ天神](http://comiten.jp/)|-|-|-|○|
|福岡県（大牟田市）|FMたんと|-|○|-|-|
|福岡県（久留米市）|[Dreams FM](https://www.dreamsfm.co.jp/)|-|-|○|-|
|福岡県（直方市）|チョクラジ|○|-|-|-|
|福岡県（八女市）|[FM八女](https://www.fmyame.jp/)|-|-|○|-|
|福岡県（築上町）|[スターコーンFM](http://www.starcornfm.com/)|-|-|-|○|
|佐賀県（佐賀市）|えびすFM|-|○|-|-|
|佐賀県（唐津市）|[FMからつ](http://www.fmkaratsu.com/)|-|-|○|-|
|長崎県（佐世保市）|FMさせぼ|-|○|-|-|
|長崎県（島原市）|[FMしまばら](http://www.shimabara.fm/)|-|○|-|○|
|長崎県（諫早市）|エフエム諫早|-|○|-|-|
|長崎県（南島原市）|FMひまわり|-|○|-|-|
|熊本県（熊本市）|[FM791](http://fm791.jp/)|-|-|○|-|
|熊本県（八代市）|[Kappa FM](http://www.kappafm.com/)|-|-|○|-|
|熊本県（天草市）|みつばちラジオ|-|○|-|-|
|熊本県（御船町）|御船災害FM|-|○|-|-|
|熊本県（益城町）|益城さいがいFM|-|○|-|-|
|大分県|[ゆふいんラヂオ局](http://874.fm/)|-|-|○|-|
|大分県（中津市）|[NOASFM](https://789.fm/)|-|-|○|-|
|宮崎県（宮崎市）|サンシャインFM|-|○|-|-|
|宮崎県（都城市）|シティエフエム都城|-|○|-|-|
|宮崎県（延岡市）|[FMのべおか](http://fmnobeoka.jp/)|○|-|-|○|
|宮崎県（日向市）|FMひゅうが|-|○|-|-|
|鹿児島県（鹿児島市）|[FMぎんが](http://fm786.jp/)|-|○|-|○|
|鹿児島県（鹿児島市）|フレンズFM|-|○|-|-|
|鹿児島県（鹿屋市）|FMかのや|-|○|-|-|
|鹿児島県（薩摩川内市）|FMさつませんだい|-|○|-|-|
|鹿児島県（霧島市）|FMきりしま|-|○|-|-|
|鹿児島県（奄美市）|[あまみFM](http://www.npo-d.org)|-|-|-|○|
|鹿児島県（奄美市）|あまみエフエム|○|-|-|-|
|鹿児島県（瀬戸内町）|せとラジ|○|-|-|-|
|鹿児島県（龍郷町）|エフエムたつごう|○|-|-|-|
|沖縄県（那覇市）|[FMレキオ](http://www.fmlequio.com/)|-|○|-|○|
|沖縄県（那覇市）|fm那覇|○|-|-|○|
|沖縄県（宜野湾市）|FMぎのわん|○|-|-|○|
|沖縄県（宜野湾市）|ぎのわんシティFM|○|-|-|○|
|沖縄県（石垣市）|FMいしがきサンサンラジオ|○|-|-|-|
|沖縄県（浦添市）|[FM21](http://www.fm21.net/)|-|○|-|○|
|沖縄県（名護市）|FMやんばる|○|-|-|○|
|沖縄県（沖縄市）|オキラジ|○|-|-|○|
|沖縄県（豊見城市）|FMとよみ|○|-|-|○|
|沖縄県（うるま市）|FMうるま|○|○|-|○|
|沖縄県（宮古島市）|FMみやこ|-|○|-|-|
|沖縄県（南城市）|[FMなんじょう](http://www.fm-nanjo.net/)|-|-|-|○|
|沖縄県（本部町）|[FMもとぶ](http://www.motob.net/)|-|○|-|○|
|沖縄県（北谷町）|FMニライ|○|-|-|-|
|沖縄県（与那原町）|[FMよなばる](http://www.fm-yonabaru.site/)|○|-|-|○|
|沖縄県（久米島町）|[FMくめじま](http://fmkumejima.com/)|-|○|-|○|
