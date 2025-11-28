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

  const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB
  const ALLOWED_FILE_TYPES = {
    'text/csv': ['.csv'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/pdf': ['.pdf']
  };

  const validateFile = (file) => {
    if (file.size > MAX_FILE_SIZE) {
      throw new Error(`File size exceeds 20MB limit. File size: ${(file.size / (1024 * 1024)).toFixed(2)}MB`);
    }
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.pdf'];
    
    if (!allowedExtensions.includes(fileExtension)) {
      throw new Error(`File type not supported. Allowed types: CSV, XLSX, XLS, PDF`);
    }
    
    return true;
  };

  const handleWeatherUpload = async (files) => {
    if (files.length === 0) return;
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const file = files[0];
      validateFile(file);
      const result = await uploadWeatherCSV(file, token);
      setMessage(`Successfully uploaded ${result.count} weather records from ${result.file_type || 'file'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.details || err.response?.data?.error || err.message || 'Upload failed';
      setError(errorMsg);
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
      const file = files[0];
      validateFile(file);
      const result = await uploadProductionCSV(file, token);
      setMessage(`Successfully uploaded ${result.count} production records from ${result.file_type || 'file'}`);
    } catch (err) {
      const errorMsg = err.response?.data?.details || err.response?.data?.error || err.message || 'Upload failed';
      setError(errorMsg);
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
      accept: ALLOWED_FILE_TYPES,
      onDrop: handleWeatherUpload,
      multiple: false,
      maxSize: MAX_FILE_SIZE,
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
          <p>Drop the file here...</p>
        ) : (
          <div>
            <p>Drag & drop a weather data file here, or click to select</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              Supported formats: CSV, XLSX, XLS, PDF (Max 20MB)
            </p>
          </div>
        )}
      </div>
    );
  };

  const ProductionDropzone = () => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      accept: ALLOWED_FILE_TYPES,
      onDrop: handleProductionUpload,
      multiple: false,
      maxSize: MAX_FILE_SIZE,
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
          <p>Drop the file here...</p>
        ) : (
          <div>
            <p>Drag & drop a production data file here, or click to select</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              Supported formats: CSV, XLSX, XLS, PDF (Max 20MB)
            </p>
          </div>
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
            <h2>Upload Weather Data</h2>
            <p>Expected columns: timestamp, temperature, humidity, wind_speed, cloud_cover, solar_irradiance, precipitation</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              <strong>Supported file formats:</strong> CSV, XLSX, XLS, PDF (Maximum file size: 20MB)
            </p>
            <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem', fontStyle: 'italic' }}>
              Note: PDF files should contain tabular data. The system will extract the first table found.
            </p>
            <WeatherDropzone />
          </div>
        )}

        {activeTab === 'production' && (
          <div>
            <h2>Upload Production Data</h2>
            <p>Expected columns: timestamp, energy_output_kwh, panel_id (optional), system_capacity_kw (optional)</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              <strong>Supported file formats:</strong> CSV, XLSX, XLS, PDF (Maximum file size: 20MB)
            </p>
            <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem', fontStyle: 'italic' }}>
              Note: PDF files should contain tabular data. The system will extract the first table found.
            </p>
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



