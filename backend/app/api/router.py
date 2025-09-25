from fastapi import APIRouter
from .endpoints import howa

api_router = APIRouter()

# 各エンドポイントルーターを統合
api_router.include_router(howa.router)