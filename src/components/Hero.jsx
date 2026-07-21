import React from "react";
import { useNavigate } from "react-router-dom";
import "./Hero.css";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section id="home" className="hero">
      <div className="hero-text">
        <h2>Welcome to Lumine AI</h2>
        <h2>Your AI-Powered Skin Health Companion</h2>
        <p>
          Lumine is an intelligent assistant built to help you understand your skin better.
          Whether you’re facing acne, rashes, dryness, or pigmentation, Lumine uses advanced
          Artificial Intelligence to analyze your symptoms and images to give you a reliable
          preliminary diagnosis. Our goal is to make skin health monitoring simple, accurate,
          and accessible for everyone.
        </p>
        <p>
          Powered by cutting-edge Machine Learning and trained with dermatological data,
          Lumine acts as your first step before consulting a doctor. You can describe your
          symptoms, upload images, and receive suggestions for potential causes and care
          options within seconds.
        </p>
        <div className="buttons">
          <button className="btn-primary" onClick={() => navigate("/diagnosis")}>
            Start Diagnosis
          </button>
          <button className="btn-secondary" onClick={() => navigate("/learnMore")}>
            Learn More
          </button>
        </div>
      </div>

      {/* 🧠 Image + Scanner Effect */}
      <div className="hero-image">
        <div className="scan-wrapper">
          <img
            src="https://img.freepik.com/premium-vector/flat-style-biometric-scanning-man-face-recognition-personal-verification-identity-detection_981400-144.jpg?semt=ais_hybrid&w=740&q=80"
            alt="AI Skin Health"
          />
          <div className="scanner-line"></div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
