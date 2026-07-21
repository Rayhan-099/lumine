import React from "react";
import describe from "../assets/describe.svg"; 
import upload from "../assets/upload.svg";
import consult from "../assets/consult.svg";
import care from "../assets/care.svg";
import "./HowItWorks.css";

const HowItWorks = () => {
  const steps = [
    {
      id: 1,
      image: describe,
      title: "Describe Your Symptoms",
      text: "Tell us what’s bothering you- acne, rashes, dryness, or irritation.",
    },
    {
      id: 2,
      image: upload,
      title: "Upload an Image",
      text: "Add a clear photo of your skin issue for AI-based analysis.",
    },
    {
      id: 3,
      image: consult,
      title: "Consult a Dermatologist",
      text: "Connect with certified doctors for expert skin care advice.",
    },
    {
      id: 4,
      image: care,
      title: "Get Your Care Plan",
      text: "Receive your personalized diagnosis and treatment suggestions.",
    },
  ];

  return (
    <section className="how-it-works">
      <div className="how-it-works-text">
        <h2>How It Works</h2>
        <p>Follow these simple steps to start your AI-powered skin care journey.</p>
      </div>

      <div className="steps-container">
        {steps.map((step) => (
          <div className="step" key={step.id}>
            <img src={step.image} alt={step.title} className="step-image" />
            <h3>{step.title}</h3>
            <p>{step.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default HowItWorks;
