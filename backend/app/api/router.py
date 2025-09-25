from fastapi import APIRouter
from .endpoints import howa

api_router = APIRouter()

# howaルーターを登録する際に、prefixとtagsを追加
api_router.include_router(
    howa.router,
    prefix="/howa",
    tags=["howa"]
)