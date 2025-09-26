from google import genai
from ...core.config import settings
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
            self.client = genai.Client(api_key=settings.google_api_key)
            logger.info("SakkaAgent (Writer) initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize SakkaAgent: {e}")
            raise

    async def write_howa(self, theme: str, topic: str, sutra_data: Dict[str, Any], audiences: List[str]) -> str:
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

## 3. 対象者
{audiences}

## 4. 引用する経典
- **一節**: {sutra_data.get('quote', 'N/A')}
- **出典**: {sutra_data.get('source', 'N/A')}
- **解説**: {sutra_data.get('explanation', 'N/A')}

# 執筆指示
1.  **形式**: 厳密なJSON形式のみを出力してください。説明や前置きは不要です。
## 出力JSONの構造
{{
  "title": "法話のタイトル（テーマと対象者を反映）",
  "introduction": "聴衆の心を引き込む、物語の始まり（時事ネタや身近な話題を含む）",
  "problem_statement": "導入から仏教のテーマへと繋ぐ、具体的な問題提起",
  "sutra_quote": {{
    "text": "テーマに沿った経典からの引用文",
    "source": "出典（例: 法句経 第十七章『忿怒品』）"
  }},
  "modern_example": "教えを現代のシーン（特に対象者に合わせて）で解説する、具体的な例え話",
  "conclusion": "聴衆が持ち帰れる、物語の締めくくりと実践のための具体的なヒント"
}}
さあ、あなたの筆で、現代人の心に安らぎを与える法話を生み出してください。
"""

        logger.info("Generating final howa text...")
        try:
            response = await self.client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            final_text = response.text.strip()
            logger.info("Successfully generated final howa text.")
            #print(final_text)  # デバッグ用に生成された法話を出力
            return final_text
        except Exception as e:
            logger.error(f"Failed to generate final howa text: {e}")
            return "申し訳ありません。法話の生成中にエラーが発生しました。"
