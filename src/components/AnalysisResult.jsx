import React from "react";
import "./AnalysisResult.css";

const AnalysisResult = ({ result, imagePreview, onReset }) => {
  return (
    <div className="analysis-result-wrapper">
      <div className="result-header">
        <h2>Analysis Complete</h2>
        <button className="btn-outline" onClick={onReset}>Start New Scan</button>
      </div>

      <div className="result-grid">
        {imagePreview && (
          <div className="result-card image-card">
            <h3>Analyzed Image</h3>
            <img src={imagePreview} alt="Scanned region" className="result-image" />
          </div>
        )}

        {result.image_analysis && (
          <div className="result-card ai-card">
            <h3>Visual Match</h3>
            <div className="match-info">
              <span className="label-badge">{result.image_analysis.predicted_label}</span>
              <div className="confidence-wrapper">
                <span className="confidence-text">{result.image_analysis.confidence}% Confidence</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${result.image_analysis.confidence}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="result-card text-card">
          <h3>Symptom Analysis</h3>
          <p><strong>Detected Condition:</strong> {result.text_analysis.condition}</p>
          <p><strong>Possible Causes:</strong> {result.text_analysis.causes}</p>
        </div>
      </div>

      {result.ai_summary && (
        <div className="gemini-insight">
          <h3><span className="sparkle">✨</span> Lumine AI Insight</h3>
          <p>{result.ai_summary}</p>
        </div>
      )}

      <div className="recommendation-box">
        <h4>General Recommendation</h4>
        <p>{result.recommendation}</p>
      </div>

      <p className="disclaimer">
        <strong>Disclaimer:</strong> Lumine AI is an informational tool and does not provide medical diagnosis. Always consult a certified dermatologist for professional advice.
      </p>
    </div>
  );
};

export default AnalysisResult;
