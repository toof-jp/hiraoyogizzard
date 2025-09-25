import pytest
from fastapi.testclient import TestClient
from main import app

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


def test_get_themes():
    """テーマ取得エンドポイントのテスト"""
    response = client.get("/v1/howa/themes")
    assert response.status_code == 200
    data = response.json()
    assert "themes" in data
    assert len(data["themes"]) > 0


def test_get_audiences():
    """対象者取得エンドポイントのテスト"""
    response = client.get("/v1/howa/audiences")
    assert response.status_code == 200
    data = response.json()
    assert "audiences" in data
    assert len(data["audiences"]) > 0


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