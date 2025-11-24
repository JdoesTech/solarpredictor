import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/auth';
import { getDashboardStats } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Dashboard() {
  const { token } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getDashboardStats(token);
      setStats(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading dashboard...</div></div>;
  }

  if (error) {
    return <div className="container"><div className="error">{error}</div></div>;
  }

  const chartData = stats?.recent_predictions?.map((pred) => ({
    timestamp: new Date(pred.timestamp).toLocaleDateString(),
    predicted: pred.predicted_output_kwh,
    actual: pred.actual_output_kwh || null,
  })) || [];

  return (
    <div className="container">
      <h1>Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card">
          <h3>Total Predictions</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4CAF50' }}>
            {stats?.total_predictions || 0}
          </p>
        </div>
        <div className="card">
          <h3>Total Production</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2196F3' }}>
            {stats?.total_production_kwh?.toFixed(2) || 0} kWh
          </p>
        </div>
        <div className="card">
          <h3>Active Model</h3>
          <p style={{ fontSize: '1rem', color: '#666' }}>
            {stats?.active_model?.version_name || 'No active model'}
          </p>
        </div>
      </div>

      <div className="card">
        <h2>Recent Predictions vs Actual</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="predicted" stroke="#4CAF50" name="Predicted" />
            <Line type="monotone" dataKey="actual" stroke="#2196F3" name="Actual" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Dashboard;


