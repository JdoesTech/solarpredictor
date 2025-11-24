import React from 'react';
import './StaticPages.css';

function About() {
  return (
    <div className="static-page container">
      <div className="card">
        <h1>About Solar Energy Prediction</h1>
        <p>
          Our platform helps energy teams forecast solar output by combining weather intelligence,
          historical generation data, and the current condition of solar arrays. Accurate forecasts
          translate to better grid planning, fewer unplanned outages, and higher returns on clean
          energy investments.
        </p>

        <h2>What You Can Do</h2>
        <ul>
          <li>Upload weather and production datasets to train custom ML models.</li>
          <li>Analyze daily and hourly production forecasts to plan dispatch.</li>
          <li>Monitor panel health through image uploads and condition scoring.</li>
          <li>Track training jobs, model versions, and overall system status.</li>
        </ul>

        <h2>Why It Matters</h2>
        <p>
          Solar adoption is growing, but grid operators still struggle to integrate intermittent
          renewables. Better forecasting empowers operators to plan ahead, avoid curtailment, and
          keep the lights on using affordable, clean energy—advancing SDG 7.
        </p>
      </div>
    </div>
  );
}

export default About;


