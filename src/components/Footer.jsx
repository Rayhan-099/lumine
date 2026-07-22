import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} Lumine AI. All Rights Reserved.</p>
      <div className="footer-links">
        <a href="#privacy">Privacy Policy</a>
        <a href="#terms">Terms</a>
        <a href="#contact">Contact</a>
      </div>
    </footer>
  );
};

export default Footer;
