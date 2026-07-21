import React, { useState, useRef } from "react";
import AnalysisResult from "./AnalysisResult";
import "./Diagnosis.css";

const API_URL = "http://127.0.0.1:8000";

const Diagnosis = () => {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        setError("Please upload a JPG, PNG, or WEBP image.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError("File is too large. Maximum size is 10MB.");
        return;
      }
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
      setError("");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleImageChange({ target: { files: [file] } });
    }
  };

  const handleRemoveImage = (e) => {
    e.stopPropagation();
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError("Please describe your skin concern.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("description", description);
    if (image) formData.append("image", image);

    try {
      const token = localStorage.getItem("token");
      const headers = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const response = await fetch(`${API_URL}/analyze/`, {
        method: "POST",
        headers: headers,
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed");
      }
      setResult(data);
    } catch (err) {
      setError(err.message || "Network error or server is unavailable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="diagnosis-container fade-in">
      {!result ? (
        <div className="diagnosis-form-wrapper">
          <h2>Start Your Skin Analysis</h2>
          <p className="subtitle">Upload a photo and describe your symptoms for an AI-powered assessment.</p>
          
          {error && <div className="error-alert">{error}</div>}
          
          <form onSubmit={handleSubmit} className="diagnosis-form">
            <div 
              className={`dropzone ${isDragging ? "dragging" : ""} ${imagePreview ? "has-image" : ""}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !imagePreview && fileInputRef.current.click()}
            >
              {imagePreview ? (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                  <button type="button" className="btn-remove" onClick={handleRemoveImage}>Remove</button>
                </div>
              ) : (
                <div className="dropzone-placeholder">
                  <span className="icon">📸</span>
                  <p>Drag and drop an image here, or <strong>click to browse</strong></p>
                  <span className="text-small">Supports JPG, PNG, WEBP (Max 10MB)</span>
                </div>
              )}
              <input 
                type="file" 
                ref={fileInputRef}
                onChange={handleImageChange} 
                accept="image/jpeg, image/png, image/webp" 
                hidden 
              />
            </div>
            
            <div className="input-group">
              <label>Describe your symptoms</label>
              <textarea
                placeholder="e.g., I've had these red bumps on my forehead for 3 days..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="4"
                required
              />
            </div>

            <button type="submit" className="btn-primary btn-large" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Skin"}
            </button>
          </form>
        </div>
      ) : (
        <AnalysisResult result={result} imagePreview={imagePreview} onReset={() => setResult(null)} />
      )}
    </div>
  );
};

export default Diagnosis;
