import React from "react";
import "./Navbar.css";

const Navbar = () => {
  const token = localStorage.getItem("token");
  
  return (
    <nav className="navbar">
      <h1 className="logo">Lumine</h1>
      <ul className="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/#how">How It Works</a></li>
        <li><a href="/#about">About</a></li>
        {token ? (
          <>
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href="/trends">Trends</a></li>
          </>
        ) : (
          <li><a href="/login">Login</a></li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
