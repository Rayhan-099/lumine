import React, { useEffect, useState } from "react";
import "./Comparison.css";

const Comparison = () => {
  const [history, setHistory] = useState([]);
  const [selectedId1, setSelectedId1] = useState("");
  const [selectedId2, setSelectedId2] = useState("");
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch("http://127.0.0.1:8000/history", {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setHistory(data);
        }
      } catch (err) {
        console.error("Failed to load history for comparison", err);
      }
    };
    fetchHistory();
  }, []);

  const handleCompare = async () => {
    if (!selectedId1 || !selectedId2) {
      setError("Please select two analyses to compare.");
      return;
    }
    if (selectedId1 === selectedId2) {
      setError("Please select two different analyses.");
      return;
    }
    
    setLoading(true);
    setError("");
    setComparisonResult(null);
    
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`http://127.0.0.1:8000/compare?id1=${selectedId1}&id2=${selectedId2}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = await response.json();
      if (response.ok) {
        setComparisonResult(data);
      } else {
        setError(data.detail || "Comparison failed.");
      }
    } catch (err) {
      setError("Network error.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoString) => new Date(isoString).toLocaleString();

  return (
    <div className="comparison-container fade-in">
      <h2>Compare Analyses</h2>
      <p className="subtitle">Select two past scans to see how your condition has changed.</p>
      
      {history.length < 2 ? (
        <div className="empty-state">
          <p>You need at least two saved analyses to perform a comparison.</p>
        </div>
      ) : (
        <div className="comparison-selector">
          <div className="select-group">
            <label>Scan 1</label>
            <select value={selectedId1} onChange={(e) => setSelectedId1(e.target.value)}>
              <option value="">Select a scan</option>
              {history.map(item => (
                <option key={item.id} value={item.id}>
                  {formatDate(item.timestamp)} - {item.predicted_class || item.text_condition}
                </option>
              ))}
            </select>
          </div>
          <div className="select-group">
            <label>Scan 2</label>
            <select value={selectedId2} onChange={(e) => setSelectedId2(e.target.value)}>
              <option value="">Select a scan</option>
              {history.map(item => (
                <option key={item.id} value={item.id}>
                  {formatDate(item.timestamp)} - {item.predicted_class || item.text_condition}
                </option>
              ))}
            </select>
          </div>
          <button className="btn-primary" onClick={handleCompare} disabled={loading}>
            {loading ? "Comparing..." : "Compare"}
          </button>
        </div>
      )}

      {error && <div className="error-alert mt-4">{error}</div>}

      {comparisonResult && (
        <div className="comparison-result fade-in">
          <div className="gemini-insight mb-6">
            <h3><span className="sparkle">✨</span> AI Comparison Insight</h3>
            <p>{comparisonResult.comparison_summary}</p>
          </div>
          
          <div className="comparison-grid">
            <div className="comparison-card">
              <div className="card-header">
                <h4>Older Scan</h4>
                <span className="date">{formatDate(comparisonResult.analysis_1.timestamp)}</span>
              </div>
              <div className="card-body">
                <p><strong>Detected:</strong> {comparisonResult.analysis_1.predicted_class || "Unknown"}</p>
                <p><strong>Confidence:</strong> {comparisonResult.analysis_1.confidence}%</p>
                <p><strong>Symptom:</strong> {comparisonResult.analysis_1.text_condition}</p>
              </div>
            </div>
            
            <div className="comparison-card">
              <div className="card-header">
                <h4>Newer Scan</h4>
                <span className="date">{formatDate(comparisonResult.analysis_2.timestamp)}</span>
              </div>
              <div className="card-body">
                <p><strong>Detected:</strong> {comparisonResult.analysis_2.predicted_class || "Unknown"}</p>
                <p><strong>Confidence:</strong> {comparisonResult.analysis_2.confidence}%</p>
                <p><strong>Symptom:</strong> {comparisonResult.analysis_2.text_condition}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Comparison;
