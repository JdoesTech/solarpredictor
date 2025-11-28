import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

// Configurable timer (set to 0 or null to disable)
const AUTO_REDIRECT_SECONDS = 10; // Set to 0 to disable auto-redirect

function EmailConfirmation() {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(AUTO_REDIRECT_SECONDS);

  useEffect(() => {
    if (AUTO_REDIRECT_SECONDS > 0) {
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            navigate('/login');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [navigate]);

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>☀️ Solar Energy Prediction</h1>
        <h2>Check Your Email</h2>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📧</div>
          <p style={{ color: '#666', marginBottom: '1rem', lineHeight: '1.6' }}>
            We've sent a confirmation email to your inbox.
          </p>
          <p style={{ color: '#666', marginBottom: '1.5rem', lineHeight: '1.6' }}>
            Please click the confirmation link in the email to activate your account.
          </p>
          <p style={{ color: '#999', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Didn't receive the email? Check your spam folder or try signing up again.
          </p>
          {AUTO_REDIRECT_SECONDS > 0 && countdown > 0 && (
            <p style={{ color: '#667eea', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: '500' }}>
              Redirecting to login in {countdown} second{countdown !== 1 ? 's' : ''}...
            </p>
          )}
        </div>
        <Link to="/login" className="btn btn-primary" style={{ display: 'block', textAlign: 'center', textDecoration: 'none' }}>
          Go to Login
        </Link>
        <p className="login-note" style={{ marginTop: '1rem' }}>
          Already confirmed? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}

export default EmailConfirmation;

