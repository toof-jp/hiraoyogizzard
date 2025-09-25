import google.generativeai as genai
from ..core.config import settings
from ..models.howa import GenerateHowaRequest, HowaResponse
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini APIとの通信を担当するサービスクラス"""

    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            # モデル名を新しいものに変更
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            logger.info("Gemini Service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Service: {e}")
            raise

    def _create_prompt(self, request: GenerateHowaRequest) -> str:
        """法話生成のためのプロンプトを作成する"""
        prompt = f"""
あなたは経験豊富な僧侶です。以下の要件に従って、法話の草稿を生成してください。

# 要件
- テーマ: {request.theme}
- 対象者: {', '.join(request.audiences)}
- 出力形式: 厳密なJSON形式のみを出力してください。説明や前置きは不要です。

# 出力JSONの構造
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

# 生成開始
"""
        return prompt

    async def generate_content(self, request: GenerateHowaRequest) -> HowaResponse:
        """プロンプトを生成し、Gemini APIを呼び出して法話草稿を取得する"""
        prompt = self._create_prompt(request)
        try:
            response = await self.model.generate_content_async(prompt)
            
            # マークダウンの```json ... ```を削除
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            
            # JSON文字列をパースしてPydanticモデルに変換
            response_data = json.loads(cleaned_text)
            
            return HowaResponse(**response_data)
        except Exception as e:
            logger.error(f"Error during Gemini content generation: {e}")
            # ここでより具体的なエラーを発生させることも可能
            raise ValueError(f"Failed to generate or parse content from Gemini: {e}")