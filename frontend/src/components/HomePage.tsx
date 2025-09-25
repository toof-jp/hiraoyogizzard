import { Link } from "react-router-dom";
import "./HomePage.css";

export function HomePage() {
	return (
		<div className="home-container">
			<header className="home-header">
				<h1 className="home-title">AIお坊さん</h1>
				<p className="home-subtitle">仏教の知恵をAIでお届けします</p>
			</header>

			<main className="home-main">
				<div className="button-grid">
					<Link to="/howa" className="feature-button active">
						<div className="button-icon">📿</div>
						<div className="button-text">
							<h3>法話メーカー</h3>
							<p>AIが心に響く法話を創作します</p>
						</div>
					</Link>

					<button className="feature-button disabled" disabled>
						<div className="button-icon">💬</div>
						<div className="button-text">
							<h3>AIお坊さんとの人生相談</h3>
							<p>開発中...</p>
						</div>
					</button>

					<button className="feature-button disabled" disabled>
						<div className="button-icon">📔</div>
						<div className="button-text">
							<h3>日記</h3>
							<p>開発中...</p>
						</div>
					</button>
				</div>
			</main>
		</div>
	);
}
