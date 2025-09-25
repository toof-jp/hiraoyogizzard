import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.howa import HowaResponse, SutraQuote  # モデルをインポート

client = TestClient(app)


def test_root_endpoint():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "healthy"


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# 以下の2つのテストは現在の仕様にないためコメントアウト
# def test_get_themes():
#     """テーマ取得エンドポイントのテスト"""
#     response = client.get("/v1/howa/themes")
#     assert response.status_code == 200
#     data = response.json()
#     assert "themes" in data
#     assert len(data["themes"]) > 0


# def test_get_audiences():
#     """対象者取得エンドポイントのテスト"""
#     response = client.get("/v1/howa/audiences")
#     assert response.status_code == 200
#     data = response.json()
#     assert "audiences" in data
#     assert len(data["audiences"]) > 0


def test_generate_howa_success():
    """法話生成の正常ケーステスト"""
    request_data = {
        "theme": "感謝",
        "audiences": ["若者"]
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # レスポンスの必須フィールドをチェック
    required_fields = ["title", "introduction", "problem_statement", 
                      "sutra_quote", "modern_example", "conclusion"]
    for field in required_fields:
        assert field in data
    
    # sutra_quoteの構造をチェック
    assert "text" in data["sutra_quote"]
    assert "source" in data["sutra_quote"]


def test_generate_howa_success_with_mock(monkeypatch):
    """
    【モックテスト】法話生成が成功するケース
    GeminiServiceをモック化し、ダミーのレスポンスを返すように設定
    """
    # 1. 差し替え用のダミーレスポンスを定義
    dummy_response = HowaResponse(
        title="【モック】感謝の心",
        introduction="これはモックの導入です。",
        problem_statement="これはモックの問題提起です。",
        sutra_quote=SutraQuote(text="モックの経典引用", source="モック経"),
        modern_example="これはモックの現代例です。",
        conclusion="これがモックの結論です。"
    )

    # 2. GeminiService.generate_content を差し替える非同期関数を定義
    async def mock_generate_content(*args, **kwargs):
        return dummy_response

    # 3. monkeypatch を使って、実際のメソッドをダミー関数に差し替える
    monkeypatch.setattr(
        "app.services.gemini_service.GeminiService.generate_content",
        mock_generate_content
    )

    # 4. APIを呼び出す
    request_data = {"theme": "感謝", "audiences": ["若者"]}
    response = client.post("/v1/howa", json=request_data)

    # 5. 結果を検証
    assert response.status_code == 200
    assert response.json()["title"] == "【モック】感謝の心"


def test_generate_howa_fails_with_mock(monkeypatch):
    """
    【モックテスト】Gemini APIの呼び出しでエラーが発生するケース
    """
    # 1. 意図的に例外を発生させるダミー関数を定義
    async def mock_raise_exception(*args, **kwargs):
        raise ValueError("Gemini APIとの通信エラー")

    # 2. メソッドを差し替える
    monkeypatch.setattr(
        "app.services.gemini_service.GeminiService.generate_content",
        mock_raise_exception
    )

    # 3. APIを呼び出す
    request_data = {"theme": "感謝", "audiences": ["若者"]}
    response = client.post("/v1/howa", json=request_data)

    # 4. 503エラーが返ってくることを検証
    assert response.status_code == 503
    assert "法話の生成に失敗しました" in response.json()["detail"]


def test_generate_howa_invalid_request():
    """法話生成の異常ケーステスト"""
    # themeが空のケース
    request_data = {
        "theme": "",
        "audiences": ["若者"]
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 422
    
    # audiencesが空のケース
    request_data = {
        "theme": "感謝",
        "audiences": []
    }
    response = client.post("/v1/howa", json=request_data)
    assert response.status_code == 422