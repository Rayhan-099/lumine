import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Diagnosis from "./components/Diagnosis";
import LearnMore from "./components/learnMore";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import HowItWorks from "./components/HowItWorks";
import About from "./components/About";
import Footer from "./components/Footer";
import Login from "./components/Login";
import Register from "./components/Register";
import Dashboard from "./components/Dashboard";
import History from "./components/History";
import Trends from "./components/Trends";
import Comparison from "./components/Comparison";
import Assistant from "./components/Assistant";
import "./App.css";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        {/* Homepage Route */}
        <Route
          path="/"
          element={
            <>
              <Hero />
              <HowItWorks />
              <About />
              <Footer />
            </>
          }
        />

        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/history" element={<History />} />
        <Route path="/trends" element={<Trends />} />
        <Route path="/compare" element={<Comparison />} />
        <Route path="/assistant" element={<Assistant />} />

        {/* Diagnosis Page Route */}
        <Route path="/diagnosis" element={<Diagnosis />} />
        <Route path="/learnMore" element={<LearnMore />} />
      </Routes>
    </Router>
  );
}

export default App;
