# フロントエンドエンジニアのためのAWS入門教科書

## この教科書について

この教科書は、フロントエンド開発の経験はあるがサーバー・ネットワーク・インフラは初めて、という方のためのAWS入門資料です。

サービス名を1つずつ暗記していく形式ではなく、「ブラウザにURLを入力してから画面が表示されるまでに、データがどこを通っているのか」という一本の道筋をたどりながら、その道筋に登場する部品としてEC2・VPC・S3・CloudFrontなどを順番に説明していきます。同時に、Netlify / Vercel が裏側で何を代行してくれていたのかも明らかにしていきます。

読み終えたときに持ってほしい感覚は1つだけです。**AWSは大量のサービス名を覚えるものではなく、Webサービスを構成する部品と、その部品同士の関係を理解するものである**、ということです。

## 対象読者

- HTML / CSS / JavaScript / TypeScript は理解している
- Astro / Next.js などのフレームワークを使った経験がある
- Netlify / Vercel などへのデプロイ経験がある
- GitHubは日常的に使える
- サーバー・ネットワーク・インフラについては初心者
- 将来的にフルスタックエンジニアを目指している、またはAWS認定資格（AWS Certified Solutions Architect - Associate。以下SAA）の取得を検討している

## 読み方

第0章から第17章まで、**順番に読み進めることを前提**に構成しています。各章は前の章で作ったものの上に次の部品を足していく形になっているため、途中から読むと「なぜこの設定が必要なのか」が見えにくくなります。

各章がどのような構成になっているか、たとえ話の統一ルール、SAA向けの補足の扱いについては、[第0章 はじめに — この教科書の歩き方](./docs/00-introduction.md)で説明しています。まずはそこから読み始めてください。

## 完成予想図

この教科書のゴールは、次の2枚の図を自分で説明できるようになることです。

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

## 目次

| 章 | タイトル |
|---|---|
| 00 | [はじめに — この教科書の歩き方](./docs/00-introduction.md) |
| 01 | [AWSとは何か — サーバーを「買う」から「借りる」へ](./docs/01-what-is-aws.md) |
| 02 | [EC2 — プログラムを「動かす」場所](./docs/02-ec2.md) |
| 03 | [IPアドレス・ドメイン・DNS — 住所と電話帳](./docs/03-ip-dns-domain.md) |
| 04 | [Route 53 — AWSの住所録](./docs/04-route53.md) |
| 05 | [VPCとSubnet — 自分専用の土地と区画](./docs/05-vpc-subnet.md) |
| 06 | [Internet GatewayとRoute Table — 正門とカーナビ](./docs/06-igw-routetable.md) |
| 07 | [NAT Gateway — 中から外へだけ出る通用口](./docs/07-nat-gateway.md) |
| 08 | [Security Group — どの通信を通すかの門番](./docs/08-security-group.md) |
| 09 | [ALBとAuto Scaling — 受付係と、人手の自動増減](./docs/09-alb-autoscaling.md) |
| 10 | [RDS — データを預かる金庫](./docs/10-rds.md) |
| 11 | [S3とSSG — ファイルを「置く」場所](./docs/11-s3-ssg.md) |
| 12 | [CloudFront — 世界中にコピーを配る前線基地](./docs/12-cloudfront.md) |
| 13 | [【組み立て1】Astro静的サイトのAWS構成](./docs/13-architecture-static.md) |
| 14 | [【組み立て2】サーバーアプリケーションのAWS構成](./docs/14-architecture-server.md) |
| 15 | [Netlify / Vercel は何を代わりにやってくれていたのか](./docs/15-vs-netlify-vercel.md) |
| 16 | [頭の中に持っておくAWS全体図](./docs/16-big-picture.md) |
| 17 | [次に学ぶことのロードマップ](./docs/17-next-roadmap.md) |

## 付録

- [APPENDIX 用語集](./APPENDIX-glossary.md) — 本書に登場する用語と、その初出章へのリンク
