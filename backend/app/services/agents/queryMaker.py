import logging
from google import genai
from ...core.config import settings
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class QueryMaker:
    """
    チーム全体の戦略を立て、他のエージェントへの指示（クエリ）を生成する方便エージェント。
    """

    def __init__(self):
        try:
            self.client = genai.Client(api_key=settings.google_api_key)
            logger.info("HobenAgent (Query Maker) initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize HobenAgent: {e}")
            raise

    async def _summarize_theme(self, long_text: str) -> str:
        """長い入力文から中心的なテーマを抽出する"""
        prompt = f"""
以下の文章を、法話のテーマとして適切なフレーズに要約してください。元の文章の意味を損なわないように注意してください。
十分に短い場合は、そのまま使用してください。
# 元の文章
{long_text}

# 抽出したテーマ:
"""
        try:
            response = await self.client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            summarized_theme = response.text.strip()
            logger.info(f"Summarized theme: '{long_text}' -> '{summarized_theme}'")
            return summarized_theme
        except Exception as e:
            logger.error(f"Failed to summarize theme: {e}")
            # エラー時は元のテキストの先頭部分を安全に使う
            return long_text[:50]

    async def create_sutra_search_prompt(self, theme_input: str, audiences: List[str]) -> str:
        """
        与えられたテーマに基づき、蔵主エージェントが仏教原典を検索するための
        詳細なプロンプトを生成する。
        """
        
        # 入力文が長い場合（例: 50文字以上）は、要約処理を挟む
        if len(theme_input) > 50:
            core_theme = await self._summarize_theme(theme_input)
        else:
            core_theme = theme_input

        # 要約・抽出されたクリーンなテーマを使ってプロンプトを生成
        prompt = f"""
以下のテーマに関連する経典を検索するために、キーワードを抜き出して読点で区切って出力してください。
# 検索テーマ
{core_theme}

# 対象聴衆
{"、".join(audiences) if audiences else "一般の人々"}

# 指示
1.  テーマに直接関連するキーワードを選んでください。
2.  キーワードは、できるだけ具体的で、かつ一般的な言葉を選んでください。
3.  キーワードは、読点「、」で区切って出力してください。
# 出力例
- 慈悲、無常、執着、若者、子供
"""
        logger.debug(f"Created sutra search prompt for core theme: {core_theme}")
        return prompt

    async def create_current_topics_search_prompt(self, theme_input: str, audiences: List[str]) -> str:
        """
        与えられたテーマに基づき、遊行僧エージェント（News Researcher）が
        時事ネタを検索するためのプロンプトを生成する。
        """
        # こちらも同様に、長い入力は要約する
        if len(theme_input) > 50:
            core_theme = await self._summarize_theme(theme_input)
        else:
            core_theme = theme_input

        # 要約されたクリーンなテーマを使って、時事ネタ検索用のプロンプトを生成
        prompt = f"""
あなたは、現代社会の動向に詳しいジャーナリスト（遊行僧）です。
Google検索ツールを駆使して、以下のテーマに関連する最近の具体的なニュース、社会的な出来事、または一般的な話題を調査してください。

# 調査テーマ
{core_theme}

# 対象聴衆
{"、".join(audiences) if audiences else "一般の人々"}

# 指示
1.  テーマと聴衆に直接関連する、興味深い、または示唆に富む出来事を5つ探してください。
2.  なるべく具体的に、企業名や個人名が含まれるニュースを選んでください。
3.  ゴシップや扇情的な内容ではなく、多くの人が共感できるような普遍的な側面を持つニュースを選んでください。
4.  ニュースは一年以内のものに限定してください。

# 出力形式
- 箇条書きのリスト形式で、調査結果のみを出力してください。説明や前置きは不要です。
- 例:
  - 最近の調査で、若者の間でのボランティア活動への関心が高まっていることが示された。
  - 新しいテクノロジーの登場により、人々のコミュニケーション方法が変化しつつある。
"""
        logger.debug(f"Created current topics search prompt for core theme: {core_theme}")
        return prompt
