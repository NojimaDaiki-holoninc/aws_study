# 第14章 【組み立て2】サーバーアプリケーションのAWS構成

> **この章でわかること**
> - Next.jsのSSRやRoute Handlersのようにサーバーで計算が必要な場合の経路を、Route 53 → ALB → EC2 → RDS の順に説明できる
> - VPC・Subnet・IGW・Route Table・NAT Gateway・Security Groupが、その経路のどこで効いているかを指し示せる
> - Security Groupを alb-sg → app-sg → db-sg と連鎖させる設計の意味を説明できる
> - 静的アセットの配信を第13章の構成と組み合わせられることを説明できる
>
> **前の章とのつながり**: [第13章](./13-architecture-static.md)では「計算しないから部品が少なくて済む」構成を見ました。この章では計算が必要になり、第5章から第10章までの部品が一斉に登場します。

## なぜこれが必要なのか

ログイン状態で表示を変えたい。フォームの内容をデータベースに保存したい。こうした要件が1つでも入った瞬間、「あらかじめ作っておいたファイルを渡すだけ」では成り立たなくなります。訪問者が来てから計算する場所が必要になるからです。

計算する場所を用意するとは、AWSでは「EC2というコンピューターを起動する」ことです。しかし1台立てて終わりにはなりません。どこに置くのか、外からどう届かせるのか、逆に触られては困るデータをどう守るのか。[第13章](./13-architecture-static.md)で1つも登場しなかったVPC・Subnet・Route Table・Security Groupが、ここで一斉に必要になります。

## まずはざっくり: 中学生にもわかる説明

前章との違いはたった1つ、「訪問者が来てから作る」かどうかです。

来てから作るなら作る人が要り、人気が出れば1人では足りないので複数人で分担します。すると「どの人に頼むか」を決める係が必要です。そして作るのに使う情報（会員名簿や注文履歴）を、誰でも触れる場所に置いておくわけにはいきません。

そこでこう配置します。訪問者が最初に会う**受付の人**は道路に面した表側に、実際に作業する人と大事な情報が入った金庫は**道路に面していない奥側**に置きます。訪問者は奥まで入れず、必ず受付を通します。ただし奥にいる人も材料の取り寄せなど外に用がある場面があるので、「中からは出られるが外からは入れない通用口」を用意しておきます。

## 身近なたとえ

奥行きのある**敷地**（VPC）を借りていると考えてください。塀で囲われ、**正門**（Internet Gateway）が1つあります。敷地は道路に面した**表の区画**（Public Subnet）と、その奥の**奥の区画**（Private Subnet）に分かれています。

表の区画には**受付・案内係**（ALB）が立ち、来客を空いている窓口に案内します。奥の区画には、実際に働く人がいる**事務所**（EC2）と、大事な書類をしまった**金庫室**（RDS）があります。奥は道路に面していないので、来客が直接たどり着くことはできません。

各建物の入口には**門番**（Security Group）が立って入館証を確認します。事務所の門番は「受付から案内されてきた人だけ」を通し、金庫室の門番は「事務所の人だけ」を通します。

表の区画には**通用口**（NAT Gateway）もあります。奥の事務所の人が資材を取り寄せたいとき、いったん表まで出てここから外に出ます。外から知らない人がこの通用口を通って入ることはできません。

## 技術的にはこういうこと

まず、この章の正本となる2枚の図を確認します。1枚目が全体の流れ（図B）です。

```text
        User (Browser)
              │
              ▼
         Route 53
              │
              ▼
            ALB        (Public Subnet)
         ┌────┴────┐
         ▼         ▼
       EC2        EC2   (Private Subnet / Auto Scaling)
         └────┬────┘
              ▼
            RDS        (Private Subnet)
```

2枚目が、その内側のネットワーク構造（図C）です。

