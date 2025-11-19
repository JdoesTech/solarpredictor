"""
API Views for Solar Energy Prediction App
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from supabase import create_client, Client
import pandas as pd
import os
from datetime import datetime, timedelta
from .serializers import (
    WeatherDataSerializer,
    ProductionDataSerializer,
    PredictionSerializer,
    ImageUploadSerializer,
    TrainingJobSerializer
)
from ml_models.predictor import SolarEnergyPredictor
from ml_models.trainer import ModelTrainer
from data_processing.file_handler import FileHandler


class LoginView(APIView):
    """
    Login endpoint - delegates to Supabase Auth
    """
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return Response({
                    'token': response.session.access_token,
                    'user': {
                        'id': response.user.id,
                        'email': response.user.email
                    }
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class DashboardStatsView(APIView):
    """
    Dashboard statistics endpoint
    """
    def get(self, request):
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Get recent predictions
            predictions = supabase.table('predictions').select('*').order('timestamp', desc=True).limit(100).execute()
            
            # Get recent production data
            production = supabase.table('production_data').select('*').order('timestamp', desc=True).limit(100).execute()
            
            # Calculate stats
            total_predictions = len(predictions.data) if predictions.data else 0
            total_production = sum([p.get('energy_output_kwh', 0) for p in (production.data or [])])
            
            # Get active model
            active_model = supabase.table('model_versions').select('*').eq('is_active', True).limit(1).execute()
            
            return Response({
                'total_predictions': total_predictions,
                'total_production_kwh': total_production,
                'active_model': active_model.data[0] if active_model.data else None,
                'recent_predictions': predictions.data[:10] if predictions.data else [],
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WeatherUploadViewSet(viewsets.ViewSet):
    """
    Handle weather data CSV uploads
    """
    def create(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            handler = FileHandler()
            data = handler.process_weather_csv(file)
            
            # Save to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('weather_data').insert(data).execute()
            
            return Response({
                'message': f'Successfully uploaded {len(data)} weather records',
                'count': len(data)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductionUploadViewSet(viewsets.ViewSet):
    """
    Handle production data CSV uploads
    """
    def create(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            handler = FileHandler()
            data = handler.process_production_csv(file)
            
            # Save to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('production_data').insert(data).execute()
            
            return Response({
                'message': f'Successfully uploaded {len(data)} production records',
                'count': len(data)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ImageUploadViewSet(viewsets.ViewSet):
    """
    Handle solar panel image uploads
    """
    def create(self, request):
        files = request.FILES.getlist('images')
        if not files:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            handler = FileHandler()
            uploaded_files = []
            
            for file in files:
                file_path = handler.save_image(file)
                uploaded_files.append({
                    'filename': file.name,
                    'file_path': file_path,
                    'panel_id': request.data.get('panel_id', ''),
                    'uploaded_by': request.user.id if hasattr(request.user, 'id') else None,
                })
            
            # Save metadata to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('panel_images').insert(uploaded_files).execute()
            
            return Response({
                'message': f'Successfully uploaded {len(uploaded_files)} images',
                'files': uploaded_files
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PredictionViewSet(viewsets.ViewSet):
    """
    Handle predictions
    """
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily predictions"""
        try:
            days = int(request.query_params.get('days', 7))
            predictor = SolarEnergyPredictor()
            predictions = predictor.predict_daily(days=days)
            return Response(predictions)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def hourly(self, request):
        """Get hourly predictions"""
        try:
            hours = int(request.query_params.get('hours', 24))
            predictor = SolarEnergyPredictor()
            predictions = predictor.predict_hourly(hours=hours)
            return Response(predictions)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrainingViewSet(viewsets.ViewSet):
    """
    Handle model training
    """
    def create(self, request):
        """Start a training job"""
        try:
            model_type = request.data.get('model_type', 'regression')
            
            # Create training job record
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            job = supabase.table('training_jobs').insert({
                'status': 'pending',
                'model_type': model_type,
                'created_by': request.user.id if hasattr(request.user, 'id') else None,
            }).execute()
            
            # Start training (async in production)
            trainer = ModelTrainer()
            result = trainer.train_model(model_type=model_type)
            
            # Update job status
            supabase.table('training_jobs').update({
                'status': 'completed',
                'training_data_count': result.get('training_samples'),
                'completed_at': datetime.now().isoformat(),
            }).eq('id', job.data[0]['id']).execute()
            
            return Response({
                'message': 'Training completed',
                'job_id': job.data[0]['id'],
                'results': result
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get training job status"""
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            jobs = supabase.table('training_jobs').select('*').order('created_at', desc=True).limit(10).execute()
            return Response(jobs.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthViewSet(viewsets.ViewSet):
    """
    System health endpoint
    """
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get system health status"""
        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Check database connection
            db_status = 'healthy'
            try:
                supabase.table('weather_data').select('id').limit(1).execute()
            except:
                db_status = 'unhealthy'
            
            # Check model availability
            predictor = SolarEnergyPredictor()
            model_status = 'available' if predictor.model_loaded else 'not_loaded'
            
            return Response({
                'database': db_status,
                'model': model_status,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

