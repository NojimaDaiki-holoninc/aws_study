# APPENDIX 用語集

本書に登場する用語と、その意味、そして**その用語が最初に説明されている章**へのリンクをまとめています。読んでいる途中で用語の意味を忘れたときは、この表から初出章に戻って確認してください。

「初出章」は、その用語が本文中で初めて意味を説明されている章です。第0章の目次やたとえ話の統一台帳での言及は、初出には数えていません。

## アルファベット

| 用語 | 意味 | 初出章 |
|---|---|---|
| ACM (AWS Certificate Manager) | HTTPS用の証明書を発行・自動更新するAWSのサービス。CloudFrontで使う証明書はus-east-1で発行する | [第12章](./docs/12-cloudfront.md) |
| ALB (Application Load Balancer) | HTTP/HTTPSのリクエストを複数のEC2へ振り分けるロードバランサー | [第9章](./docs/09-alb-autoscaling.md) |
| Alias レコード | Route 53独自のレコード。Aレコードの形でCloudFront・ALB・S3を直接指せる | [第4章](./docs/04-route53.md) |
| AMI (Amazon Machine Image) | OSやプリインストールされたソフトの組み合わせを定義したEC2起動用テンプレート | [第2章](./docs/02-ec2.md) |
| Auto Scaling Group (ASG) | 条件に応じてEC2の台数を自動で増減させる仕組み。ALBのターゲットグループへ自動登録される | [第9章](./docs/09-alb-autoscaling.md) |
| AWS (Amazon Web Services) | Amazonが提供するクラウドコンピューティングサービス群の総称 | [第1章](./docs/01-what-is-aws.md) |
| A レコード | ドメイン名を直接IPアドレスに対応づけるDNSレコード | [第4章](./docs/04-route53.md) |
| CDN (Content Delivery Network) | 世界各地の拠点にコピーを置き、利用者に近い場所から配信して速度を上げる仕組み | [第12章](./docs/12-cloudfront.md) |
| CIDR (Classless Inter-Domain Routing) | `10.0.0.0/16` のように、ネットワークで使うIPアドレスの範囲を1行で表す書き方 | [第5章](./docs/05-vpc-subnet.md) |
| CloudFront | AWSのCDN。エッジロケーションにキャッシュを持ち、HTTPSの終端も行う | [第12章](./docs/12-cloudfront.md) |
| CNAME レコード | あるドメイン名を、別のドメイン名の別名として登録するDNSレコード | [第4章](./docs/04-route53.md) |
| DBサブネットグループ | RDSを配置してよいSubnetの集合を定義する設定。2つ以上のAZにまたがる必要がある | [第10章](./docs/10-rds.md) |
| DNS (Domain Name System) | ドメイン名をIPアドレスに変換する仕組み | [第3章](./docs/03-ip-dns-domain.md) |
| EC2 (Elastic Compute Cloud) | AWS上で借りられる仮想サーバー。プログラムを「動かす」場所 | [第2章](./docs/02-ec2.md) |
| Elastic IP (EIP) | 明示的に解放するまで変わらない固定のパブリックIPアドレス | [第6章](./docs/06-igw-routetable.md) |
| ENI (Elastic Network Interface) | AWSリソースが持つ仮想的なネットワークカード。Security Groupはこの単位で適用される | [第8章](./docs/08-security-group.md) |
| HTTPS の終端 | 暗号化された通信を復号し、そこから先は別の経路で扱うこと。本書ではCloudFrontが担う | [第12章](./docs/12-cloudfront.md) |
| Internet Gateway (IGW) | VPCとインターネットの間で通信を成立させるコンポーネント。VPCに1つアタッチする | [第6章](./docs/06-igw-routetable.md) |
| Invalidation（キャッシュの無効化） | CloudFrontのエッジロケーションに残った古いキャッシュを明示的に破棄する操作 | [第12章](./docs/12-cloudfront.md) |
| IPアドレス | インターネットに接続された機器を識別する番号。通信の最終的な宛先 | [第3章](./docs/03-ip-dns-domain.md) |
| Multi-AZ | RDSで、別のAZに待機系を用意し障害時に切り替える機能。有効化が必要 | [第10章](./docs/10-rds.md) |
| NAT (Network Address Translation) | パケットの送信元IPアドレスを書き換える仕組み | [第7章](./docs/07-nat-gateway.md) |
| NAT Gateway | Private Subnetからの外向き通信を中継し、戻りだけを返すマネージドサービス。Public Subnetに置く | [第7章](./docs/07-nat-gateway.md) |
| OAC (Origin Access Control) | S3バケットを非公開のまま、CloudFrontだけに読み取りを許可する推奨の接続方式 | [第12章](./docs/12-cloudfront.md) |
| RDS (Relational Database Service) | MySQLやPostgreSQLを運用するマネージドなデータベースサービス | [第10章](./docs/10-rds.md) |
| Route 53 | AWSが提供するDNSサービス | [第4章](./docs/04-route53.md) |
| Route Table | 「宛先IPアドレスの範囲」と「その宛先へ渡す先」の対応表。Subnetに関連付けて使う | [第6章](./docs/06-igw-routetable.md) |
| S3 (Simple Storage Service) | AWSのオブジェクトストレージ。ファイルを「置く」場所 | [第11章](./docs/11-s3-ssg.md) |
| Security Group | リソース（ENI）単位で適用される仮想ファイアウォール。ステートフルで許可ルールのみ | [第8章](./docs/08-security-group.md) |
| SSG（静的サイトジェネレーター） | ビルド時にHTML等を生成し、リクエスト時の計算を不要にする方式。Astroなど | [第11章](./docs/11-s3-ssg.md) |
| SSH (Secure Shell) | サーバーに安全にリモート接続するための通信方式。標準ポートは22番 | [第2章](./docs/02-ec2.md) |
| Subnet | VPCを用途別に切り分けた区画。必ず1つのAZの中に作られる | [第5章](./docs/05-vpc-subnet.md) |
| TTL (Time To Live) | キャッシュを保持しておく有効期限。DNSの変更がすぐ反映されない原因になる | [第3章](./docs/03-ip-dns-domain.md) |
| VPC (Virtual Private Cloud) | AWSアカウント内に作る、論理的に隔離された自分専用の仮想ネットワーク | [第5章](./docs/05-vpc-subnet.md) |
| Zone Apex | `www` などのサブドメインが付かないドメインの頂点（`example.com` 自体）。CNAMEを設定できない | [第4章](./docs/04-route53.md) |