```text
            Internet
               │
               ▼
      ┌─── Internet Gateway ───┐
      │                        │
┌─────┴────────── VPC ─────────┴─────┐
│ 10.0.0.0/16                        │
│                                    │
│  ┌─── Public Subnet 10.0.1.0/24 ─┐ │
│  │   ALB                         │ │
│  │   NAT Gateway                 │ │
│  └───────────────────────────────┘ │
│                 │                  │
│                 ▼                  │
│  ┌─── Private Subnet 10.0.2.0/24 ┐ │
│  │   EC2  (App)                  │ │
│  │   RDS  (Database)             │ │
│  └───────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

この2枚を重ねながら、リクエストを追っていきます。

**ステップ1: 名前を住所に変える（Route 53）。**
`example.com` の問い合わせにRoute 53（[第4章](./04-route53.md)）が応答します。指す先がCloudFrontからALBに変わるだけで仕組みは前章と同じで、Zone Apexから指すときは**Aレコードのエイリアス**を使います。

**ステップ2: 正門をくぐる（IGW + Route Table）。**
通信がVPCに入るには**Internet Gateway**（[第6章](./06-igw-routetable.md)）が必要ですが、アタッチしただけでは成立しません。ALBが置かれたPublic Subnetに関連付けられた**Route Table**に `0.0.0.0/0 ► igw-xxxx` の1行があり、はじめて道が通ります。この1行があるSubnetがPublic Subnetです。

**ステップ3: 受付で振り分けられる（ALB）。**
リクエストはPublic Subnetの**ALB**（[第9章](./09-alb-autoscaling.md)）に届きます。ALBの門番 `alb-sg` がインターネット（`0.0.0.0/0`）からの80番・443番を許可しているので通過します。ALBはリスナーで受けたリクエストを**ターゲットグループ**に登録されたEC2へ振り分け、**ヘルスチェック**に失敗したEC2は自動的に振り分け先から外します。

**ステップ4: 奥の区画で計算する（EC2 + Auto Scaling）。**
振り分け先の**EC2**（[第2章](./02-ec2.md)）はPrivate Subnetにあります。門番 `app-sg` はソースにIPアドレスではなく **`alb-sg` そのもの**を指定して80番を許可しているため、「ALBを経由した通信だけ」が入れます。EC2が何台に増減してもルールを書き換える必要がありません。

台数を管理するのは**Auto Scaling Group**です。ALBが増やすのではなく、Auto Scaling GroupがCPU使用率などに応じてEC2を起動・終了し、起動したEC2が自動的にターゲットグループに登録されます。これは台数を増やす**水平スケーリング**であり、1台のスペックを上げる垂直スケーリングとは別の仕組みです。

**ステップ5: データを取り出す（RDS）。**
**RDS**（[第10章](./10-rds.md)）も同じPrivate Subnetにあり、門番 `db-sg` はソースに `app-sg` を指定して3306番（PostgreSQLなら5432番）だけを許可します。

ここで**Security Groupの連鎖**が完成します。`0.0.0.0/0` → `alb-sg` → `app-sg` → `db-sg` と、外に近いほど広く、奥ほど狭くなります。インターネットからRDSへ直接届く経路はどこにもありません。

**戻りの通信。**
EC2が生成したHTMLをALB経由でブラウザに返すとき、戻り用の許可ルールは要りません。Security Group（[第8章](./08-security-group.md)）は**ステートフル**、つまり許可した通信の状態を記憶しているため、戻りは自動的に通ります。「行きと帰りの両方を許可設定する必要がある」というのは誤りです。

**外向きの通信。**
`npm install` やOSのアップデート、外部API呼び出しは、EC2の側から外へ出ていく通信です。EC2はPrivate Subnetにいるのでそのままでは出られません。ここで**NAT Gateway**（[第7章](./07-nat-gateway.md)）が効きます。Private SubnetのRoute Tableに `0.0.0.0/0 ► nat-xxxx` の行があり、通信はいったんPublic SubnetのNAT Gatewayへ向かい、そこからIGWを通って外に出ます。NAT Gatewayは送信元IPを自分のElastic IPに書き換えるため戻りは正しくEC2に返り、逆にインターネット側から新規接続を張ることは仕組み上できません。

**この図は簡略図です。**
図Cは1つのPublic Subnetと1つのPrivate Subnetだけを描いています。実際には**ALBは2つ以上のAZ（Availability Zone。同一リージョン内で電源や設備が分離された拠点）のSubnetにまたがる必要があり**、**RDSのDBサブネットグループにも2つ以上のAZにまたがるSubnetが必要**です。実運用ではこれらのSubnetがAZごとに複製されると考えてください。

**静的アセットとの組み合わせ。**
この構成でも、CSS・JavaScript・画像まで毎回EC2に取りに行かせる必要はありません。それらを[第13章](./13-architecture-static.md)の構成（CloudFront + S3）に載せ、HTMLを返す動的なリクエストだけをALBへ向ければEC2の負荷が下がります。2つの構成は排他ではなく組み合わせるものだと押さえておいてください。

## AWSでの具体例

構築は外側から内側へ順に積み上げます。

1. **VPC**（`10.0.0.0/16`）を作成し、**Internet Gateway**を作ってアタッチする。
2. **Subnet**を作成する。Public（`10.0.1.0/24`）とPrivate（`10.0.2.0/24`）を、それぞれ2つ以上のAZに用意する。
3. **Route Table**を2つ作る。Public用に `0.0.0.0/0 ► igw-xxxx` を追加してPublic Subnetに関連付ける。
4. **NAT Gateway**を**Public Subnet**に作成してElastic IPを割り当て、Private用Route Tableに `0.0.0.0/0 ► nat-xxxx` を追加する。
5. **Security Group**を3つ作る。

```text
   alb-sg   inbound  80,443  from 0.0.0.0/0
              │
              ▼
   app-sg   inbound  80      from alb-sg     ◄── source = SG ID
              │
              ▼
   db-sg    inbound  3306    from app-sg     ◄── source = SG ID
