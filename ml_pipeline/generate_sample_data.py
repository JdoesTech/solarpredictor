"""
Generate sample CSV files for testing the application
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_weather_data(start_date='2024-01-01', days=365, filename='weather_data.csv'):
    """Generate synthetic weather data"""
    dates = pd.date_range(start=start_date, periods=days*24, freq='H')
    
    # Generate realistic weather patterns
    base_temp = 20
    temp_variation = 10 * np.sin(np.arange(len(dates)) * 2 * np.pi / (365*24))  # Seasonal variation
    hourly_variation = 5 * np.sin(np.arange(len(dates)) * 2 * np.pi / 24)  # Daily variation
    
    weather_data = pd.DataFrame({
        'timestamp': dates.strftime('%Y-%m-%dT%H:%M:%S'),
        'temperature': (base_temp + temp_variation + hourly_variation + np.random.randn(len(dates)) * 3).clip(0, 40),
        'humidity': (50 + 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / 24) + np.random.randn(len(dates)) * 10).clip(0, 100),
        'wind_speed': (5 + 3 * np.random.randn(len(dates))).clip(0, 20),
        'cloud_cover': (30 + 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / 24) + np.random.randn(len(dates)) * 15).clip(0, 100),
        'solar_irradiance': (500 + 300 * np.sin(np.arange(len(dates)) * 2 * np.pi / 24) + np.random.randn(len(dates)) * 50).clip(0, 1000),
        'precipitation': np.random.exponential(0.5, len(dates)).clip(0, 50),
        'is_forecast': False,
        'location': 'Solar Farm A'
    })
    
    weather_data.to_csv(filename, index=False)
    print(f"Generated {len(weather_data)} weather records in {filename}")
    return weather_data

def generate_production_data(start_date='2024-01-01', days=365, filename='production_data.csv'):
    """Generate synthetic production data based on weather patterns"""
    dates = pd.date_range(start=start_date, periods=days*24, freq='H')
    
    # Generate production based on solar irradiance pattern
    base_irradiance = 500 + 300 * np.sin(np.arange(len(dates)) * 2 * np.pi / 24)
    production = (base_irradiance * 0.2 + np.random.randn(len(dates)) * 10).clip(0)
    
    production_data = pd.DataFrame({
        'timestamp': dates.strftime('%Y-%m-%dT%H:%M:%S'),
        'energy_output_kwh': production,
        'panel_id': 'panel_001',
        'system_capacity_kw': 10.0,
        'efficiency': 20.0
    })
    
    production_data.to_csv(filename, index=False)
    print(f"Generated {len(production_data)} production records in {filename}")
    return production_data

if __name__ == '__main__':
    print("Generating sample data files...")
    print("=" * 50)
    
    weather_df = generate_weather_data()
    production_df = generate_production_data()
    
    print("=" * 50)
    print("Sample data files created!")
    print("\nYou can now upload these files via the Upload page in the web app.")
    print("Or use the API:")
    print("  curl -X POST http://localhost:8000/api/upload/weather/ \\")
    print("    -H 'Authorization: Bearer <token>' \\")
    print("    -F 'file=@weather_data.csv'")



