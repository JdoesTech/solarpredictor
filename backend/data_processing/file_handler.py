"""
File Handler - Processes uploaded CSV and image files
"""
import os
import pandas as pd
from datetime import datetime
from django.conf import settings
from PIL import Image


class FileHandler:
    """
    Handles file uploads and processing
    """
    
    def __init__(self):
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        self.image_dir = os.path.join(settings.MEDIA_ROOT, 'images')
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
    
    def process_weather_csv(self, file):
        """
        Process weather data CSV file
        Expected columns: timestamp, temperature, humidity, wind_speed, 
                         cloud_cover, solar_irradiance, precipitation, is_forecast, location
        """
        try:
            df = pd.read_csv(file)
            
            # Validate required columns
            required_cols = ['timestamp']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"CSV must contain columns: {', '.join(required_cols)}")
            
            # Convert timestamp to ISO format
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Fill missing values
            numeric_cols = ['temperature', 'humidity', 'wind_speed', 'cloud_cover', 
                          'solar_irradiance', 'precipitation']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Convert to dict format for Supabase
            records = df.to_dict('records')
            
            # Clean up None values
            for record in records:
                record = {k: v for k, v in record.items() if pd.notna(v)}
            
            return records
            
        except Exception as e:
            raise Exception(f"Error processing weather CSV: {str(e)}")
    
    def process_production_csv(self, file):
        """
        Process production data CSV file
        Expected columns: timestamp, energy_output_kwh, panel_id, 
                         system_capacity_kw, efficiency
        """
        try:
            df = pd.read_csv(file)
            
            # Validate required columns
            if 'timestamp' not in df.columns or 'energy_output_kwh' not in df.columns:
                raise ValueError("CSV must contain 'timestamp' and 'energy_output_kwh' columns")
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Validate energy output
            df['energy_output_kwh'] = pd.to_numeric(df['energy_output_kwh'], errors='coerce')
            if df['energy_output_kwh'].isna().any():
                raise ValueError("energy_output_kwh must be numeric")
            
            # Fill optional columns
            if 'system_capacity_kw' in df.columns:
                df['system_capacity_kw'] = pd.to_numeric(df['system_capacity_kw'], errors='coerce')
            if 'efficiency' in df.columns:
                df['efficiency'] = pd.to_numeric(df['efficiency'], errors='coerce')
            
            # Convert to dict format
            records = df.to_dict('records')
            
            # Clean up None values
            for record in records:
                record = {k: v for k, v in record.items() if pd.notna(v)}
            
            return records
            
        except Exception as e:
            raise Exception(f"Error processing production CSV: {str(e)}")
    
    def save_image(self, file):
        """
        Save uploaded image file and return file path
        """
        try:
            # Validate image
            img = Image.open(file)
            img.verify()
            
            # Reset file pointer
            file.seek(0)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.name}"
            file_path = os.path.join(self.image_dir, filename)
            
            # Save image
            img = Image.open(file)
            img.save(file_path)
            
            # Return relative path
            return os.path.join('images', filename)
            
        except Exception as e:
            raise Exception(f"Error saving image: {str(e)}")


