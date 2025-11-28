"""
File Handler - Processes uploaded CSV, XLSX, PDF and image files
"""
import os
import pandas as pd
from datetime import datetime
from django.conf import settings
from PIL import Image
import pdfplumber
import io


class FileHandler:
    """
    Handles file uploads and processing
    Supports: CSV, XLSX, PDF files up to 20MB
    """
    
    MAX_FILE_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE', 20 * 1024 * 1024)  # 20MB
    ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.pdf']
    
    def __init__(self):
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        self.image_dir = os.path.join(settings.MEDIA_ROOT, 'images')
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
    
    def _validate_file(self, file):
        """
        Validate file size and extension
        """
        # Check file size
        if hasattr(file, 'size') and file.size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.0f}MB")
        
        # Check file extension
        filename = file.name.lower()
        if not any(filename.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise ValueError(f"File type not supported. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        return True
    
    def _read_dataframe(self, file):
        """
        Read file into pandas DataFrame based on file extension
        """
        filename = file.name.lower()
        
        # Reset file pointer
        if hasattr(file, 'seek'):
            file.seek(0)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file, engine='openpyxl')
            elif filename.endswith('.pdf'):
                # Extract tables from PDF
                df = self._extract_pdf_tables(file)
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            return df
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    def _extract_pdf_tables(self, file):
        """
        Extract tables from PDF file using pdfplumber
        """
        try:
            # Reset file pointer
            file.seek(0)
            
            # Read PDF
            with pdfplumber.open(file) as pdf:
                all_tables = []
                
                # Extract tables from each page
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                
                if not all_tables:
                    raise ValueError("No tables found in PDF. Please ensure the PDF contains tabular data.")
                
                # Use the first table (or merge all tables if needed)
                # For now, we'll use the largest table
                largest_table = max(all_tables, key=len)
                
                # Convert to DataFrame
                if len(largest_table) > 1:
                    # First row as header
                    df = pd.DataFrame(largest_table[1:], columns=largest_table[0])
                else:
                    raise ValueError("PDF table is empty or has no data rows")
                
                return df
        except Exception as e:
            raise Exception(f"Error extracting PDF tables: {str(e)}. Please ensure the PDF contains readable tabular data.")
    
    def process_weather_csv(self, file):
        """
        Process weather data file (CSV, XLSX, or PDF)
        Expected columns: timestamp, temperature, humidity, wind_speed, 
                         cloud_cover, solar_irradiance, precipitation, is_forecast, location
        """
        try:
            # Validate file
            self._validate_file(file)
            
            # Read file into DataFrame
            df = self._read_dataframe(file)
            
            # Validate required columns
            required_cols = ['timestamp']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"File must contain columns: {', '.join(required_cols)}. Found columns: {', '.join(df.columns.tolist())}")
            
            # Convert timestamp to ISO format
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            if df['timestamp'].isna().any():
                raise ValueError("Invalid timestamp format. Please ensure timestamps are in a recognizable date/time format.")
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            
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
            raise Exception(f"Error processing weather file: {str(e)}")
    
    def process_production_csv(self, file):
        """
        Process production data file (CSV, XLSX, or PDF)
        Expected columns: timestamp, energy_output_kwh, panel_id, 
                         system_capacity_kw, efficiency
        """
        try:
            # Validate file
            self._validate_file(file)
            
            # Read file into DataFrame
            df = self._read_dataframe(file)
            
            # Validate required columns
            if 'timestamp' not in df.columns or 'energy_output_kwh' not in df.columns:
                raise ValueError(f"File must contain 'timestamp' and 'energy_output_kwh' columns. Found columns: {', '.join(df.columns.tolist())}")
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            if df['timestamp'].isna().any():
                raise ValueError("Invalid timestamp format. Please ensure timestamps are in a recognizable date/time format.")
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            
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
            raise Exception(f"Error processing production file: {str(e)}")
    
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



