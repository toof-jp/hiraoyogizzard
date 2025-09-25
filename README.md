# hiraoyogizzard

要件定義書：法話メーカー

1. プロジェクトのコアコンセプト
   このプロジェクトは、**「AI による僧伽（サンガ）」**を創り出す試みです。個性豊かな AI エージェントたちが、ひとつのチームとして協力し、仏教の智慧と現代社会を繋ぐ、心に響く「法話」というコンテンツを創造します。シンプルさ、自律性、そして創造性を重視します。

プロジェクト名: 法話メーカー (Howa Maker)

目的: 駆け出し僧侶の創造的パートナーとなり、法話作成の負担を軽減し、質を高める。

ソリューション: テーマと聴衆を指定するだけで、AI チームが自律的に調査・執筆を行い、法話の草稿を提案する Web アプリ。

2. 機能：AI エージェントチームの共同作業
   2.1. エージェントの構成と役割
   4 人の個性的な専門エージェントが、このプロジェクトの心臓部です。

① 方便（ほうべん）エージェント : 戦略家
ユーザーの意図を深く読み解き、チーム全体の行動計画を立てる司令塔。仏教の本質を探る「問い」と、現代社会の事象を探る「キーワード」を同時に生み出す。

② 蔵主（ぞうす）エージェント : 古典学者
経典の宇宙を探求するリサーチャー。方便エージェントの「問い」を頼りに、法話の根拠となる経典の一節を見つけ出す。

③ 遊行僧（ゆぎょうそう）エージェント : ジャーナリスト
現代社会を駆け巡るフィールドワーカー。方便エージェントの「キーワード」を元に、法話にリアリティを与える時事ニュースを収集する。

④ 作家（さっか）エージェント : 物語の紡ぎ手
チームの知性を結集し、一つの物語を紡ぐアーティスト。難解な教えと無機質なニュースを、感動的な法話へと昇華させる。

2.2. 自律的な処理フロー
User Request
|
V
[方便エージェント] -> 戦略（仏教クエリ + 時事クエリ）を立案
|
+---> [蔵主エージェント] -> 経典を検索
|
+---> [遊行僧エージェント] -> 時事ニュースを検索
|
V (二つの結果を統合)
|
[作家エージェント] -> 法話として執筆
|
V
Final Output 3. システムのルール（非機能要件）
パフォーマンス: 各エージェントは、外部との通信（API コールなど）を 30 秒以内に完了させる。

信頼性（エラーハンドリング）:

ニュース検索の失敗: 致命的エラーとし、ユーザーに「時事ニュースの取得に失敗しました」と通知する。

経典検索の失敗: 致命的エラーとし、ユーザーに「経典の情報を参照できませんでした」と通知する。

AI の応答失敗: 1 度だけ再試行し、それでも失敗する場合は「AI の応答に問題が発生しました」と通知する。

4. 技術とデータ仕様
   4.1. テクノロジー
   フロントエンド: TypeScript, React

バックエンド: Python, FastAPI

生成 AI: Gemini API

データベース: Vertex AI Vector Search (経典用)

検索ツール: Google Search API (時事ネタ用)

4.2. デプロイ環境
フロントエンド: Cloudflare Pages

バックエンド: Google Cloud Run

4.3. API 仕様 (シンプル版)
API は、ただ一つの機能 POST /v1/howa を提供します。

YAML

# openapi.yaml

# ---

# 人間にも AI にも分かりやすいように、各フィールドの「意図」をコメントで記述

# ---

openapi: 3.0.3
info:
title: "法話メーカー"
description: "AI エージェントが、法話の草稿を生成するための API"
version: "1.0.0"
servers:

- url: "/v1"
  paths:
  /howa:
  post:
  summary: "法話の草稿を生成する"
  requestBody:
  required: true
  content:
  application/json:
  schema:
  $ref: '#/components/schemas/GenerateHowaRequest'
  responses:
  '200':
  description: "法話の生成に成功"
  content:
  application/json:
  schema:
  $ref: '#/components/schemas/HowaResponse'
  '500':
  description: "サーバー内部エラー"
  '503':
  description: "外部サービス利用不可"

components:
schemas:
GenerateHowaRequest:
type: object
required: [theme, audiences]
properties:
theme:
type: string
description: "法話の中心となるテーマや感情"
example: "感謝"
audiences:
type: array
description: "この法話を届けたい人々の層"
items:
type: string
enum: [子供, 若者, ビジネスパーソン, 高齢者, 指定なし]
example: ["若者"]

    HowaResponse:
      type: object
      properties:
        title:
          type: string
          description: "生成された法話の顔となるタイトル"
        introduction:
          type: string
          description: "聴衆の心を引き込む、物語の始まり（時事ネタを含む）"
        problem_statement:
          type: string
          description: "導入から仏教のテーマへと繋ぐ、問題提起"
        sutra_quote:
          type: object
          description: "法話の根拠となる、経典からの引用"
          properties:
            text:
              type: string
              description: "引用された経典の本文"
            source:
              type: string
              description: "出典（例: 法句経 第十七章『忿怒品』）"
        modern_example:
          type: string
          description: "教えを現代のシーンで解説する、具体的な例え話"
        conclusion:
          type: string
          description: "聴衆が持ち帰れる、物語の締めくくりと実践のヒント"

4.4. 経典メタデータ仕様
Vertex AI に投入する経典データには、その「住所」を示す以下のメタデータを付与します。

JSON

{
// 経典の名前（例: 法句経）
"source_title": "法句経（ダンマパダ）",

// 経典内の位置を示す階層（巻・章・品など柔軟に対応）
"source_hierarchy": {
"level_1": "第十七章『忿怒品』",
"level_2": null,
"level_3": null
},

// (任意) Web で参照できる場合の URL
"source_url": "https://example.com/sutra/dhammapada/17",

// このデータがデータベースに投入された日時
"ingestion_date": "2025-09-24T18:30:00Z"
} 5. 対象外
ユーザー認証、ログイン機能

生成された法話の保存、履歴機能
