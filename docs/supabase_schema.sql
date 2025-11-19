-- Supabase Database Schema for Solar Energy Prediction App
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Weather Data Table
CREATE TABLE IF NOT EXISTS weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    wind_speed DECIMAL(5,2),
    cloud_cover DECIMAL(5,2),
    solar_irradiance DECIMAL(8,2),
    precipitation DECIMAL(5,2),
    is_forecast BOOLEAN DEFAULT FALSE,
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Production Data Table
CREATE TABLE IF NOT EXISTS production_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL,
    energy_output_kwh DECIMAL(10,2) NOT NULL,
    panel_id VARCHAR(50),
    system_capacity_kw DECIMAL(8,2),
    efficiency DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_type VARCHAR(20) NOT NULL CHECK (prediction_type IN ('hourly', 'daily')),
    timestamp TIMESTAMP NOT NULL,
    predicted_output_kwh DECIMAL(10,2) NOT NULL,
    confidence_score DECIMAL(5,2),
    model_version VARCHAR(50),
    weather_data_id UUID REFERENCES weather_data(id) ON DELETE SET NULL,
    actual_output_kwh DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Panel Images Table
CREATE TABLE IF NOT EXISTS panel_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    panel_id VARCHAR(50),
    condition_score DECIMAL(5,2) CHECK (condition_score >= 0 AND condition_score <= 100),
    condition_status VARCHAR(20) CHECK (condition_status IN ('excellent', 'good', 'fair', 'poor')),
    uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    analyzed_at TIMESTAMP
);

-- Model Versions Table
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_name VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('regression', 'cnn')),
    file_path VARCHAR(500) NOT NULL,
    training_data_start TIMESTAMP,
    training_data_end TIMESTAMP,
    accuracy_score DECIMAL(5,4) CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    mse DECIMAL(10,4),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- Training Jobs Table
CREATE TABLE IF NOT EXISTS training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    model_type VARCHAR(50),
    training_data_count INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_forecast ON weather_data(is_forecast);
CREATE INDEX IF NOT EXISTS idx_production_timestamp ON production_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_panel_images_panel_id ON panel_images(panel_id);
CREATE INDEX IF NOT EXISTS idx_model_versions_active ON model_versions(is_active);
CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for weather_data updated_at
CREATE TRIGGER update_weather_data_updated_at BEFORE UPDATE ON weather_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE weather_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE panel_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_jobs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read all data
CREATE POLICY "Users can read weather_data" ON weather_data FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can read production_data" ON production_data FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can read predictions" ON predictions FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can read panel_images" ON panel_images FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can read model_versions" ON model_versions FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can read training_jobs" ON training_jobs FOR SELECT USING (auth.role() = 'authenticated');

-- Policy: Users can insert their own data
CREATE POLICY "Users can insert weather_data" ON weather_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can insert production_data" ON production_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can insert predictions" ON predictions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can insert panel_images" ON panel_images FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can insert model_versions" ON model_versions FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can insert training_jobs" ON training_jobs FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Policy: Users can update their own data
CREATE POLICY "Users can update weather_data" ON weather_data FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update production_data" ON production_data FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update predictions" ON predictions FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update panel_images" ON panel_images FOR UPDATE USING (uploaded_by = auth.uid());
CREATE POLICY "Users can update model_versions" ON model_versions FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Users can update training_jobs" ON training_jobs FOR UPDATE USING (auth.role() = 'authenticated');

