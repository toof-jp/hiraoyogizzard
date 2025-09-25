from typing import List
import random
from ..models.howa import GenerateHowaRequest, HowaResponse
from .gemini_service import GeminiService
from fastapi import HTTPException


class HowaGenerationService:
    """法話生成サービス"""
    
    def __init__(self):
        # Geminiサービスを初期化
        self.gemini_service = GeminiService()
    
    async def generate_howa(self, request: GenerateHowaRequest) -> HowaResponse:
        """
        Geminiサービスを使って法話を生成する
        """
        try:
            # Geminiサービスに処理を委譲
            response = await self.gemini_service.generate_content(request)
            return response
        except Exception as e:
            # エラーハンドリングを強化
            raise HTTPException(
                status_code=503, 
                detail=f"法話の生成に失敗しました (外部サービスエラー): {str(e)}"
            )