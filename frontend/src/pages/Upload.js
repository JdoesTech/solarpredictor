import React, { useState } from 'react';
import { useAuth } from '../services/auth';
import { uploadWeatherCSV, uploadProductionCSV, uploadImages } from '../services/api';
import { useDropzone } from 'react-dropzone';

function Upload() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('weather');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [panelId, setPanelId] = useState('');

  const handleWeatherUpload = async (files) => {
    if (files.length === 0) return;
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const result = await uploadWeatherCSV(files[0], token);
      setMessage(`Successfully uploaded ${result.count} weather records`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleProductionUpload = async (files) => {
    if (files.length === 0) return;
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const result = await uploadProductionCSV(files[0], token);
      setMessage(`Successfully uploaded ${result.count} production records`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (files) => {
    if (files.length === 0) return;
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const result = await uploadImages(files, panelId, token);
      setMessage(`Successfully uploaded ${result.files?.length || 0} images`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const WeatherDropzone = () => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      accept: { 'text/csv': ['.csv'] },
      onDrop: handleWeatherUpload,
      multiple: false,
    });

    return (
      <div {...getRootProps()} className="dropzone" style={{ 
        border: '2px dashed #ccc', 
        padding: '2rem', 
        textAlign: 'center', 
        cursor: 'pointer',
        borderRadius: '8px',
        backgroundColor: isDragActive ? '#f0f0f0' : 'white'
      }}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the CSV file here...</p>
        ) : (
          <p>Drag & drop a weather CSV file here, or click to select</p>
        )}
      </div>
    );
  };

  const ProductionDropzone = () => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      accept: { 'text/csv': ['.csv'] },
      onDrop: handleProductionUpload,
      multiple: false,
    });

    return (
      <div {...getRootProps()} className="dropzone" style={{ 
        border: '2px dashed #ccc', 
        padding: '2rem', 
        textAlign: 'center', 
        cursor: 'pointer',
        borderRadius: '8px',
        backgroundColor: isDragActive ? '#f0f0f0' : 'white'
      }}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the CSV file here...</p>
        ) : (
          <p>Drag & drop a production CSV file here, or click to select</p>
        )}
      </div>
    );
  };

  const ImageDropzone = () => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      accept: { 'image/*': ['.jpg', '.jpeg', '.png'] },
      onDrop: handleImageUpload,
      multiple: true,
    });

    return (
      <div {...getRootProps()} className="dropzone" style={{ 
        border: '2px dashed #ccc', 
        padding: '2rem', 
        textAlign: 'center', 
        cursor: 'pointer',
        borderRadius: '8px',
        backgroundColor: isDragActive ? '#f0f0f0' : 'white'
      }}>
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the images here...</p>
        ) : (
          <p>Drag & drop panel images here, or click to select</p>
        )}
      </div>
    );
  };

  return (
    <div className="container">
      <h1>Upload Data</h1>

      <div className="info-banner">
        <strong>Optional ingestion.</strong>
        The platform already serves dashboards from trained datasets. Use these uploaders only
        when you have vetted CSVs or imagery that should influence the next training cycle.
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #ddd' }}>
        <button
          className={`btn ${activeTab === 'weather' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('weather')}
        >
          Weather Data
        </button>
        <button
          className={`btn ${activeTab === 'production' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('production')}
        >
          Production Data
        </button>
        <button
          className={`btn ${activeTab === 'images' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('images')}
        >
          Panel Images
        </button>
      </div>

      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}

      <div className="card">
        {activeTab === 'weather' && (
          <div>
            <h2>Upload Weather CSV</h2>
            <p>Expected columns: timestamp, temperature, humidity, wind_speed, cloud_cover, solar_irradiance, precipitation</p>
            <WeatherDropzone />
          </div>
        )}

        {activeTab === 'production' && (
          <div>
            <h2>Upload Production CSV</h2>
            <p>Expected columns: timestamp, energy_output_kwh, panel_id (optional), system_capacity_kw (optional)</p>
            <ProductionDropzone />
          </div>
        )}

        {activeTab === 'images' && (
          <div>
            <h2>Upload Panel Images</h2>
            <div className="form-group">
              <label>Panel ID (optional)</label>
              <input
                type="text"
                value={panelId}
                onChange={(e) => setPanelId(e.target.value)}
                placeholder="Enter panel ID"
              />
            </div>
            <ImageDropzone />
          </div>
        )}
      </div>

      {loading && <div className="loading">Uploading...</div>}
    </div>
  );
}

export default Upload;



