// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

async function enableMocking() {
	// MSWモックを無効にして実APIを使用
	// 必要に応じてimport.meta.env.VITE_USE_MOCKSなどの環境変数で制御可能
	return;
}

enableMocking().then(() => {
	ReactDOM.createRoot(document.getElementById("root")!).render(
		<React.StrictMode>
			<App />
		</React.StrictMode>,
	);
});
