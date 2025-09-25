from typing import List
import random
from ..models.howa import GenerateHowaRequest, HowaResponse, SutraQuote, AudienceType


class HowaGenerationService:
    """法話生成サービス"""
    
    def __init__(self):
        # サンプルデータ（実際の実装では、AIやデータベースから取得）
        self.sample_sutras = {
            "感謝": SutraQuote(
                text="恵みを与える者は幸せであり、与えられた者もまた幸せである。",
                source="法句経 第十五章『安楽品』"
            ),
            "慈悲": SutraQuote(
                text="慈しみの心を持つ者に、怨みは生じない。",
                source="法句経 第一章『双要品』"
            ),
            "智慧": SutraQuote(
                text="愚かさを知ることは智慧の始まりである。",
                source="法句経 第五章『愚人品』"
            ),
        }
        
        self.modern_examples = {
            AudienceType.YOUTH: [
                "SNSでのコミュニケーションにおいて、相手の気持ちを思いやることの大切さ",
                "就職活動や人間関係での困難を、成長の機会として捉える視点",
                "デジタル時代における本当のつながりとは何かを考える"
            ],
            AudienceType.BUSINESS_PERSON: [
                "忙しい日々の中で、一息つく時間の大切さを見つめ直す",
                "競争社会において、他者への思いやりを忘れないことの意義",
                "成功と失敗を通して学ぶ、本当の豊かさとは何か"
            ],
            AudienceType.CHILDREN: [
                "友達と喧嘩したとき、相手の気持ちを考えてみよう",
                "お父さんお母さんへの感謝の気持ちを表現してみよう",
                "自然の中で感じる、すべての生き物への思いやり"
            ],
            AudienceType.ELDERLY: [
                "人生の経験を通して培った智慧を、若い世代に伝える喜び",
                "家族や地域とのつながりの中で見つける、生きがい",
                "これまでの人生を振り返り、感謝の心を育む"
            ]
        }

    async def generate_howa(self, request: GenerateHowaRequest) -> HowaResponse:
        """法話を生成する"""
        
        # テーマに基づいて適切な経典を選択
        sutra = self.sample_sutras.get(request.theme, self.sample_sutras["感謝"])
        
        # 対象者に応じた現代的な例を選択
        primary_audience = request.audiences[0] if request.audiences else AudienceType.UNSPECIFIED
        if primary_audience in self.modern_examples:
            modern_example = random.choice(self.modern_examples[primary_audience])
        else:
            modern_example = "日常生活の中で出会う、様々な人々との関わりを通して学ぶ大切なこと"
        
        # 法話を構成
        response = HowaResponse(
            title=f"{request.theme}の心を育む - {primary_audience.value}へのメッセージ",
            introduction=f"""
皆さん、こんにちは。今日は「{request.theme}」というテーマについて、
ご一緒に考えてみたいと思います。

現代社会は変化が激しく、私たちは日々様々な出来事に直面します。
そんな中で、心の平安を保ち、他者との良い関係を築いていくことは、
決して簡単なことではありません。

しかし、仏教の教えには、そうした困難な時代を生きる私たちへの
深い智慧が込められています。
            """.strip(),
            
            problem_statement=f"""
では、現代を生きる私たち、特に{primary_audience.value}の皆さんにとって、
「{request.theme}」とはどのような意味を持つのでしょうか。

忙しい日常の中で、私たちはともすると自分のことで精一杯になり、
他者への思いやりや、身の回りの恵みに気づくことを忘れがちです。

そんな時こそ、仏教の教えに立ち返り、
心の在り方を見つめ直すことが大切なのです。
            """.strip(),
            
            sutra_quote=sutra,
            
            modern_example=modern_example,
            
            conclusion=f"""
この教えを日常生活に活かすために、まずは小さなことから始めてみましょう。

毎日のちょっとした瞬間に、{request.theme}の心を思い出してください。
朝起きたときに「今日も新しい一日をいただけることへの感謝」を、
人と出会ったときに「この出会いへの感謝」を、
そして一日の終わりには「今日一日の恵みへの感謝」を。

小さな積み重ねが、やがて大きな心の変化をもたらします。
仏教の教えとともに、豊かな人生を歩んでいきましょう。
            """.strip()
        )
        
        return response