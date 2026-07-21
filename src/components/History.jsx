import React, { useEffect, useState } from "react";
import "./History.css";

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/history`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setAnalyses(data);
        } else {
          setError("Failed to load history.");
        }
      } catch (err) {
        setError("Network error.");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handleDeleteAll = async () => {
    if (!window.confirm("Are you sure you want to delete ALL your history? This cannot be undone.")) return;
    
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/privacy/all`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        setAnalyses([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm("Delete this record?")) return;
    
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/privacy/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        setAnalyses(analyses.filter(a => a.id !== id));
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="history-container">Loading...</div>;
  if (error) return <div className="history-container">{error}</div>;

  return (
    <div className="history-container fade-in">
      <div className="history-page-header">
        <div>
          <h2>Your Skin History</h2>
          <p className="subtitle">Review your past analyses and AI insights.</p>
        </div>
        {analyses.length > 0 && (
          <button className="btn-outline btn-danger" onClick={handleDeleteAll}>
            Clear All History
          </button>
        )}
      </div>

      {analyses.length === 0 ? (
        <p>You haven't completed any scans yet. Complete a skin analysis to see trends here.</p>
      ) : (
        <div className="history-list">
          {analyses.map(analysis => (
            <div key={analysis.id} className="history-card fade-in">
              <div className="history-header">
                <span className="date">{new Date(analysis.timestamp).toLocaleDateString()}</span>
                <div className="header-actions">
                  {analysis.predicted_class && (
                    <span className="badge prediction mr-2">AI Match: {analysis.predicted_class} ({analysis.confidence}%)</span>
                  )}
                  <button 
                    className="btn-outline btn-small"
                    onClick={() => {
                      const token = localStorage.getItem("token");
                      fetch(`${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/history/reports/${analysis.id}/pdf`, {
                        headers: { Authorization: `Bearer ${token}` }
                      })
                      .then(response => response.blob())
                      .then(blob => {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `Lumine_Report_${analysis.id}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                      });
                    }}
                  >
                    PDF
                  </button>
                  <button 
                    className="btn-outline btn-small btn-danger"
                    onClick={() => handleDeleteItem(analysis.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <h4>{analysis.text_condition}</h4>
              {analysis.ai_summary && (
                <div className="ai-summary">
                  <strong>AI Insights:</strong>
                  <p>{analysis.ai_summary}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
