import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../services/auth';
import './Landing.css';

function Landing() {
  const { user } = useAuth();

  return (
    <div className="landing">
      <header className="landing-hero">
        <div className="landing-hero-content">
          <p className="landing-badge">SDG 7 • Affordable & Clean Energy</p>
          <h1>Predict Solar Output with Confidence</h1>
          <p>
            Upload weather forecasts and panel images to forecast solar production,
            plan maintenance, and maximize ROI across your solar portfolio.
          </p>
          <div className="landing-cta">
            {user ? (
              <Link to="/dashboard" className="btn btn-primary">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn btn-primary">
                  Login
                </Link>
                <Link to="/signup" className="btn btn-secondary">
                  Create Account
                </Link>
              </>
            )}
          </div>
        </div>
        <div className="landing-hero-card">
          <h3>Why Solar Analytics?</h3>
          <ul>
            <li>⚡ Hourly and daily production forecasts</li>
            <li>🛰️ Weather + image-driven predictions</li>
            <li>🔧 Maintenance alerts for panel health</li>
            <li>📈 Improved grid planning and ROI</li>
          </ul>
        </div>
      </header>

      <section className="landing-links">
        <Link to="/about" className="landing-link-card">
          <h3>About the Project</h3>
          <p>Learn how we support clean energy adoption with data-driven insights.</p>
        </Link>
        <Link to="/contact" className="landing-link-card">
          <h3>Contact</h3>
          <p>Need help or want to collaborate? Let’s connect.</p>
        </Link>
      </section>
    </div>
  );
}

export default Landing;

