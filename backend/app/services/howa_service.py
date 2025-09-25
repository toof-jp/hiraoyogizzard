from typing import List, Dict, Any
import random
import asyncio
from ..models.howa import GenerateHowaRequest, HowaResponse
from .gemini_service import GeminiService
from .agents.queryMaker import QueryMaker
from .agents.newsResearcher import NewsResearcher
from .agents.sutraResearcher import SutraResearcher
from .agents.writer import Writer
from .agents.reviewer import Reviewer
from .agents.kyotenFinder import KyotenFinder, KyotenSearchRequest, KyotenSearchResponse
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
        #self.sutra_researcher = SutraResearcher()
        self.kyoten_finder = KyotenFinder()
        self.writer = Writer()
        self.reviewer = Reviewer()
        
    
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
        logger.info(f"Executing interactive step: {step} for theme: {theme}")

        if step == "create_prompts":
            # このステップはシンプルに戻る。経典データは不要。
            news_prompt = await self.query_maker.create_current_topics_search_prompt(theme)
            sutra_prompt = await self.query_maker.create_sutra_search_prompt(theme)
            return {
                "news_search_prompt": news_prompt,
                "sutra_search_prompt": sutra_prompt
            }

        elif step == "run_sutra_search":
            # ステップ3: 蔵主エージェントが経典を検索する (将来の実装)
            sutra_prompt = context.get("sutra_search_prompt")
            if not sutra_prompt:
                # 先にプロンプトを生成する必要があることを示唆するエラー
                raise ValueError("Context must contain 'sutra_search_prompt'. Please run 'create_prompts' step first.")

            search_request = KyotenSearchRequest(theme=sutra_prompt)
            response: KyotenSearchResponse = await self.kyoten_finder.search_sutra_placeholder(search_request)
            found_quote_dict = {
                "quote": response.sutra_text,
                "source": response.source,
                "explanation": response.context
            }
            return {"found_quote": found_quote_dict}

        elif step == "run_news_search":
            # ステップ2: 遊行僧エージェントが時事ネタを検索する
            news_prompt = context.get("news_search_prompt")
            if not news_prompt:
                raise ValueError("Context must contain 'news_search_prompt'. Please run 'create_prompts' step first.")
            
            # コンテキストから経典データを取得（なくても良い）
            sutra_data = context.get("found_quote")
            
            # 遊行僧エージェントに、基本プロンプトと経典データの両方を渡す
            topics = await self.news_researcher.search_current_topics(news_prompt, sutra_data)
            return {"found_topics": topics}
        elif step == "write_howa":
            sutra_data = context.get("found_quote")
            topics = context.get("found_topics")
            
            # --- ★デバッグ用のprint文を追加 ---
            print(f"\n[DEBUG] 'write_howa' step received topics. Type: {type(topics)}, Content: {topics}\n")

            if not sutra_data or not topics:
                raise ValueError("Context must contain 'found_quote' and 'found_topics'.")

            # 見つかった各トピックに対して、並行して法話を生成します
            howa_tasks = []
            for topic in topics:
                # ★ writer.write_howa には、単一の文字列(topic)を渡します
                task = self.writer.write_howa(theme, topic, sutra_data)
                howa_tasks.append(task)
            
            # 全ての法話執筆タスクが完了するのを待ちます
            howa_candidates = await asyncio.gather(*howa_tasks)
            
            # 生成された法話候補のリストを返します
            return {"final_howa": howa_candidates}
        elif step == "evaluate_howa":
            # ステップ5: 評価エージェントが法話候補を評価し、最良のものを選ぶ
            howa_candidates = context.get("howa_candidates")
            if not howa_candidates:
                raise ValueError("Context must contain 'howa_candidates'. Please provide multiple howa drafts to evaluate.")
            
            best_howa = await self.reviewer.evaluate_and_select(theme, howa_candidates)
            return {"best_howa": best_howa}
            
        else:
            raise ValueError(f"Unknown step: {step}")
