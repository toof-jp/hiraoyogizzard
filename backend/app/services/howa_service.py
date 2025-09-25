from typing import List, Dict, Any
import random
from ..models.howa import GenerateHowaRequest, HowaResponse
from .gemini_service import GeminiService
from .agents.queryMaker import QueryMaker
from .agents.newsResearcher import NewsResearcher
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class HowaGenerationService:
    """法話生成サービス"""
    
    def __init__(self):
        # Geminiサービスを初期化
        self.gemini_service = GeminiService()
        self.query_maker = QueryMaker()
        self.news_researcher = NewsResearcher()
    
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
    
    async def execute_interactive_step(self, step: str, theme: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """【テスト用】指定された対話ステップを実行する"""
        logger.info(f"Executing interactive step: {step} for theme: {theme}")

        if step == "create_prompts":
            # ステップ1: 方便エージェントがプロンプトを生成する
            news_prompt = await self.query_maker.create_current_topics_search_prompt(theme)
            sutra_prompt = await self.query_maker.create_sutra_search_prompt(theme)
            return {
                "news_search_prompt": news_prompt,
                "sutra_search_prompt": sutra_prompt
            }

        elif step == "run_news_search":
            # ステップ2: 遊行僧エージェントが時事ネタを検索する
            news_prompt = context.get("news_search_prompt")
            if not news_prompt:
                raise ValueError("Context must contain 'news_search_prompt' for this step.")

            topics = await self.news_researcher.search_current_topics(news_prompt)
            return {"found_topics": topics}

        elif step == "run_sutra_search":
            # ステップ3: 蔵主エージェントが経典を検索する (将来の実装)
            return {"message": "Sutra search step is not yet implemented."}
            
        else:
            raise ValueError(f"Unknown step: {step}")
    