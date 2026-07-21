import React from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  if (!token) {
    navigate("/login");
    return null;
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h2>Lumine AI Dashboard</h2>
        <button onClick={handleLogout} className="btn-secondary">Logout</button>
      </header>
      <div className="dashboard-content">
        <div className="card">
          <h3>Quick Analysis</h3>
          <p>Scan your skin instantly using our AI models.</p>
          <button className="btn-primary" onClick={() => navigate("/diagnosis")}>Start Scan</button>
        </div>
        <div className="card">
          <h3>Your History</h3>
          <p>View your past scans and AI insights.</p>
          <button className="btn-secondary" onClick={() => navigate("/history")}>View History</button>
        </div>
        <div className="card">
          <h3>Analytics & Trends</h3>
          <p>Track your skin's progress over time.</p>
          <button className="btn-secondary" onClick={() => navigate("/trends")}>View Trends</button>
        </div>
        <div className="card">
          <h3>Compare Scans</h3>
          <p>See before and after comparisons side-by-side.</p>
          <button className="btn-secondary" onClick={() => navigate("/compare")}>Compare</button>
        </div>
        <div className="card">
          <h3>AI Assistant</h3>
          <p>Chat with Lumine AI about your skin history.</p>
          <button className="btn-secondary" onClick={() => navigate("/assistant")}>Ask AI</button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
