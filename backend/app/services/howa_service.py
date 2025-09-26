from typing import List, Dict, Any
from fastapi import HTTPException
import random
import asyncio
from ..models.howa import GenerateHowaRequest, HowaResponse, SutraQuote
from .gemini_service import GeminiService
from .agents.queryMaker import QueryMaker
from .agents.newsResearcher import NewsResearcher
from .agents.writer import Writer
from .agents.reviewer import Reviewer
from .agents.kyotenFinder import KyotenFinder, KyotenSearchRequest
import logging
import json

logger = logging.getLogger(__name__)

class HowaGenerationService:
    """法話生成サービス"""
    
    def __init__(self):
        # Geminiサービスを初期化
        self.gemini_service = GeminiService()
        self.query_maker = QueryMaker()
        self.news_researcher = NewsResearcher()
        self.writer = Writer()
        self.reviewer = Reviewer()
        self.kyoten_finder = KyotenFinder()
        
    
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
    
    async def generate_full_howa(self, request: GenerateHowaRequest) -> HowaResponse:
        """
        一括生成リクエストを受け取り、経典検索から評価までの一連の処理を実行する。
        """
        theme = request.theme
        audiences = request.audiences
        context = {}
        logger.info(f"Starting full howa generation for theme: '{theme}'")

        # --- ステップを順番に実行 ---

        # 1. プロンプト生成 (内部的に実行)
        prompts_result = await self.execute_step("create_prompts", theme, audiences, context)
        context.update(prompts_result)

        # 2. 経典検索
        sutra_result = await self.execute_step("run_sutra_search", theme, audiences, context)
        context.update(sutra_result)

        # 3. ニュース検索
        news_result = await self.execute_step("run_news_search", theme, audiences, context)
        context.update(news_result)

        # 4. 法話執筆
        write_result = await self.execute_step("write_howa", theme, audiences, context)
        context["howa_candidates"] = write_result["final_howa"] # キー名を評価ステップ用に変更
        
        # 最終的なレスポンスを組み立てる
        # evaluate_and_selectは、パース済みの辞書(dict)を返す
        final_howa_data = await self.execute_step("evaluate_howa", theme, audiences, context)
        
        # 最終的なレスポンスを組み立てる
        try:
            # 辞書をそのままHowaResponseモデルに渡す
            return HowaResponse(**final_howa_data)
        except Exception as e:
            # モデルへの変換に失敗した場合 (キーが足りないなど)
            logger.error(f"Failed to create HowaResponse from final data: {e}\nData was: {final_howa_data}")
            # 安全なフォールバック
            return HowaResponse(
                title=theme,
                introduction="最終的な法話の組み立てに失敗しました。",
                problem_statement="",
                sutra_quote=SutraQuote(text="", source=""),
                modern_example="",
                conclusion=""
            )

    async def execute_step(self, step: str, theme: str, audiences: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        単一の対話ステップを実行する内部ヘルパーメソッド。
        """
        logger.debug(f"Executing step: '{step}'")

        if step == "create_prompts":
            news_search_prompt = await self.query_maker.create_current_topics_search_prompt(theme, audiences)
            sutra_search_prompt = await self.query_maker.create_sutra_search_prompt(theme, audiences)
            return {"news_search_prompt": news_search_prompt, "sutra_search_prompt": sutra_search_prompt}

        elif step == "run_sutra_search":
            search_prompt = context.get("sutra_search_prompt") or theme
            if not search_prompt:
                raise ValueError("Context must contain 'sutra_search_prompt'.")

            search_request = KyotenSearchRequest(theme=search_prompt)

            try:
                # Vertex AI Search の同期クライアントはブロッキングなので別スレッドで実行
                response = await asyncio.to_thread(self.kyoten_finder.search, search_request.theme)
            except Exception as e:
                logger.error(f"Failed to execute Vertex AI search: {e}. Falling back to placeholder response.")
                response = await self.kyoten_finder.search_sutra_placeholder(search_request)
            return {"found_quote": {
                "quote": response.sutra_text,
                "source": response.source,
                "interpretation": response.context
            }}

        elif step == "run_news_search":
            prompt = context.get("news_search_prompt", "")
            sutra_data = context.get("found_quote")
            topics = await self.news_researcher.search_current_topics(prompt, sutra_data)
            return {"found_topics": topics}

        elif step == "write_howa":
            sutra_data = context.get("found_quote")
            topics = context.get("found_topics", [])
            if not sutra_data or not topics:
                raise ValueError("Context must contain 'found_quote' and 'found_topics'.")
            
            howa_tasks = [self.writer.write_howa(theme, topic, sutra_data,audiences) for topic in topics]
            howa_candidates = await asyncio.gather(*howa_tasks)
            return {"final_howa": howa_candidates}

        elif step == "evaluate_howa":
            howa_candidates = context.get("howa_candidates", [])
            if not howa_candidates:
                raise ValueError("Context must contain 'howa_candidates'.")
            
            return await self.reviewer.evaluate_and_select(theme, howa_candidates)

            
        else:
            raise ValueError(f"Unknown step: {step}")

    async def execute_interactive_step(self, step: str, theme: str, audiences: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        [対話型API用] 単一のステップを実行し、結果を返す。
        """
        return await self.execute_step(step, theme, audiences, context)
