import logging
import re
import json
from typing import List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class Reviewer:
    """
    生成された複数の法話候補を評価し、最も優れたものを1つ選ぶ評価エージェント。
    """

    def __init__(self):
        logger.info("Reviewer initialized with its own Gemini model instance.")
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    # --- ▼▼▼ 戻り値の型ヒントを Dict[str, Any] に変更 ▼▼▼ ---
    async def evaluate_and_select(self, theme: str, howa_candidates: List[str]) -> Dict[str, Any]:
        """
        法話の候補リストから最も優れたものを選択し、パースして辞書として返す。
        """
        # フォールバック用のダミーデータ
        fallback_data = {"title": theme, "introduction": "法話の評価中にエラーが発生しました。", "conclusion": ""}

        if not howa_candidates:
            return fallback_data
        
        if len(howa_candidates) == 1:
            logger.info("Only one candidate available. Selecting and parsing it directly.")
            return self._parse_howa_string(howa_candidates[0], fallback_data)

        logger.info(f"Evaluating {len(howa_candidates)} candidates using LLM...")
        prompt = self._create_evaluation_prompt(theme, howa_candidates)

        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            json_match = re.search(r'```json\n({.*?})\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                best_index = data.get("best_choice_index")
                reasoning = data.get("reasoning", "理由が提供されませんでした。")

                print("\n--- [DEBUG] Selection Reasoning ---")
                print(reasoning)
                print("---------------------------------\n")

                if isinstance(best_index, int) and 0 <= best_index - 1 < len(howa_candidates):
                    # --- ▼▼▼ 選択したJSON文字列をパースするロジックを修正 ▼▼▼ ---
                    selected_howa_str = howa_candidates[best_index - 1]
                    logger.info(f"LLM selected candidate number {best_index}.")
                    return self._parse_howa_string(selected_howa_str, fallback_data)
                    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

            logger.warning(f"Could not parse selection JSON from LLM response: '{response_text}'. Falling back.")
            return self._parse_howa_string(howa_candidates[0], fallback_data)

        except Exception as e:
            logger.error(f"Error during LLM-based evaluation: {e}. Falling back.")
            return self._parse_howa_string(howa_candidates[0], fallback_data)

    def _parse_howa_string(self, howa_str: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        法話のJSON文字列を安全にパースする内部ヘルパー。
        """
        try:
            # マークダウンのコードブロックを除去
            cleaned_str = re.sub(r'```json\s*|\s*```', '', howa_str).strip()
            return json.loads(cleaned_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse selected howa string as JSON: {e}\nString was: {howa_str}")
            return fallback_data

    def _create_evaluation_prompt(self, theme: str, candidates: List[str]) -> str:
        # このメソッドは変更なし (JSONを要求するプロンプトのまま)
        formatted_candidates = ""
        for i, candidate in enumerate(candidates):
            formatted_candidates += f"--- 法話候補 {i+1} ---\n"
            formatted_candidates += f"{candidate}\n\n"

        return f"""
あなたは経験豊富な編集者であり、仏教の教えにも精通しています。
これから、あるテーマに基づいて書かれた複数の法話の候補を提示します。
以下の評価基準に基づき、最も優れていると判断した法話を選んでください。

# 評価基準
- テーマとの整合性: 法話全体が提示されたテーマに沿っているか。
- 構成の明瞭さ: 話の流れが論理的で、聴衆が理解しやすいか。
- 心への響き: 聴衆の心に残り、行動や考え方に良い影響を与える可能性があるか。
- 独自性: ありきたりな表現に留まらず、独自の視点や深みがあるか。

# テーマ
{theme}

# 法話の候補
{formatted_candidates}

# 指示
最も優れていると判断した法話について、以下のJSON形式で回答してください。
- `best_choice_index`には選んだ法話の番号（整数）を入れてください。
- `reasoning`には、なぜその法話が最も優れていると判断したのか、評価基準に沿った具体的な理由を100文字程度で記述してください。

```json
{{
  "best_choice_index": <ここに番号>,
  "reasoning": "<ここに選定理由>"
}}
```
"""
