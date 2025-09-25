import logging
import re
import json
from typing import List
import google.generativeai as genai

logger = logging.getLogger(__name__)

class Reviewer:
    """
    生成された複数の法話候補を評価し、最も優れたものを1つ選ぶ評価エージェント。
    """

    def __init__(self):
        logger.info("Reviewer initialized with its own Gemini model instance.")
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # --- ▼▼▼ 戻り値の型ヒントを str に戻す ▼▼▼ ---
    async def evaluate_and_select(self, theme: str, howa_candidates: List[str]) -> str:
        """
        法話の候補リストから最も優れたものを選択し、その本文を返す。
        """
        if not howa_candidates:
            return "適切な法話が見つかりませんでした。"
        
        if len(howa_candidates) == 1:
            logger.info("Only one candidate available. Selecting it directly.")
            return howa_candidates[0]

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

                # --- ▼▼▼ 理由をprintで表示 ▼▼▼ ---
                print("\n--- [DEBUG] Selection Reasoning ---")
                print(reasoning)
                print("---------------------------------\n")
                # --- ▲▲▲ ここまで ▲▲▲ ---

                if isinstance(best_index, int) and 0 <= best_index - 1 < len(howa_candidates):
                    selected_howa = howa_candidates[best_index - 1]
                    logger.info(f"LLM selected candidate number {best_index}.")
                    return selected_howa # ★ 文字列だけを返す

            logger.warning(f"Could not parse JSON from LLM response: '{response_text}'. Falling back.")
            return howa_candidates[0] # ★ 文字列だけを返す

        except Exception as e:
            logger.error(f"Error during LLM-based evaluation: {e}. Falling back.")
            return howa_candidates[0] # ★ 文字列だけを返す

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