import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import { HomePage } from "./components/HomePage.tsx";
import { HowaPage } from "./pages/HowaPage.tsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/howa" element={<HowaPage />} />
      </Routes>
    </Router>
  );
}

export default App;
