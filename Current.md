# 法話メーカー - 現在の進捗状況

## 完了済み機能

### フロントエンド（React + TypeScript）
- ✅ **基本セットアップ完了**
  - Vite + React + TypeScript環境構築済み
  - 開発サーバー起動中: http://localhost:5173

- ✅ **API型定義**
  - `frontend/src/api/generated.ts`: OpenAPI仕様から生成された型定義
  - `frontend/src/api/client.ts`: API呼び出し用のクライアント関数

- ✅ **モック環境（MSW）**
  - `frontend/src/mocks/browser.ts`: ブラウザ用MSWセットアップ
  - `frontend/src/mocks/handlers.ts`: 法話生成APIのモックハンドラー
  - `frontend/src/main.tsx`: 開発環境でのMSW自動起動

- ✅ **UIコンポーネント**
  - `frontend/src/App.tsx`: メインアプリケーション
    - 法話生成ボタン
    - ローディング状態表示
    - エラーハンドリング
    - 法話表示（タイトル、導入、問題提起、経典引用、現代例、結論）

### モックデータ内容
現在のモックレスポンス例：
- **タイトル**: "【モック】SNS疲れの心に効く「足るを知る」という智慧"
- **導入**: スマートフォン通知による心のザワつきから始まる導入
- **経典引用**: 龍安寺「知足の蹲踞」より「吾れ唯だ足ることを知るのみ」
- **現代例**: インフルエンサー投稿との比較から足るを知る教え

## 技術スタック
- **フロントエンド**: React 19.1.1, TypeScript, Vite
- **API型生成**: openapi-typescript
- **モック**: MSW (Mock Service Worker)
- **HTTPクライアント**: openapi-fetch
- **コード品質**: Biome (linting, formatting)

## 動作確認方法
1. ブラウザで http://localhost:5173 にアクセス
2. 「法話を生成する (モック)」ボタンをクリック
3. 1.5秒後にモックデータによる法話が表示される

## 次のステップ（未実装）
### バックエンド
- [ ] FastAPI環境構築
- [ ] Gemini API統合
- [ ] 4つのAIエージェント実装
  - [ ] 方便エージェント（戦略家）
  - [ ] 蔵主エージェント（古典学者）
  - [ ] 遊行僧エージェント（ジャーナリスト）
  - [ ] 作家エージェント（物語の紡ぎ手）
- [ ] Vector Search（経典データベース）
- [ ] Google Search API統合

### インフラ
- [ ] Google Cloud Run（バックエンド）
- [ ] Cloudflare Pages（フロントエンド）
- [ ] Vertex AI Vector Search

### フロントエンド追加機能
- [ ] テーマ・聴衆選択フォーム
- [ ] レスポンシブデザイン
- [ ] エラー状態の詳細表示
- [ ] 法話の印刷・共有機能

## ファイル構成
```
hiraoyogizzard/
├── README.md              # 要件定義書
├── openapi.yaml          # API仕様
├── Current.md            # 現在の進捗（このファイル）
└── frontend/
    ├── src/
    │   ├── api/
    │   │   ├── generated.ts  # 型定義
    │   │   └── client.ts     # APIクライアント
    │   ├── mocks/
    │   │   ├── browser.ts    # MSWブラウザセットアップ
    │   │   └── handlers.ts   # モックハンドラー
    │   ├── App.tsx          # メインコンポーネント
    │   └── main.tsx         # アプリエントリーポイント
    └── package.json
```