// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

async function enableMocking() {
  // 開発環境でない場合は、何もしない
  if (!import.meta.env.DEV) {
    return;
  }

  const { worker } = await import("./mocks/browser.js");

  // `worker.start()` は非同期です。
  return worker.start();
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});
