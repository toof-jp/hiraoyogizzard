from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.router import api_router

# FastAPIアプリケーションの初期化
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの追加
app.include_router(api_router, prefix="/v1")


# ヘルスチェック用エンドポイント
@app.get("/")
async def root():
    return {
        "message": "FastAPI Backend is running",
        "version": settings.api_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,  # アプリケーションオブジェクトを直接渡す
        host=settings.host,
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        reload=False  # 開発時はFalseに設定するか、別の方法で起動
    )
