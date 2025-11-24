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
            The platform streams insights from our curated, trained models so you can
            monitor generation, health, and risk without rebuilding pipelines every time.
            Uploads are still available when you want to expand the data set, but the UI
            defaults to production-ready intelligence.
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
            <li>⚡ Hourly and daily production forecasts from trained data</li>
            <li>🛰️ Weather + image-driven predictions, ready to consume</li>
            <li>🔧 Maintenance alerts for panel health</li>
            <li>📈 Improved grid planning and ROI</li>
          </ul>
        </div>
      </header>

      <section className="landing-data-focus">
        <div className="landing-data-card">
          <h3>Pre-trained Intelligence</h3>
          <p>
            Dashboards, predictions, and health checks read directly from vetted model
            outputs stored in Supabase. Stay confident that stakeholders see the same
            trained truth everywhere in the app.
          </p>
        </div>
        <div className="landing-data-card">
          <h3>Optional Data Expansion</h3>
          <p>
            Need to push new CSVs or imagery? Upload flows and retraining remain available,
            but your analysts can focus on consuming results, not feeding pipelines.
          </p>
        </div>
      </section>

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


