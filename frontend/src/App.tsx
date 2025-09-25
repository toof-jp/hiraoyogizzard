import { useState } from "react";
import "./App.css";
import { generateHowa } from "./api/client.js";
import type { components } from "./api/generated.js";

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

  // ボタンが押されたときに実行される関数
  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setHowa(null);
    try {
      const response = await generateHowa({
        theme: "感謝",
        audiences: ["若者"],
      });
      if (response) {
        setHowa(response);
      }
    } catch (err) {
      setError("法話の生成に失敗しました。");
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
        {/* ここに将来的にフォームコンポーネントを配置 */}
        <button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? "生成中..." : "法話を生成する (モック)"}
        </button>

        {/* ローディング、エラー、成功時の表示を切り替える */}
        {isLoading && <p>AIが執筆中です...</p>}
        {error && <p className="error">{error}</p>}
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
