import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/auth';
import { getHealthStatus } from '../services/api';

function Health() {
  const { token } = useAuth();
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchHealth = async () => {
    try {
      const data = await getHealthStatus(token);
      setHealth(data);
    } catch (err) {
      setError('Failed to fetch health status');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading health status...</div></div>;
  }

  const getStatusColor = (status) => {
    return status === 'healthy' || status === 'available' ? '#4CAF50' : '#f44336';
  };

  return (
    <div className="container">
      <h1>System Health</h1>

      {error && <div className="error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        <div className="card">
          <h2>Database</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              backgroundColor: getStatusColor(health?.database)
            }}></div>
            <span style={{ textTransform: 'capitalize', fontSize: '1.2rem' }}>
              {health?.database || 'Unknown'}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>ML Model</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              backgroundColor: getStatusColor(health?.model)
            }}></div>
            <span style={{ textTransform: 'capitalize', fontSize: '1.2rem' }}>
              {health?.model || 'Unknown'}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>Last Check</h2>
          <p style={{ fontSize: '1rem', color: '#666' }}>
            {health?.timestamp ? new Date(health.timestamp).toLocaleString() : 'N/A'}
          </p>
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h2>System Information</h2>
        <p>This panel shows the health status of various system components.</p>
        <ul style={{ marginTop: '1rem', lineHeight: '1.8' }}>
          <li><strong>Database:</strong> Connection status to Supabase PostgreSQL</li>
          <li><strong>ML Model:</strong> Availability of trained prediction models</li>
          <li><strong>Last Check:</strong> Timestamp of the last health check</li>
        </ul>
      </div>
    </div>
  );
}

export default Health;


