# はじめに — この教科書の歩き方

## 目的

この教科書は、フロントエンドエンジニアがAWS（Amazon Web Services。Amazon社が提供するクラウドサービス群の総称）を基礎から理解するための入門資料です。

AWSの学習でつまずきやすいのは、「EC2とは」「VPCとは」というサービス名の説明を単独で覚えようとしてしまうことです。サービス名を暗記しても、それらがどう組み合わさってひとつのWebサイトを動かしているのかが見えないままでは、実務でもAWS認定試験でも応用が利きません。

この教科書は逆の順序を取ります。「ブラウザにURLを入力してから画面が表示されるまでに、データがどこを通っているのか」という一本の道筋を先に見せ、その道筋上に登場する部品としてEC2・VPC・S3・CloudFrontなどを順番に説明していきます。読み終えたときには、AWSのサービス名を丸暗記した状態ではなく、「Webサイトを構成する部品と、部品同士の関係」を自分の言葉で説明できる状態を目指します。

## 対象読者

この教科書は、次のような方を想定しています。

- HTML / CSS / JavaScript / TypeScript は理解している
- Astro / Next.js などのフレームワークを使った経験がある
- Netlify / Vercel などへのデプロイ経験がある
- GitHubは日常的に使える
- サーバー・ネットワーク・インフラについては初心者
- 将来的にフルスタックエンジニアを目指している、またはAWS認定資格（AWS Certified Solutions Architect - Associate。以下SAA）の取得を検討している

つまり「フロントエンドは書けるが、その裏側で何が起きているかは分からない」という方に向けた内容です。

## 読み方

各章は次の順番で構成されています。

1. なぜこれが必要なのか（困りごとから入る）
2. 中学生にもわかる説明
3. 身近なたとえ
4. 正式な技術的説明
5. AWSでの具体例
6. フロントエンド開発との関係（Netlify / Vercel / Astro / Next.jsとの対比）
7. よくある勘違い
8. 覚えるべきポイント

さらに各章の末尾に、SAA試験でどう問われるかという補足を簡潔に添えています。資格取得を考えていない方は読み飛ばしても構いません。

第1章から第15章までは、Webサイトへのアクセスを外側（インターネット）から内側（サーバーやデータベース）へたどる一本のストーリーになっています。順番に読み進めることを推奨しますが、用語を調べたいだけの場合は目次から該当章に飛んでも読めるように、各章で専門用語の初出説明を省略していません。

## 完成予想図

この教科書のゴールは、次の2枚の図を自分で説明できるようになることです。まず、この2枚を先に見ておきましょう。

**図A: 静的サイト構成図**（Astroなどでビルドしたファイルだけを配信する構成）

```text
        User (Browser)
              │
              ▼
         Route 53   (DNS: example.com ► CloudFront)
              │
              ▼
        CloudFront   (CDN / HTTPS terminate / Cache)
              │
              ▼
            S3       (dist/ : HTML, CSS, JS, images)
```

**図B: サーバーアプリ構成図**（プログラムを常時動かして応答を作る構成）

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

図Aは、Netlify/Vercelに静的サイトをデプロイするときに近い構成です。図Bは、常時稼働するサーバーとデータベースが必要なアプリケーション向けの構成です。この2つの違いと、それぞれに登場する部品の役割を説明できることが、この教科書のゴールです。

## たとえ話の統一台帳

この教科書では、AWSの世界観を「**国の中に、自分の土地を借りて、建物を建てる**」というたとえで一貫させています。章によって違うたとえを使うと混乱するため、以下の対応表を統一して使用します。同じ対象に別のたとえが出てきた場合は誤りです。