## 五十音順

| 用語 | 意味 | 初出章 |
|---|---|---|
| アウトバウンド | リソースから外へ出ていく方向の通信 | [第8章](./docs/08-security-group.md) |
| アベイラビリティゾーン (AZ) | リージョン内で独立して構成されたデータセンター群の単位。Subnetは1つのAZに属する | [第5章](./docs/05-vpc-subnet.md) |
| インスタンスタイプ | EC2のCPU・メモリ性能の区分。`t3.micro` など | [第2章](./docs/02-ec2.md) |
| インバウンド | 外からリソースへ入ってくる方向の通信 | [第8章](./docs/08-security-group.md) |
| エッジロケーション | CloudFrontがコンテンツのコピーを保持する世界各地の拠点 | [第12章](./docs/12-cloudfront.md) |
| オブジェクト | S3のバケットに保存される実体（ファイル本体と付随情報） | [第11章](./docs/11-s3-ssg.md) |
| オブジェクトストレージ | ファイルをフォルダ階層ではなく「オブジェクト」としてフラットに保管する仕組み | [第11章](./docs/11-s3-ssg.md) |
| オリジン | CDNが配信する元データを持っている場所。本書ではS3バケット | [第12章](./docs/12-cloudfront.md) |
| 可用性 (Availability) | システムが停止せずに使える状態をどれだけ維持できるか | [第9章](./docs/09-alb-autoscaling.md) |
| キー (key) | S3のオブジェクトを一意に識別する名前。`images/logo.png` など | [第11章](./docs/11-s3-ssg.md) |
| キャッシュ | 一度取得したデータを一時的に保存し、次回以降そのコピーを使い回す仕組み | [第3章](./docs/03-ip-dns-domain.md) |
| キャッシュヒット / キャッシュミス | エッジロケーションのコピーで応答できた場合がヒット、オリジンまで取りに行く場合がミス | [第12章](./docs/12-cloudfront.md) |
| 権威DNSサーバー | あるドメインについて「正しい答え」を持つ、そのドメインの管理担当サーバー | [第3章](./docs/03-ip-dns-domain.md) |
| サブネットマスク | CIDRの `/16` `/24` の部分。数字が大きいほどアドレス範囲は狭くなる | [第5章](./docs/05-vpc-subnet.md) |
| 冗長化 (Redundancy) | 同じ役割の構成要素を複数用意し、一部が壊れても全体が止まらないようにすること | [第9章](./docs/09-alb-autoscaling.md) |
| 垂直スケーリング | 1台のスペックを上げて処理能力を上げる方式 | [第9章](./docs/09-alb-autoscaling.md) |
| 水平スケーリング | 台数を増やして処理能力を上げる方式。Auto Scalingはこちら | [第9章](./docs/09-alb-autoscaling.md) |
| スケーラビリティ (Scalability) | 負荷の増減に応じて処理能力を調整できる度合い | [第9章](./docs/09-alb-autoscaling.md) |
| ステートフル | 通信の状態を記憶して判断する性質。許可した通信の戻りは自動で通る | [第8章](./docs/08-security-group.md) |
| 静的ウェブサイトホスティング | S3バケットの中身を直接Webサイトとして公開する機能。本書では使わない旧来方式 | [第11章](./docs/11-s3-ssg.md) |
| ターゲットグループ | ALBの振り分け先となるEC2インスタンスの集まり | [第9章](./docs/09-alb-autoscaling.md) |
| 単一障害点 | そこが停止すると全体が止まってしまう箇所 | [第9章](./docs/09-alb-autoscaling.md) |
| デフォルトルート | Route Tableの `0.0.0.0/0`（すべての宛先）の行 | [第6章](./docs/06-igw-routetable.md) |
| ドメイン名 | `example.com` のように人間が読みやすい形式で表された名前 | [第3章](./docs/03-ip-dns-domain.md) |
| 名前解決 | ドメイン名をIPアドレスに変換する作業 | [第3章](./docs/03-ip-dns-domain.md) |
| バケット (bucket) | S3上でファイルを入れる保管場所の単位。名前はAWS全体で一意 | [第11章](./docs/11-s3-ssg.md) |
| パブリックIPアドレス | インターネット上で直接やり取りできる、世界で重複しない番号 | [第3章](./docs/03-ip-dns-domain.md) |
| ファイアウォール | 通信を検査して通すか通さないかを判断する仕組み | [第8章](./docs/08-security-group.md) |
| プライベートIPアドレス | 特定のネットワーク内でのみ通用する番号。`10.0.0.0` などの範囲 | [第3章](./docs/03-ip-dns-domain.md) |
| Private Subnet | そのようなRoute Tableが関連付けられていないSubnet | [第6章](./docs/06-igw-routetable.md) |
| プロトコル | 通信の方式。Webの通信はTCP | [第8章](./docs/08-security-group.md) |
| ヘルスチェック | ALBが各EC2に定期的に正常応答を確認する仕組み。失敗すると振り分け対象から外れる | [第9章](./docs/09-alb-autoscaling.md) |
| ポート | 1台のコンピューターで複数の通信を区別する番号。HTTPは80、HTTPSは443、SSHは22 | [第2章](./docs/02-ec2.md) |
| ホストゾーン | Route 53で、あるドメインのDNSレコードをまとめて管理する単位 | [第4章](./docs/04-route53.md) |
| Public Subnet | `0.0.0.0/0` がInternet Gatewayを向くRoute Tableが関連付けられたSubnet | [第6章](./docs/06-igw-routetable.md) |
| マネージドサービス | サーバーの用意・冗長化・パッチ適用などの運用をAWSが代行するサービス形態 | [第1章](./docs/01-what-is-aws.md) |
| リージョン | 東京・大阪・バージニアなど、地理的に離れた場所にあるAWSの拠点 | [第1章](./docs/01-what-is-aws.md) |
| リスナー | ALBがどのポート・プロトコルで通信を受け付けるかの設定 | [第9章](./docs/09-alb-autoscaling.md) |
| レイテンシー | リクエストを送ってから応答が返るまでの遅延時間 | [第12章](./docs/12-cloudfront.md) |

---

**目次に戻る**: [README](./README.md)
