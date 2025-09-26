import { Link } from "react-router-dom";
import "./HomePage.css";
import logoWhite from "../assets/logoWhite.png";

export function HomePage() {
  return (
    <div className="home-container">
      <header className="home-header">
        <div className="title-with-logo">
          <img
            src={logoWhite}
            alt="Logo"
            className="logo-image"
          />
          <h1 className="home-title">AIお坊さん</h1>
        </div>
        <p className="home-subtitle">仏教の知恵をAIでお届けします</p>
      </header>

      <main className="home-main">
        <nav className="navigation-links">
          <Link
            to="/howa"
            className="nav-link active"
            data-tooltip="AIが心に響く法話を創作します"
          >
            法話メーカー
          </Link>

          <span className="nav-link disabled" data-tooltip="開発中...">
            AIお坊さんとの人生相談
          </span>

          <span className="nav-link disabled" data-tooltip="開発中...">
            日記
          </span>
        </nav>
      </main>
    </div>
  );
}
