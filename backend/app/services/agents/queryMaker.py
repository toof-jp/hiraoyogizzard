import logging
import google.generativeai as genai
from ...core.config import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class QueryMaker:
    """
    チーム全体の戦略を立て、他のエージェントへの指示（クエリ）を生成する方便エージェント。
    """

    def __init__(self):
        try:
            # このエージェントも思考するためにモデルを持つ
            #genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
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
            response = await self.model.generate_content_async(prompt)
            summarized_theme = response.text.strip()
            logger.info(f"Summarized theme: '{long_text}' -> '{summarized_theme}'")
            return summarized_theme
        except Exception as e:
            logger.error(f"Failed to summarize theme: {e}")
            # エラー時は元のテキストの先頭部分を安全に使う
            return long_text[:50]

    async def create_sutra_search_prompt(self, theme_input: str) -> str:
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
あなたは、三蔵に精通した仏教学者（蔵主）です。
以下のテーマに最も合致する仏教の経典（パーリ語仏典、漢訳仏典など）から、象徴的な一節を探し出し、提示してください。

# 検索テーマ
{core_theme}

# 指示
1.  テーマに最も関連深く、心に響く一節を選んでください。
2.  長すぎる場合は、最も重要な部分（200字以内）を抜粋してください。
3.  必ず、引用した経典の「出典（経典名と章や偈の番号など）」を明記してください。
4.  なぜその一節がテーマと関連するのか、1〜2文で簡単な解説を加えてください。

# 出力形式
厳密なJSON形式で、以下の構造に従って出力してください。説明や前置きは一切不要です。
{{
  "quote": "ここに経典からの引用文を記述",
  "source": "ここに経典名と出典を記述（例: 法句経 第1偈）",
  "explanation": "ここにテーマとの関連性の解説を記述"
}}
"""
        logger.debug(f"Created sutra search prompt for core theme: {core_theme}")
        return prompt

    async def create_current_topics_search_prompt(self, theme: str) -> str:
        """
        与えられたテーマに基づき、遊行僧エージェントが時事ネタを検索するための
        プロンプトを生成する。（将来の拡張用）
        """
        # ここに時事ネタ検索用のプロンプト生成ロジックを追加できます
        pass
    
    async def create_current_topics_search_prompt(self, theme_input: str) -> str:
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

# 指示
1.  テーマに直接関連する、興味深い、または示唆に富む出来事を5つ探してください。
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