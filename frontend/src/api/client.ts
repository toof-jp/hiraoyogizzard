// src/api/client.ts

import createClient from "openapi-fetch";
// 'paths'は型なので、`import type`を使ってインポートします
import type { paths } from "./generated.js";

// createClientのbaseUrlは環境変数から読み込みます
const { POST } = createClient<paths>({
	baseUrl: import.meta.env.VITE_API_BASE_URL,
});

// 法話生成APIを呼び出す関数
export const generateHowa = async (
	// 型も`paths`から正しく参照します
	params: paths["/howa"]["post"]["requestBody"]["content"]["application/json"],
) => {
	const { data, error } = await POST("/howa", {
		body: params,
	});

	if (error) {
		throw new Error(`API Error: ${error}`);
	}
	return data;
};
