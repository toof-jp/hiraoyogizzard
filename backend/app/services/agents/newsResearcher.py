import google.generativeai as genai
from google.generativeai import protos
from ...core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

class NewsResearcher:
    """時事ニュースを調査する遊行僧エージェント (News Researcher)"""

    def __init__(self):
        try:
            # Google検索ツールを持たせる
            google_search_tool = protos.Tool(
                google_search_retrieval=protos.GoogleSearchRetrieval()
            )
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash-latest',
                tools=[google_search_tool]
            )
            logger.info("YugyosoAgent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize YugyosoAgent: {e}")
            raise

    async def search_current_topics(self, search_prompt: str) -> List[str]:
        """
        司令塔から与えられたプロンプト（指示書）に従って時事ニュースを調査し、
        結果を箇条書きリストで返す。
        """
        logger.debug("YugyosoAgent received a search prompt.")
        try:
            # 自分でプロンプトを作らず、渡されたものをそのまま使う
            response = await self.model.generate_content_async(search_prompt)
            
            # レスポンスを箇条書きのリストに分割
            topics = [line.strip().lstrip('- ').strip() for line in response.text.strip().split('\n') if line.strip()]
            
            logger.info(f"YugyosoAgent found {len(topics)} topics.")
            return topics
        except Exception as e:
            logger.error(f"Error during topic search: {e}")
            return [] # エラー時は空のリストを返す