```

6. **RDS**を作成する。DBサブネットグループにPrivate Subnetを2AZ分登録し、Security Groupに `db-sg` を指定する。
7. **起動テンプレート**でEC2の設定（AMI、インスタンスタイプ、`app-sg`）を定義し、**Auto Scaling Group**を作成してPrivate Subnetと台数（例: 最小1台・希望2台・最大5台）を指定する。
8. **ALB**を作成する。Public Subnetを2AZ分指定し、Security Groupに `alb-sg`、リスナーに80番・443番、転送先にターゲットグループを設定する。ターゲットグループにヘルスチェックパス（例: `/health`）を設定し、Auto Scaling Groupに関連付ける。
9. **Route 53**でAレコードのエイリアスを作成し、ALBを指す。

## フロントエンド開発との関係

Next.jsをVercelにデプロイすると、`getServerSideProps` によるSSRも `app/api/` のRoute Handlersも、何も設定せずに動きます。しかし「どこで動いているのか」と尋ねられると、答えられないままになりがちです。

この章の構成がその答えの1つです。SSRのレンダリングもRoute Handlersのリクエスト処理も、**Private SubnetにいるEC2の上のNode.jsプロセス**が実行しています。Vercelが「サーバーレス関数」として抽象化していた実行環境を自分で用意したのがEC2であり、そこにリクエストを届ける受付がALB、混雑に応じた台数調整がAuto Scaling Groupです。

データベースも同じです。Vercel PostgresやSupabaseに接続文字列だけで繋いでいたものが、AWSでは「RDSをPrivate Subnetに置き、EC2のSecurity Groupからのみ3306番を許可する」という明示的なネットワーク設計になります。「誰が繋いでよいか」を決めているのは、自分が書いたSecurity Groupのルールです。

`npm install` の話は特に象徴的です。ビルドログでパッケージがダウンロードされるのを何度も見てきたはずですが、同じ外向き通信をPrivate SubnetのEC2で行うには、NAT Gatewayという有料の部品を明示的に置く必要があります。「勝手に外に出られる」のは、誰かがその経路を用意してくれていたからです。

## よくある勘違い

> **勘違い**: EC2はインターネットからアクセスされるのだから、Public Subnetに置かなければならない。
> **実際は**: ALBがPublic Subnetにあれば、EC2はPrivate Subnetで構いません。ユーザーはALBまでしか届かず、EC2への通信はALB経由に限定されます。

> **勘違い**: アクセスが増えるとALBがEC2の台数を増やしてくれる。
> **実際は**: 台数を管理するのはAuto Scaling Groupです。ALBは振り分けとヘルスチェックのみを担当し、両者はターゲットグループを介してつながっています。

> **勘違い**: EC2からRDSへ通信するので、EC2側のアウトバウンドとRDS側のインバウンドの両方を設定しなければならない。
> **実際は**: Security Groupはステートフルなので戻りの通信は自動的に通り、アウトバウンドはデフォルトで全許可です。設定が要るのはRDS側のインバウンドだけです。

> **勘違い**: NAT GatewayはPrivate Subnetに置くものだ。
> **実際は**: NAT Gateway自身がインターネットへ出る必要があるため、`0.0.0.0/0` がIGWを向くRoute Tableを持つ**Public Subnet**に置きます。Private SubnetのRoute Tableが、そのNAT Gatewayを向きます。

> **勘違い**: この構成にすれば、CSSや画像もEC2が高速に配信してくれる。
> **実際は**: 静的ファイルの配信はCloudFront + S3に任せるほうが速く、EC2の負荷も下がります。2つの構成は組み合わせて使うものです。

## この章で覚えるべきポイント

- [ ] 経路は Route 53 → ALB（Public Subnet）→ EC2（Private Subnet）→ RDS（Private Subnet）
- [ ] Public Subnetである条件は、Route Tableに `0.0.0.0/0 ► igw-xxxx` があって関連付けられていること
- [ ] Security Groupは `0.0.0.0/0` → `alb-sg` → `app-sg` → `db-sg` と連鎖させ、ソースにSG IDを指定する
- [ ] Security Groupはステートフルなので、戻りの通信に許可ルールは不要
- [ ] Private SubnetからのnpmインストールなどはNAT Gateway（Public Subnetに配置）経由で外へ出る
- [ ] ALBとRDSのDBサブネットグループは、いずれも2つ以上のAZにまたがるSubnetが必要

---

### Solutions Architect Associate ではこう問われる

「Webサーバーをインターネットに直接公開せずに構成したい」という要件では、**ALBをPublic Subnetに、EC2をPrivate Subnetに置き、EC2のSecurity GroupのソースにALBのSecurity Groupを指定する**構成が定番の正解です。「Private Subnetのサーバーからパッチを取得したい」が加われば**NAT Gateway（Public Subnetに配置）**が、「可用性を高めたい」が加われば**複数AZ構成**が決め手になります。ALBとAuto Scaling Groupの役割分担、Security Groupのステートフル性、NAT Gatewayの配置場所は、いずれも誤答の選択肢として繰り返し登場する論点です。

---

**次の章**: [第15章 Netlify / Vercel は何を代わりにやってくれていたのか](./15-vs-netlify-vercel.md) — ここまでで組み立てた部品の数を数えながら、隠されていたものを整理します。
