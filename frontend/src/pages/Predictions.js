import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/auth';
import { getDailyPredictions, getHourlyPredictions } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Predictions() {
  const { token } = useAuth();
  const [predictionType, setPredictionType] = useState('daily');
  const [days, setDays] = useState(7);
  const [hours, setHours] = useState(24);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPredictions();
  }, [predictionType, days, hours]);

  const fetchPredictions = async () => {
    setLoading(true);
    setError('');

    try {
      let data;
      if (predictionType === 'daily') {
        data = await getDailyPredictions(days, token);
      } else {
        data = await getHourlyPredictions(hours, token);
      }
      setPredictions(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  const chartData = predictions.map((pred) => ({
    timestamp: new Date(pred.timestamp).toLocaleString(),
    output: pred.predicted_output_kwh,
    confidence: pred.confidence_score,
  }));

  return (
    <div className="container">
      <h1>Predictions</h1>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center' }}>
          <label>
            <input
              type="radio"
              value="daily"
              checked={predictionType === 'daily'}
              onChange={(e) => setPredictionType(e.target.value)}
            />
            Daily
          </label>
          <label>
            <input
              type="radio"
              value="hourly"
              checked={predictionType === 'hourly'}
              onChange={(e) => setPredictionType(e.target.value)}
            />
            Hourly
          </label>
          {predictionType === 'daily' && (
            <select value={days} onChange={(e) => setDays(parseInt(e.target.value))}>
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
            </select>
          )}
          {predictionType === 'hourly' && (
            <select value={hours} onChange={(e) => setHours(parseInt(e.target.value))}>
              <option value={24}>24 hours</option>
              <option value={48}>48 hours</option>
              <option value={72}>72 hours</option>
            </select>
          )}
        </div>

        {error && <div className="error">{error}</div>}

        {loading ? (
          <div className="loading">Loading predictions...</div>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="output" stroke="#4CAF50" name="Predicted Output (kWh)" />
              </LineChart>
            </ResponsiveContainer>

            <table className="table" style={{ marginTop: '2rem' }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Predicted Output (kWh)</th>
                  <th>Confidence Score</th>
                  <th>Model Version</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred, idx) => (
                  <tr key={idx}>
                    <td>{new Date(pred.timestamp).toLocaleString()}</td>
                    <td>{pred.predicted_output_kwh.toFixed(2)}</td>
                    <td>{(pred.confidence_score * 100).toFixed(1)}%</td>
                    <td>{pred.model_version || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  );
}

export default Predictions;