| 対象 | たとえ | 補足 |
|---|---|---|
| クラウド全般 | 電気（発電所を自分で作らない） | 第1章の導入専用 |
| AWS | 巨大な国・都市 | リージョン = その国の都市 |
| リージョン | 都市 | 東京・大阪・バージニアなど |
| VPC | 自分専用に借りた土地・敷地 | 塀で囲われている |
| Subnet | 敷地内の区画 | 表の区画 / 奥の区画 |
| Public Subnet | 表の区画（道路に面している） | 来客が入れる |
| Private Subnet | 奥の区画（道路に面していない） | 関係者以外立ち入り禁止 |
| Internet Gateway | 敷地の正門 | 門を建てただけでは道は通っていない |
| Route Table | カーナビ / 道路標識 | 「この宛先はあの門へ」 |
| NAT Gateway | 通用口（中から外へは出られるが、外からは入れない） | 出前を頼むイメージ |
| Security Group | 建物の入口に立つ門番 | 入館証チェック。名簿で入館のみ確認 |
| EC2 | 敷地に建てた建物（働く人がいる事務所） | 「動かす場所」 |
| ALB | 受付・案内係 | 空いている窓口へ案内 |
| Auto Scaling | 混雑に応じてスタッフを増減する店長 | |
| RDS | 金庫室・書庫（奥の区画にある） | 専門の管理人付き |
| S3 | 巨大な倉庫・ロッカー | 「置く場所」 |
| CloudFront | 各地の前線倉庫・コンビニ | 近くの店から受け取れば早い |
| IPアドレス | 住所（番地） | |
| ドメイン | 店の名前 | |
| DNS | 電話帳 / 住所録 | |
| Route 53 | AWSが運営する住所録 | |
| HTTPS証明書 | 身分証明書 | 第12章でのみ軽く触れる |

なお、EC2を「倉庫」と呼んだり、S3を「サーバー」と呼んだりはしません。Security Groupは「門」ではなく必ず「門番」と呼びます（「門」はInternet Gatewayのたとえです）。VPCも「建物」ではなく「土地」です。

## 目次

| 章 | ファイル | 内容 |
|---|---|---|
| 00 | [00-introduction.md](./00-introduction.md) | はじめに（本章） |
| 01 | [01-what-is-aws.md](./01-what-is-aws.md) | AWSとは何か |
| 02 | [02-ec2.md](./02-ec2.md) | EC2 |
| 03 | [03-ip-dns-domain.md](./03-ip-dns-domain.md) | IPアドレス・ドメイン・DNS |
| 04 | [04-route53.md](./04-route53.md) | Route 53 |
| 05 | [05-vpc-subnet.md](./05-vpc-subnet.md) | VPCとSubnet |
| 06 | [06-igw-routetable.md](./06-igw-routetable.md) | Internet GatewayとRoute Table |
| 07 | [07-nat-gateway.md](./07-nat-gateway.md) | NAT Gateway |
| 08 | [08-security-group.md](./08-security-group.md) | Security Group |
| 09 | [09-alb-autoscaling.md](./09-alb-autoscaling.md) | ALBとAuto Scaling |
| 10 | [10-rds.md](./10-rds.md) | RDS |
| 11 | [11-s3-ssg.md](./11-s3-ssg.md) | S3とSSG |
| 12 | [12-cloudfront.md](./12-cloudfront.md) | CloudFront |
| 13 | [13-architecture-static.md](./13-architecture-static.md) | 組み立て1: 静的サイトのAWS構成 |
| 14 | [14-architecture-server.md](./14-architecture-server.md) | 組み立て2: サーバーアプリのAWS構成 |
| 15 | [15-vs-netlify-vercel.md](./15-vs-netlify-vercel.md) | Netlify / Vercelとの違い |
| 16 | [16-big-picture.md](./16-big-picture.md) | 頭の中に持っておくAWS全体図 |
| 17 | [17-next-roadmap.md](./17-next-roadmap.md) | 次に学ぶことのロードマップ |

---

**次の章**: [第1章 AWSとは何か](./01-what-is-aws.md) — なぜ自分でサーバーを買わなくてよくなったのか、という問いから旅を始めます。
