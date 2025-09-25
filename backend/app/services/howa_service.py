from typing import List
import random
from ..models.howa import GenerateHowaRequest, HowaResponse, SutraQuote
from ..core.error_handler import ErrorHandler


class HowaGenerationService:
    """法話生成サービス"""
    
    async def generate_howa(self, request: GenerateHowaRequest) -> HowaResponse:
        """法話を生成する（モックデータ使用）"""
        try:
            theme = request.theme
            audience = request.audiences[0] if request.audiences else "指定なし"

            # 新しいレスポンス形式に合わせたモックレスポンスを作成
            response = HowaResponse(
                title=f"「{theme}」についての法話 ({audience}向け)",
                introduction=f"皆さん、こんにちは。今日は「{theme}」という、私たちの生活に深く関わるテーマについてお話しします。最近のニュースでも話題になりましたが...",
                problem_statement=f"私たちは日々忙しく過ごす中で、本当に大切な「{theme}」の心を見失いがちではないでしょうか？仏教の教えは、この問題に光を当ててくれます。",
                sutra_quote=SutraQuote(
                    text="一切の生きとし生けるものは、幸福であれ、安穏であれ、安楽であれ。",
                    source="スッタニパータ"
                ),
                modern_example=f"例えば、{audience}の皆さんが日常で経験する〇〇のような状況。ここにも「{theme}」の教えを活かすヒントが隠されています。",
                conclusion=f"今日の話をまとめますと、「{theme}」の心を育むことで、私たちの人生はより豊かになります。明日からできる小さな一歩として、〇〇を試してみてはいかがでしょうか。"
            )
            
            return response
            
        except Exception as e:
            error_info = ErrorHandler.handle_generation_error(e)
            # FastAPIが適切に処理できるよう、HTTPExceptionを発生させるのが望ましい
            # ここでは簡略化のため元の例外を再発生
            raise Exception(error_info["detail"])