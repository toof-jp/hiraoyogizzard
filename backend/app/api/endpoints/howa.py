from fastapi import APIRouter, HTTPException
from typing import List

from ...models.howa import GenerateHowaRequest, HowaResponse
from ...services.howa_service import HowaGenerationService

router = APIRouter(prefix="/howa", tags=["法話生成"])

# サービスインスタンス
howa_service = HowaGenerationService()


@router.post("", response_model=HowaResponse)
async def generate_howa(request: GenerateHowaRequest):
    """
    法話を生成する
    
    - **theme**: 法話のテーマ（例: "感謝", "慈悲", "智慧"）
    - **audiences**: 対象となる聴衆の種類
    """
    try:
        response = await howa_service.generate_howa(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"法話の生成に失敗しました: {str(e)}")


@router.get("/themes")
async def get_available_themes():
    """利用可能なテーマ一覧を取得する"""
    return {
        "themes": [
            {"value": "感謝", "label": "感謝", "description": "日々の恵みに気づく心"},
            {"value": "慈悲", "label": "慈悲", "description": "他者への思いやりと慈しみ"},
            {"value": "智慧", "label": "智慧", "description": "真理を見抜く洞察力"},
            {"value": "忍耐", "label": "忍耐", "description": "困難に耐え抜く心の強さ"},
            {"value": "平安", "label": "平安", "description": "心の静寂と安らぎ"},
        ]
    }


@router.get("/audiences")
async def get_audience_types():
    """対象者の種類一覧を取得する"""
    return {
        "audiences": [
            {"value": "子供", "label": "子供", "description": "小学生から中学生まで"},
            {"value": "若者", "label": "若者", "description": "高校生から20代まで"},
            {"value": "ビジネスパーソン", "label": "ビジネスパーソン", "description": "働く大人の方々"},
            {"value": "高齢者", "label": "高齢者", "description": "60代以上の方々"},
            {"value": "指定なし", "label": "指定なし", "description": "幅広い年齢層"},
        ]
    }