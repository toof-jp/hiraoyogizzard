import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "../App.css";
import { createHowaTask, fetchHowaTask } from "../api/client.js";
import type { components } from "../api/generated.js";
import { HowaForm } from "../components/HowaForm.tsx";
import { LoadingSpinner } from "../components/LoadingSpinner.tsx";
import { HowaFeedback } from "../components/HowaFeedback.tsx";

type HowaResponse = components["schemas"]["HowaResponse"];
type HowaTaskStatus = components["schemas"]["HowaTaskStatus"];

export function HowaPage() {
	const [howa, setHowa] = useState<HowaResponse | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [taskId, setTaskId] = useState<string | null>(null);
	const [taskStatus, setTaskStatus] = useState<HowaTaskStatus | null>(null);

	const handleSubmit = async (
		theme: string,
		audiences: ("子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし")[],
	) => {
		setIsLoading(true);
		setError(null);
		setHowa(null);
		setTaskId(null);
		setTaskStatus(null);
		try {
			const submission = await createHowaTask({
				theme,
				audiences,
			});
			if (!submission || !submission.task_id) {
				throw new Error("タスクIDが取得できませんでした。");
			}
			setTaskId(submission.task_id);
			setTaskStatus(submission.status ?? "queued");
		} catch (err) {
			setError(
				"法話の生成に失敗しました。APIサーバーが起動していることを確認してください。",
			);
			console.error(err);
			setIsLoading(false);
		}
	};

	useEffect(() => {
		if (!taskId) {
			return;
		}

		let cancelled = false;
		let timeoutId: number | undefined;

		const poll = async () => {
			try {
				const statusResponse = await fetchHowaTask(taskId);
				if (cancelled) {
					return;
				}
				setTaskStatus(statusResponse.status);

				if (statusResponse.status === "completed") {
					if (statusResponse.result) {
						setHowa(statusResponse.result);
					} else {
						setError("タスクは完了しましたが結果を取得できませんでした。");
					}
					setIsLoading(false);
					setTaskId(null);
					return;
				}

				if (statusResponse.status === "failed") {
					setError(
						statusResponse.error ?? "法話の生成に失敗しました。時間をおいて再度お試しください。",
					);
					setIsLoading(false);
					setTaskId(null);
					return;
				}

				timeoutId = window.setTimeout(poll, 2000);
			} catch (err) {
				if (cancelled) {
					return;
				}
				console.error(err);
				setError("タスクの状態取得に失敗しました。時間をおいて再試行してください。");
				setIsLoading(false);
				setTaskId(null);
			}
		};

		poll();

		return () => {
			cancelled = true;
			if (timeoutId !== undefined) {
				window.clearTimeout(timeoutId);
			}
		};
	}, [taskId]);

	const loadingMessage =
		taskStatus === "queued"
			? "キューで順番待ちをしています..."
			: "AIが法話を執筆中です...";

	return (
		<div className="container">
			<header>
				<nav style={{ marginBottom: "1rem" }}>
					<Link
						to="/"
						style={{
							textDecoration: "none",
							color: "#666",
							fontSize: "0.9rem",
						}}
					>
						← AIお坊さんに戻る
					</Link>
				</nav>
				<h1>法話メーカー</h1>
				<p>AIエージェントが、あなたのための法話を創作します。</p>
			</header>

			<main>
				<HowaForm onSubmit={handleSubmit} isLoading={isLoading} />

				{isLoading && <LoadingSpinner message={loadingMessage} />}
				{error && (
					<div
						style={{
							backgroundColor: "#fee",
							border: "1px solid #fcc",
							color: "#c33",
							padding: "12px",
							borderRadius: "4px",
							marginBottom: "20px",
						}}
					>
						<strong>エラー:</strong> {error}
					</div>
				)}
				{taskId && !error && isLoading && (
					<p style={{ marginBottom: "20px", color: "#555" }}>
						タスクID: <code>{taskId}</code>
					</p>
				)}
				{howa && (
					<article className="howa-card">
						<h2>{howa.title}</h2>
						<section>
							<h3>導入</h3>
							<p>{howa.introduction}</p>
						</section>
						<section>
							<h3>問題提起</h3>
							<p>{howa.problem_statement}</p>
						</section>
						<section>
							<h3>経典の引用</h3>
							<blockquote>
								<p>{howa.sutra_quote?.text}</p>
								<footer>- {howa.sutra_quote?.source}</footer>
							</blockquote>
						</section>
						<section>
							<h3>現代の例え話</h3>
							<p>{howa.modern_example}</p>
						</section>
						<section>
							<h3>結論</h3>
							<p>{howa.conclusion}</p>
						</section>
					</article>
				)}
				{howa && <HowaFeedback howaId={howa.title} />}
			</main>
		</div>
	);
}
