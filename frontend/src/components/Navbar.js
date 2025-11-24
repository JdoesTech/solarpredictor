import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/auth';
import './Navbar.css';

function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = async () => {
    await signOut();
    localStorage.removeItem('token');
    navigate('/login');
    setIsMenuOpen(false);
  };

  const handleNavClick = () => {
    setIsMenuOpen(false);
  };

  if (!user) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          ☀️ Solar Energy Prediction
        </Link>
        <button
          className="navbar-toggle"
          onClick={() => setIsMenuOpen((prev) => !prev)}
          aria-label="Toggle navigation menu"
        >
          <span />
          <span />
          <span />
        </button>
        <div className="navbar-links">
          <div className={`navbar-links__items ${isMenuOpen ? 'open' : ''}`}>
            <Link to="/dashboard" onClick={handleNavClick}>Dashboard</Link>
            <Link to="/upload" onClick={handleNavClick}>Upload</Link>
            <Link to="/training" onClick={handleNavClick}>Training</Link>
            <Link to="/predictions" onClick={handleNavClick}>Predictions</Link>
            <Link to="/health" onClick={handleNavClick}>Health</Link>
          </div>
          <span className="navbar-user">{user.email}</span>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;



