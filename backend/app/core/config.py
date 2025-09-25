from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # API設定
    api_title: str = "FastAPI Backend"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI Backend API"
    
    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS設定
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # データベース設定（将来使用）
    database_url: Optional[str] = None
    
    # セキュリティ設定
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"


# グローバル設定インスタンス
settings = Settings()