import React from 'react';
import './StaticPages.css';

function Contact() {
  return (
    <div className="static-page container">
      <div className="card">
        <h1>Contact</h1>
        <p>
          Have questions, feature ideas, or data partnerships to discuss? Reach out and we’ll respond
          within 2 business days.
        </p>

        <div className="contact-grid">
          <div>
            <h3>Email</h3>
            <p>
              <a href="mailto:hello@solarpredict.ai">hello@solarpredict.ai</a>
            </p>
          </div>
          <div>
            <h3>Community</h3>
            <p>
              Join the conversation on{' '}
              <a href="https://discord.gg/cleanenergy" target="_blank" rel="noreferrer">
                Discord
              </a>
            </p>
          </div>
          <div>
            <h3>Support</h3>
            <p>Support hours: Monday–Friday, 8AM–6PM UTC</p>
          </div>
        </div>

        <h2>Share Your Use Case</h2>
        <p>
          We’re building for grid operators, solar developers, and sustainability teams. Tell us how
          you plan to use the app so we can prioritize features that matter most.
        </p>
      </div>
    </div>
  );
}

export default Contact;


