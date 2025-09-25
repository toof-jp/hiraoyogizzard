// src/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
	// 法話生成APIのモック
	http.post("/v1/howa", async () => {
		// 実際のAPIっぽく、少し待つ
		await new Promise((resolve) => setTimeout(resolve, 1500));

		// 成功時のレスポンスを返す
		return HttpResponse.json({
			title: "【モック】SNS疲れの心に効く「足るを知る」という智慧",
			introduction:
				"最近、スマートフォンの通知が鳴るたびに、少し心がザワつくことはありませんか？これはモックデータから生成された導入文です。",
			problem_statement:
				"私たちは常に他者と繋がり、比較することで、無意識のうちに自分をすり減らしています。この心の渇きはどこから来るのでしょうか。",
			sutra_quote: {
				text: "吾れ唯だ足ることを知るのみ（われただたることをしるのみ）",
				source: "龍安寺『知足の蹲踞（つくばい）』より",
			},
			modern_example:
				"インフルエンサーの華やかな投稿を見て落ち込む必要はありません。あなたが今、この瞬間に持っているもの――温かいコーヒー一杯、好きな音楽、静かな時間――に意識を向けてみませんか。",
			conclusion:
				"「足りない」と外に求めるのではなく、「既に足りている」と内に感謝すること。それが、情報過多の時代を穏やかに生きるための第一歩です。",
		});
	}),
];
