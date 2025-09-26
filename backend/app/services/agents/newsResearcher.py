import google.generativeai as genai
from google.generativeai import protos
from typing import List, Dict, Any, Optional
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
                'gemini-2.5-flash',
                tools=[google_search_tool]
            )
            logger.info("YugyosoAgent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize YugyosoAgent: {e}")
            raise

    async def search_current_topics(
        self, 
        base_prompt: str, 
        sutra_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        司令塔から与えられた基本プロンプトと、オプションの経典データに基づき
        時事ニュースを調査し、結果を箇条書きリストで返す。
        """
        final_prompt = base_prompt
        
        # もし経典データがあれば、それを参考情報としてプロンプトに追記する
        if sutra_data:
            context_section = f"""
# 参考にする仏教の教え
以下の経典の一節は、今回のテーマについて語っています。
この教えが示すような状況や感情、出来事を現代社会の中から探してください。

- **経典からの引用**: {sutra_data.get('quote', 'N/A')}
- **出典**: {sutra_data.get('source', 'N/A')}
- **その解説**: {sutra_data.get('explanation', 'N/A')}
"""
            # 基本プロンプトに、このコンテキスト情報を組み込む
            final_prompt = f"{context_section}\n\n{base_prompt}"

        logger.debug("YugyosoAgent received a search request. Final prompt:\n%s", final_prompt)
        try:
            response = await self.model.generate_content_async(final_prompt)
            
            # レスポンスを箇条書きのリストに分割
            topics = [line.strip().lstrip('- ').strip() for line in response.text.strip().split('\n') if line.strip()]
            
            logger.info(f"YugyosoAgent found {len(topics)} topics.")
            return topics
        except Exception as e:
            logger.error(f"Error during topic search: {e}")
            return [] # エラー時は空のリストを返す
