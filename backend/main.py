"""FastAPI application bootstrap with Valkey-backed task processing."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from redis.asyncio import Redis
import uvicorn

from app.core.config import settings
from app.api.router import api_router
from app.services.howa_service import HowaGenerationService
from app.services.task_queue import HowaTaskQueue
from app.services.task_worker import HowaTaskWorker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise shared resources (Valkey + background worker)."""

    redis = Redis(
        host=settings.valkey_host,
        port=settings.valkey_port,
        db=settings.valkey_db,
        password=settings.valkey_password,
        decode_responses=True,
    )

    queue = HowaTaskQueue(
        redis,
        queue_name=settings.valkey_queue_name,
        task_ttl_seconds=settings.valkey_task_ttl_seconds,
    )

    worker = HowaTaskWorker(queue, HowaGenerationService)
    worker_task = asyncio.create_task(worker.start())

    app.state.valkey = redis
    app.state.howa_task_queue = queue
    app.state.howa_worker = worker
    app.state.howa_worker_task = worker_task

    try:
        yield
    finally:
        worker.stop()
        worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await worker_task
        await redis.close()


# FastAPIアプリケーションの初期化
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    lifespan=lifespan,
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
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz_check():
    return "ok"


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        reload=False,
    )
