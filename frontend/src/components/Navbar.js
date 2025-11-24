import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/auth';
import './Navbar.css';

function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut();
    localStorage.removeItem('token');
    navigate('/login');
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
        <div className="navbar-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/upload">Upload</Link>
          <Link to="/training">Training</Link>
          <Link to="/predictions">Predictions</Link>
          <Link to="/health">Health</Link>
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



