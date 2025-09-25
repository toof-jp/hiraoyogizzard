import logging
from typing import List

logger = logging.getLogger(__name__)

class Reviewer:
    """
    生成された複数の法話候補を評価し、最も優れたものを1つ選ぶ評価エージェント。
    【注意】現在はダミーとして、常に最初の候補を選択します。
    """

    def __init__(self):
        logger.info("Reviewer initialized. [MODE: DUMMY]")

    async def evaluate_and_select(self, theme: str, howa_candidates: List[str]) -> str:
        """
        法話の候補リストから、最もテーマに合致するものを1つ選択する。
        """
        if not howa_candidates:
            return "適切な法話が見つかりませんでした。"

        logger.info(f"Evaluating {len(howa_candidates)} candidates... Selecting the first one as a dummy implementation.")
        
        # 将来的には、ここにLLMを使った評価ロジックが入る
        # (例: 各候補がテーマにどれだけ合致しているか点数付けさせる)
        
        # ダミー実装: 最初の候補を常に選択する
        best_howa = howa_candidates[0]
        
        return best_howa