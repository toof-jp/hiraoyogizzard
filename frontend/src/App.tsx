import { useState } from "react";
import "./App.css";
import { generateHowa } from "./api/client.js";
import type { components } from "./api/generated.js";
import { HowaForm } from "./components/HowaForm.tsx";
import { LoadingSpinner } from "./components/LoadingSpinner.tsx";

// HowaResponseの型をインポート
type HowaResponse = components["schemas"]["HowaResponse"];

function App() {
  // 3つの状態を管理する
  // 1. 生成された法話のデータ
  const [howa, setHowa] = useState<HowaResponse | null>(null);
  // 2. ローディング中かどうかの状態
  const [isLoading, setIsLoading] = useState(false);
  // 3. エラーが発生したときのメッセージ
  const [error, setError] = useState<string | null>(null);

  // フォームが送信されたときに実行される関数
  const handleSubmit = async (
    theme: string,
    audiences: ("子供" | "若者" | "ビジネスパーソン" | "高齢者" | "指定なし")[]
  ) => {
    setIsLoading(true);
    setError(null);
    setHowa(null);
    try {
      const response = await generateHowa({
        theme,
        audiences,
      });
      if (response) {
        setHowa(response);
      }
    } catch (err) {
      setError(
        "法話の生成に失敗しました。APIサーバーが起動していることを確認してください。"
      );
      console.error(err); // コンソールにエラーの詳細を出力
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>法話メーカー</h1>
        <p>AIエージェントが、あなたのための法話を創作します。</p>
      </header>

      <main>
        <HowaForm onSubmit={handleSubmit} isLoading={isLoading} />

        {/* ローディング、エラー、成功時の表示を切り替える */}
        {isLoading && <LoadingSpinner message="AIが法話を執筆中です..." />}
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
      </main>
    </div>
  );
}

export default App;
