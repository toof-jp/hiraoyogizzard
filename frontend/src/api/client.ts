// src/api/client.ts

import createClient from "openapi-fetch";
import type { paths } from "./generated.js";

const { POST, GET } = createClient<paths>({
	baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

export const createHowaTask = async (
	params: paths["/v1/howa"]["post"]["requestBody"]["content"]["application/json"],
) => {
	const { data, error } = await POST("/v1/howa", {
		body: params,
	});

	if (error) {
		throw new Error(`API Error: ${error}`);
	}
	return data;
};

export const fetchHowaTask = async (
	taskId: string,
): Promise<
	paths["/v1/howa/{task_id}"]["get"]["responses"]["200"]["content"]["application/json"]
> => {
	const { data, error } = await GET("/v1/howa/{task_id}", {
		params: {
			path: { task_id: taskId },
		},
	});

	if (error) {
		throw new Error(`API Error: ${error}`);
	}
	if (!data) {
		throw new Error("Empty response from status endpoint");
	}
	return data;
};
