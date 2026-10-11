import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useNavigate,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Crops from "./pages/Crops";
import SoilFertilizer from "./pages/SoilFertilizer";
import DiseaseDetection from "./pages/DiseaseDetection";
import YieldPrediction from "./pages/YieldPrediction";
import WeatherIrrigation from "./pages/WeatherIrrigation";

import "./App.css";

const features = [
  {
    icon: "🌱",
    title: "Crop Management",
    description: "Manage crops and monitor crop details.",
    color: "green",
  },
  {
    icon: "🔬",
    title: "Disease Detection",
    description: "Upload a leaf image to check plant health.",
    color: "orange",
  },
  {
    icon: "🧪",
    title: "Fertilizer Recommendation",
    description: "Get fertilizer suggestions for your soil.",
    color: "blue",
  },
  {
    icon: "🌾",
    title: "Yield Prediction",
    description: "Estimate crop yield from farm conditions.",
    color: "purple",
  },
  {
    icon: "🌦️",
    title: "Weather & Irrigation",
    description: "Plan farming activities around conditions.",
    color: "cyan",
  },
  {
    icon: "🤖",
    title: "AI Agriculture Assistant",
    description: "Ask questions and get farming guidance.",
    color: "pink",
  },
];

function Dashboard() {
  const [activePage, setActivePage] = useState("Dashboard");
  const navigate = useNavigate();

  const navigation = [
    { icon: "🏠", label: "Dashboard" },
    { icon: "🌱", label: "Crop Management" },
    { icon: "🧪", label: "Soil & Fertilizer" },
    { icon: "🔬", label: "Disease Detection" },
    { icon: "🌾", label: "Yield Prediction" },
    { icon: "🌦️", label: "Weather & Irrigation" },
    { icon: "🤖", label: "AI Assistant" },
  ];

  const pageMap = {
    "Crop Management": "Crop Management",
    "Disease Detection": "Disease Detection",
    "Fertilizer Recommendation": "Soil & Fertilizer",
    "Yield Prediction": "Yield Prediction",
    "Weather & Irrigation": "Weather & Irrigation",
    "AI Agriculture Assistant": "AI Assistant",
  };

  function logout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }

  function renderPage() {
    switch (activePage) {
      case "Crop Management":
        return <Crops />;

      case "Soil & Fertilizer":
        return <SoilFertilizer />;

      case "Disease Detection":
        return <DiseaseDetection />;

      case "Yield Prediction":
        return <YieldPrediction />;

      case "Weather & Irrigation":
        return <WeatherIrrigation />;

      case "AI Assistant":
        return (
          <section className="placeholder-page">
            <div className="placeholder-icon">🤖</div>
            <h2>AI Agriculture Assistant</h2>
            <p>
              Ask agricultural questions and get AI-powered
              farming guidance. The assistant interface will
              be connected here.
            </p>
            <button
              type="button"
              className="primary-button"
              onClick={() => setActivePage("Dashboard")}
            >
              ← Back to dashboard
            </button>
          </section>
        );

      default:
        return (
          <section className="placeholder-page">
            <div className="placeholder-icon">🌿</div>
            <h2>{activePage}</h2>
            <p>
              Select a tool from the sidebar to manage your farm
              with Smart Agriculture AI.
            </p>
            <button
              type="button"
              className="primary-button"
              onClick={() => setActivePage("Dashboard")}
            >
              ← Back to dashboard
            </button>
          </section>
        );
    }
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <Link to="/" className="brand">
          <div className="brand-icon">🌿</div>
          <div>
            <h2>SmartAgri</h2>
            <span>AI FARMING PLATFORM</span>
          </div>
        </Link>

        <p className="nav-heading">MAIN MENU</p>

        <nav>
          {navigation.map((item) => (
            <button
              key={item.label}
              type="button"
              className={`nav-item ${
                activePage === item.label ? "active" : ""
              }`}
              onClick={() => setActivePage(item.label)}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-icon">💡</div>
          <strong>Smart farming starts here</strong>
          <p>
            Use AI insights to make better farming decisions.
          </p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace / {activePage}
            </p>
            <h1>{activePage}</h1>
          </div>

          <div className="profile">
            <div className="profile-avatar">F</div>
            <div>
              <strong>Farmer</strong>
              <span>Smart Agriculture AI</span>
            </div>

            <button
              type="button"
              className="logout-button"
              onClick={logout}
            >
              Log out
            </button>
          </div>
        </header>

        {activePage === "Dashboard" ? (
          <>
            <section className="welcome-banner">
              <div>
                <span className="eyebrow">
                  YOUR FARM, POWERED BY AI
                </span>

                <h2>Welcome to Smart Agriculture 🌿</h2>

                <p>
                  Make informed farming decisions with intelligent
                  crop management, predictions, and AI assistance.
                </p>

                <button
                  type="button"
                  className="primary-button"
                  onClick={() =>
                    setActivePage("Crop Management")
                  }
                >
                  Explore crop management →
                </button>
              </div>

              <div className="banner-illustration">🌾</div>
            </section>

            <section className="section-heading">
              <div>
                <h2>Explore your tools</h2>
                <p>
                  Everything you need to manage your farm.
                </p>
              </div>
            </section>

            <section className="feature-grid">
              {features.map((feature) => (
                <button
                  type="button"
                  className="feature-card"
                  key={feature.title}
                  onClick={() =>
                    setActivePage(pageMap[feature.title])
                  }
                >
                  <div
                    className={`feature-icon ${feature.color}`}
                  >
                    {feature.icon}
                  </div>

                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                  <span className="card-link">
                    Open tool →
                  </span>
                </button>
              ))}
            </section>

            <footer>
              Smart Agriculture AI <span>•</span> Version 1.0.0
            </footer>
          </>
        ) : (
          renderPage()
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
