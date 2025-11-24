import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/auth';
import { trainModel, getTrainingStatus } from '../services/api';

function Training() {
  const { token } = useAuth();
  const [modelType, setModelType] = useState('regression');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [trainingJobs, setTrainingJobs] = useState([]);

  useEffect(() => {
    fetchTrainingStatus();
  }, []);

  const fetchTrainingStatus = async () => {
    try {
      const jobs = await getTrainingStatus(token);
      setTrainingJobs(jobs);
    } catch (err) {
      console.error('Failed to fetch training status:', err);
    }
  };

  const handleTrain = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const result = await trainModel(modelType, token);
      setMessage(`Training completed! Model: ${result.version_name}, R² Score: ${result.results?.r2_score?.toFixed(4) || 'N/A'}`);
      fetchTrainingStatus();
    } catch (err) {
      setError(err.response?.data?.error || 'Training failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Model Training</h1>

      <div className="card">
        <h2>Train New Model</h2>
        <form onSubmit={handleTrain}>
          <div className="form-group">
            <label>Model Type</label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
            >
              <option value="regression">Regression (Random Forest)</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Training...' : 'Start Training'}
          </button>
        </form>

        {message && <div className="success">{message}</div>}
        {error && <div className="error">{error}</div>}
      </div>

      <div className="card">
        <h2>Training History</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Model Type</th>
              <th>Training Samples</th>
              <th>Started At</th>
              <th>Completed At</th>
            </tr>
          </thead>
          <tbody>
            {trainingJobs.map((job) => (
              <tr key={job.id}>
                <td>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    backgroundColor: job.status === 'completed' ? '#4CAF50' : 
                                   job.status === 'running' ? '#2196F3' : 
                                   job.status === 'failed' ? '#f44336' : '#ff9800',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}>
                    {job.status}
                  </span>
                </td>
                <td>{job.model_type}</td>
                <td>{job.training_data_count || 'N/A'}</td>
                <td>{job.started_at ? new Date(job.started_at).toLocaleString() : 'N/A'}</td>
                <td>{job.completed_at ? new Date(job.completed_at).toLocaleString() : 'N/A'}</td>
              </tr>
            ))}
            {trainingJobs.length === 0 && (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center' }}>No training jobs yet</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Training;


