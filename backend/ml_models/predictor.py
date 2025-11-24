"""
Solar Energy Predictor - Loads trained models and generates predictions
"""
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.conf import settings
from supabase import create_client, Client


class SolarEnergyPredictor:
    """
    Predicts solar energy output based on weather data
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_version = None
        self._load_model()
    
    def _load_model(self):
        """Load the active ML model"""
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('model_versions').select('*').eq('is_active', True).eq('model_type', 'regression').limit(1).execute()
            
            if result.data:
                model_info = result.data[0]
                model_path = model_info['file_path']
                
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    self.model_version = model_info['version_name']
                    self.model_loaded = True
                else:
                    print(f"Model file not found: {model_path}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # Use a simple default model for development
            self.model_loaded = False
    
    def _get_weather_features(self, timestamp):
        """
        Get weather features for a given timestamp
        Returns default values if no weather data available
        """
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('weather_data').select('*').eq('timestamp', timestamp.isoformat()).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                weather = result.data[0]
                return [
                    weather.get('temperature', 20.0),
                    weather.get('humidity', 50.0),
                    weather.get('wind_speed', 5.0),
                    weather.get('cloud_cover', 30.0),
                    weather.get('solar_irradiance', 500.0),
                    weather.get('precipitation', 0.0),
                ]
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
        
        # Default features (average conditions)
        return [20.0, 50.0, 5.0, 30.0, 500.0, 0.0]
    
    def predict_hourly(self, hours=24):
        """
        Generate hourly predictions for the next N hours
        """
        predictions = []
        now = datetime.now()
        
        for i in range(hours):
            timestamp = now + timedelta(hours=i)
            features = self._get_weather_features(timestamp)
            
            if self.model_loaded and self.model:
                # Use trained model
                prediction = self.model.predict([features])[0]
            else:
                # Simple heuristic: solar_irradiance * 0.5 (kW conversion factor)
                prediction = max(0, features[4] * 0.5)
            
            predictions.append({
                'timestamp': timestamp.isoformat(),
                'predicted_output_kwh': float(prediction),
                'confidence_score': 0.85 if self.model_loaded else 0.5,
                'model_version': self.model_version,
                'weather_features': {
                    'temperature': features[0],
                    'solar_irradiance': features[4],
                    'cloud_cover': features[3],
                }
            })
        
        return predictions
    
    def predict_daily(self, days=7):
        """
        Generate daily predictions for the next N days
        """
        predictions = []
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days):
            date = now + timedelta(days=i)
            # Get average weather for the day
            features = self._get_weather_features(date)
            
            if self.model_loaded and self.model:
                # Use trained model
                daily_prediction = self.model.predict([features])[0] * 24  # Convert hourly to daily
            else:
                # Simple heuristic
                daily_prediction = max(0, features[4] * 0.5 * 24)
            
            predictions.append({
                'timestamp': date.isoformat(),
                'predicted_output_kwh': float(daily_prediction),
                'confidence_score': 0.85 if self.model_loaded else 0.5,
                'model_version': self.model_version,
                'weather_features': {
                    'temperature': features[0],
                    'solar_irradiance': features[4],
                    'cloud_cover': features[3],
                }
            })
        
        return predictions


