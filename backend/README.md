# Backend API

FastAPIを使用したバックエンドAPIサーバーです。

## セットアップ

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### サーバーの起動

```bash
# 開発サーバーの起動
python main.py

# または uvicorn を直接使用
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API ドキュメント

サーバー起動後、以下のURLでAPIドキュメントを確認できます：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## プロジェクト構造

```
backend/
├── main.py              # FastAPIアプリケーションのエントリーポイント
├── requirements.txt     # Python依存関係
├── app/                 # アプリケーションコード
│   ├── api/            # APIエンドポイント
│   ├── core/           # 設定、セキュリティ
│   ├── models/         # データモデル
│   └── services/       # ビジネスロジック
└── tests/              # テストコード
```
