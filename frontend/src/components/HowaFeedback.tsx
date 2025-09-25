import { useState } from "react";

interface HowaFeedbackProps {
	howaId?: string;
}

export function HowaFeedback({ howaId }: HowaFeedbackProps) {
	const [feedback, setFeedback] = useState<"positive" | "negative" | null>(
		null,
	);
	const [isSubmitted, setIsSubmitted] = useState(false);

	const handleFeedback = async (type: "positive" | "negative") => {
		if (isSubmitted) return;

		setFeedback(type);
		setIsSubmitted(true);

		// TODO: API呼び出しでフィードバックを送信
		console.log("Feedback submitted:", { howaId, type });

		// フィードバック送信完了を示すタイムアウト
		setTimeout(() => {
			// setIsSubmitted(false); // 必要に応じてリセット
		}, 2000);
	};

	return (
		<div
			style={{
				marginTop: "2rem",
				padding: "1.5rem",
				borderRadius: "12px",
				background: "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)",
				border: "1px solid #e2e8f0",
				textAlign: "center",
			}}
		>
			<p
				style={{
					margin: "0 0 1rem 0",
					fontSize: "1rem",
					fontWeight: "500",
					color: "#4a5568",
					fontFamily: '"Noto Serif JP", serif',
				}}
			>
				この法話は役に立ちましたか？
			</p>

			{!isSubmitted ? (
				<div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
					<button
						onClick={() => handleFeedback("positive")}
						style={{
							background:
								feedback === "positive" ? "rgba(72, 187, 120, 0.1)" : "white",
							border:
								feedback === "positive"
									? "2px solid #48bb78"
									: "2px solid #e2e8f0",
							borderRadius: "50px",
							padding: "0.75rem 1.5rem",
							cursor: "pointer",
							transition: "all 0.2s ease",
							fontSize: "1.2rem",
							display: "flex",
							alignItems: "center",
							gap: "0.5rem",
							fontWeight: "500",
							color: feedback === "positive" ? "#2f855a" : "#4a5568",
						}}
						onMouseEnter={(e) => {
							e.currentTarget.style.transform = "translateY(-2px)";
							e.currentTarget.style.boxShadow =
								"0 4px 12px rgba(72, 187, 120, 0.2)";
						}}
						onMouseLeave={(e) => {
							e.currentTarget.style.transform = "translateY(0)";
							e.currentTarget.style.boxShadow = "none";
						}}
					>
						👍 <span>役に立った</span>
					</button>

					<button
						onClick={() => handleFeedback("negative")}
						style={{
							background:
								feedback === "negative" ? "rgba(245, 101, 101, 0.1)" : "white",
							border:
								feedback === "negative"
									? "2px solid #f56565"
									: "2px solid #e2e8f0",
							borderRadius: "50px",
							padding: "0.75rem 1.5rem",
							cursor: "pointer",
							transition: "all 0.2s ease",
							fontSize: "1.2rem",
							display: "flex",
							alignItems: "center",
							gap: "0.5rem",
							fontWeight: "500",
							color: feedback === "negative" ? "#c53030" : "#4a5568",
						}}
						onMouseEnter={(e) => {
							e.currentTarget.style.transform = "translateY(-2px)";
							e.currentTarget.style.boxShadow =
								"0 4px 12px rgba(245, 101, 101, 0.2)";
						}}
						onMouseLeave={(e) => {
							e.currentTarget.style.transform = "translateY(0)";
							e.currentTarget.style.boxShadow = "none";
						}}
					>
						👎 <span>改善の余地あり</span>
					</button>
				</div>
			) : (
				<div
					style={{
						padding: "1rem",
						color: "#2f855a",
						fontWeight: "500",
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						gap: "0.5rem",
					}}
				>
					✅ フィードバックをありがとうございます！
				</div>
			)}

			<p
				style={{
					margin: "1rem 0 0 0",
					fontSize: "0.85rem",
					color: "#718096",
					fontStyle: "italic",
				}}
			>
				あなたのフィードバックはAIの改善に活用されます
			</p>
		</div>
	);
}
