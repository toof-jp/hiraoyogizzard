import google.generativeai as genai
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Writer:
    """
    与えられた材料（テーマ、時事ネタ、経典）を元に、
    最終的な法話の文章を執筆する作家エージェント。
    """

    def __init__(self):
        try:
            # このエージェントは文章生成が目的なので、検索ツールは不要
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            logger.info("SakkaAgent (Writer) initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize SakkaAgent: {e}")
            raise

    async def write_howa(self, theme: str, topic: str, sutra_data: Dict[str, Any]) -> str:
        """
        テーマ、時事ネタ、経典データを組み合わせて一つの法話を生成する。
        """


        # これが最終的な法話の品質を決めるプロンプト
        prompt = f"""
あなたは、現代的で分かりやすい法話を書くのが得意な、才能ある作家（作務僧）です。
以下の材料を元に、心に響く短い法話を執筆してください。

# 材料
## 1. メインテーマ
{theme}

## 2. 参考にする時事ネタ
{topic}

## 3. 引用する経典
- **一節**: {sutra_data.get('quote', 'N/A')}
- **出典**: {sutra_data.get('source', 'N/A')}
- **解説**: {sutra_data.get('explanation', 'N/A')}

# 執筆指示
1.  **導入**: 時事ネタの中から1つか2つを選び、それを切り口として話を始めてください。
2.  **展開**: 導入で触れた現代の出来事を、経典の一節が示す仏教の教えと自然に結びつけてください。
3.  **結論**: 全体をまとめ、読者が日常生活で実践できるような、前向きなメッセージで締めくくってください。
4.  **形式**: 全体で600字程度の、親しみやすい文章にしてください。タイトルは不要です。

さあ、あなたの筆で、現代人の心に安らぎを与える法話を生み出してください。
"""

        logger.info("Generating final howa text...")
        try:
            response = await self.model.generate_content_async(prompt)
            final_text = response.text.strip()
            logger.info("Successfully generated final howa text.")
            print(final_text)  # デバッグ用に生成された法話を出力
            return final_text
        except Exception as e:
            logger.error(f"Failed to generate final howa text: {e}")
            return "申し訳ありません。法話の生成中にエラーが発生しました。"