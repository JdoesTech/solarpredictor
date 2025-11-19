"""
Model Trainer - Trains regression models for solar energy prediction
"""
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from django.conf import settings
from supabase import create_client, Client


class ModelTrainer:
    """
    Trains ML models for solar energy prediction
    """
    
    def __init__(self):
        self.models_dir = settings.ML_MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
    
    def _fetch_training_data(self):
        """
        Fetch weather and production data from Supabase for training
        """
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Get weather data
            weather_result = supabase.table('weather_data').select('*').order('timestamp').execute()
            weather_df = pd.DataFrame(weather_result.data) if weather_result.data else pd.DataFrame()
            
            # Get production data
            production_result = supabase.table('production_data').select('*').order('timestamp').execute()
            production_df = pd.DataFrame(production_result.data) if production_result.data else pd.DataFrame()
            
            if weather_df.empty or production_df.empty:
                return None, None
            
            # Merge on timestamp
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
            
            # Round timestamps to nearest hour for merging
            weather_df['timestamp_hour'] = weather_df['timestamp'].dt.floor('H')
            production_df['timestamp_hour'] = production_df['timestamp'].dt.floor('H')
            
            merged = pd.merge(
                weather_df,
                production_df,
                on='timestamp_hour',
                how='inner',
                suffixes=('_weather', '_production')
            )
            
            if merged.empty:
                return None, None
            
            # Prepare features
            feature_cols = [
                'temperature', 'humidity', 'wind_speed',
                'cloud_cover', 'solar_irradiance', 'precipitation'
            ]
            
            # Fill missing values
            for col in feature_cols:
                if col in merged.columns:
                    merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(merged[col].median())
            
            X = merged[feature_cols].values
            y = merged['energy_output_kwh'].values
            
            return X, y
            
        except Exception as e:
            print(f"Error fetching training data: {str(e)}")
            return None, None
    
    def train_model(self, model_type='regression'):
        """
        Train a regression model for solar energy prediction
        """
        try:
            # Fetch training data
            X, y = self._fetch_training_data()
            
            if X is None or y is None or len(X) == 0:
                # Generate synthetic data for demonstration
                print("No training data found, generating synthetic data...")
                n_samples = 1000
                X = np.random.rand(n_samples, 6) * np.array([40, 100, 20, 100, 1000, 50])
                y = (X[:, 4] * 0.5 + np.random.randn(n_samples) * 10).clip(0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            if model_type == 'regression':
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            version_name = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = os.path.join(self.models_dir, f"{version_name}.pkl")
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Save model metadata to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Deactivate old models
            supabase.table('model_versions').update({'is_active': False}).eq('model_type', model_type).execute()
            
            # Create new model version
            model_record = supabase.table('model_versions').insert({
                'version_name': version_name,
                'model_type': model_type,
                'file_path': model_path,
                'accuracy_score': float(r2),
                'mse': float(mse),
                'is_active': True,
                'training_data_start': datetime.now().isoformat(),
                'training_data_end': datetime.now().isoformat(),
            }).execute()
            
            return {
                'version_name': version_name,
                'mse': float(mse),
                'mae': float(mae),
                'r2_score': float(r2),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'model_path': model_path
            }
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            raise Exception(f"Training failed: {str(e)}")

