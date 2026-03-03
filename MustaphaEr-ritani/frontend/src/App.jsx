
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import UploadCV from "./components/UploadCV";
import JobForm from "./components/JobForm";
import MatchResult from "./components/MatchResult";
import CandidateRanking from "./components/CandidateRanking";

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const renderPage = () => {
    switch (activePage) {
      case "dashboard": return <Dashboard />;
      case "upload": return <UploadCV />;
      case "jobs": return <JobForm />;
      case "match": return <MatchResult />;
      case "ranking": return <CandidateRanking />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />
      <main className="main-content fade-in">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
