"""
API Views for Solar Energy Prediction App
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.conf import settings
from supabase import create_client, Client
import os
import time
import copy
import requests
from threading import Lock
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


SOLCAST_API_KEY = getattr(settings, 'SOLCAST_API_KEY', '')
SOLCAST_CACHE_TTL = getattr(settings, 'SOLCAST_CACHE_TTL_SECONDS', 900)
SOLCAST_MAX_HOURS = getattr(settings, 'SOLCAST_MAX_HOURS', 336)
SOLCAST_BASE_URL = getattr(settings, 'SOLCAST_BASE_URL', '')
NOMINATIM_BASE_URL = getattr(settings, 'NOMINATIM_BASE_URL', '')
NOMINATIM_RATE_LIMIT_SECONDS = getattr(settings, 'NOMINATIM_RATE_LIMIT_SECONDS', 1.0)

_solcast_cache = {}
_solcast_cache_lock = Lock()
_nominatim_lock = Lock()
_nominatim_last_call = 0.0


def _round_coord(value: float) -> float:
    return round(value, 4)


def _solcast_cache_key(lat: float, lon: float) -> str:
    return f"{_round_coord(lat)}:{_round_coord(lon)}"


def _get_cached_forecast(lat: float, lon: float):
    if not SOLCAST_CACHE_TTL:
        return None

    cache_key = _solcast_cache_key(lat, lon)
    with _solcast_cache_lock:
        cached = _solcast_cache.get(cache_key)
        if cached and cached['expires_at'] > time.time():
            return cached
        if cached:
            # Expired entry, clean it up
            _solcast_cache.pop(cache_key, None)
    return None


def _store_forecast_in_cache(lat: float, lon: float, data: dict):
    if not SOLCAST_CACHE_TTL:
        return
    cache_key = _solcast_cache_key(lat, lon)
    with _solcast_cache_lock:
        _solcast_cache[cache_key] = {
            'data': data,
            'expires_at': time.time() + SOLCAST_CACHE_TTL,
        }


def _enforce_nominatim_rate_limit():
    global _nominatim_last_call
    with _nominatim_lock:
        elapsed = time.monotonic() - _nominatim_last_call
        wait_time = NOMINATIM_RATE_LIMIT_SECONDS - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        _nominatim_last_call = time.monotonic()


def _call_nominatim(endpoint: str, params: dict):
    if not NOMINATIM_BASE_URL:
        raise RuntimeError('Nominatim base URL is not configured')

    _enforce_nominatim_rate_limit()
    headers = {
        'User-Agent': getattr(settings, 'NOMINATIM_USER_AGENT', 'SolarForecastDashboard/1.0')
    }
    if getattr(settings, 'NOMINATIM_EMAIL', ''):
        params['email'] = settings.NOMINATIM_EMAIL

    response = requests.get(
        f"{NOMINATIM_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}",
        params=params,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _reverse_geocode(lat: float, lon: float):
    try:
        data = _call_nominatim(
            'reverse',
            {
                'lat': lat,
                'lon': lon,
                'format': 'jsonv2',
                'zoom': 10,
                'addressdetails': 1,
            },
        )
        address = data.get('address', {})
        return {
            'display_name': data.get('display_name'),
            'city': address.get('city') or address.get('town') or address.get('village'),
            'country': address.get('country'),
        }
    except Exception:
        return {
            'display_name': None,
            'city': None,
            'country': None,
        }


def _search_locations(query: str):
    try:
        data = _call_nominatim(
            'search',
            {
                'q': query,
                'format': 'jsonv2',
                'limit': 5,
                'addressdetails': 1,
            },
        )
        results = []
        for item in data:
            address = item.get('address', {})
            results.append({
                'display_name': item.get('display_name'),
                'lat': float(item.get('lat')),
                'lon': float(item.get('lon')),
                'city': address.get('city') or address.get('town') or address.get('village'),
                'country': address.get('country'),
            })
        return results
    except Exception:
        return []


def _estimate_pv_power_kw(entry: dict):
    ghi = entry.get('ghi')
    if ghi is None:
        return None
    # Convert W/m2 to kW for a 1 kWp system with 20% efficiency
    return round((ghi * 0.2) / 1000, 3)


def _summarize_daily_energy(forecasts: list, days: int = 7):
    daily_totals = {}
    for item in forecasts:
        period_end = item.get('period_end')
        if not period_end:
            continue
        day_key = period_end.split('T')[0]
        ghi = item.get('ghi')
        if ghi is None:
            continue
        daily_totals.setdefault(day_key, 0)
        daily_totals[day_key] += ghi / 1000  # Convert W/m2 to kWh/m2 per hour
    summary = []
    for day in sorted(daily_totals.keys())[:days]:
        summary.append({
            'date': day,
            'kwh_per_m2': round(daily_totals[day], 2),
        })
    return summary


def _fetch_solcast_forecast(lat: float, lon: float):
    if not SOLCAST_BASE_URL or not SOLCAST_API_KEY:
        raise RuntimeError('Solcast API is not configured. Set SOLCAST_BASE_URL and SOLCAST_API_KEY.')

    params = {
        'latitude': lat,
        'longitude': lon,
        'format': 'json',
        'api_key': SOLCAST_API_KEY,
        'hours': min(SOLCAST_MAX_HOURS, 336),
    }

    response = requests.get(
        SOLCAST_BASE_URL,
        params=params,
        headers={'Accept': 'application/json'},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    forecasts = data.get('forecasts') or data.get('radiation') or []
    if not forecasts:
        raise ValueError('Solcast response did not include forecast data.')
    return forecasts


def _build_forecast_payload(lat: float, lon: float, forecasts: list):
    location_meta = _reverse_geocode(lat, lon)
    hourly = []
    for entry in forecasts[:48]:
        pv_kw = _estimate_pv_power_kw(entry)
        hourly.append({
            'time': entry.get('period_end'),
            'ghi': entry.get('ghi'),
            'pv_kw': pv_kw,
            'air_temp': entry.get('air_temp'),
            'cloud_opacity': entry.get('cloud_opacity'),
        })

    current_entry = forecasts[0] if forecasts else {}
    summary = _summarize_daily_energy(forecasts, days=7)

    return {
        'location': {
            'lat': lat,
            'lon': lon,
            'display_name': location_meta.get('display_name'),
            'city': location_meta.get('city'),
            'country': location_meta.get('country'),
        },
        'current_conditions': {
            'ghi': current_entry.get('ghi'),
            'air_temp': current_entry.get('air_temp'),
            'cloud_opacity': current_entry.get('cloud_opacity'),
            'period_end': current_entry.get('period_end'),
        } if current_entry else {},
        'hourly_forecast': [entry for entry in hourly if entry.get('time')],
        'daily_summary': summary,
        'forecast_length': min(len(forecasts), SOLCAST_MAX_HOURS),
    }

class LoginView(APIView):
    """
    Login endpoint - delegates to Supabase Auth
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
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


class SolarForecastProxy(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        print(f"SOLAR FORECAST CALLED: {request.query_params}")
        
        lat_str = request.query_params.get('lat')
        lon_str = request.query_params.get('lon')
        
        print(f"RAW COORDS: lat='{lat_str}', lon='{lon_str}'")
        
        # Validate parameters are provided
        if not lat_str or not lon_str:
            print("ERROR: Missing lat/lon")
            return Response(
                {'error': 'Missing required parameters', 'details': 'Both lat and lon query parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and parse coordinates
        try:
            lat = float(lat_str)
            lon = float(lon_str)
            print(f"PARSED: lat={lat}, lon={lon}")
        except (ValueError, TypeError) as e:
            print(f"ERROR: Invalid coordinate format lat='{lat_str}', lon='{lon_str}'")
            return Response(
                {
                    'error': 'Invalid coordinate format',
                    'details': f'Could not parse coordinates: lat="{lat_str}", lon="{lon_str}". Expected numeric values.',
                    'received': {'lat': lat_str, 'lon': lon_str}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            print(f"ERROR: Latitude out of range: {lat}")
            return Response(
                {
                    'error': 'Latitude out of valid range',
                    'details': f'Latitude must be between -90 and 90 degrees. Received: {lat}',
                    'received': lat,
                    'valid_range': {'min': -90, 'max': 90}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not (-180 <= lon <= 180):
            print(f"ERROR: Longitude out of range: {lon}")
            return Response(
                {
                    'error': 'Longitude out of valid range',
                    'details': f'Longitude must be between -180 and 180 degrees. Received: {lon}',
                    'received': lon,
                    'valid_range': {'min': -180, 'max': 180}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate API key is configured
        SOLCAST_KEY = os.getenv('SOLCAST_API_KEY', '')
        if not SOLCAST_KEY:
            print("ERROR: No SOLCAST_API_KEY configured")
            return Response(
                {
                    'error': 'Solcast API key not configured',
                    'details': 'The SOLCAST_API_KEY environment variable is not set on the server'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check cache first
        try:
            cached = _get_cached_forecast(lat, lon)
            if cached:
                print(f"CACHE HIT for {lat}, {lon}")
                payload = copy.deepcopy(cached['data'])
                payload['cache'] = {
                    'source': 'cache',
                    'expires_at': datetime.utcfromtimestamp(cached['expires_at']).isoformat() + 'Z',
                }
                return Response(payload)
        except Exception as e:
            print(f"WARNING: Cache retrieval failed: {type(e).__name__}: {e}")
            # Continue to fetch fresh data if cache fails
        
        # Fetch fresh forecast data
        try:
            forecasts = _fetch_solcast_forecast(lat, lon)
            print(f"SOLCAST SUCCESS: {len(forecasts)} forecasts retrieved")
            
            # Build the payload using the helper function
            payload = _build_forecast_payload(lat, lon, forecasts)
            payload['cache'] = {
                'source': 'origin',
                'expires_at': (datetime.utcnow() + timedelta(seconds=SOLCAST_CACHE_TTL)).isoformat() + 'Z',
            }
            
            # Store in cache (use deepcopy to avoid reference issues)
            try:
                _store_forecast_in_cache(lat, lon, copy.deepcopy(payload))
            except Exception as e:
                print(f"WARNING: Cache storage failed: {type(e).__name__}: {e}")
                # Continue even if cache storage fails
            
            return Response(payload)
            
        except requests.HTTPError as exc:
            print(f"SOLCAST HTTP ERROR: {exc.response.status_code if exc.response else 'No response'}: {exc}")
            error_details = {
                'error': 'Solcast API request failed',
                'details': str(exc),
            }
            if exc.response:
                try:
                    error_details['solcast_response'] = exc.response.text[:500]
                    error_details['status_code'] = exc.response.status_code
                except:
                    pass
            return Response(
                error_details,
                status=exc.response.status_code if exc.response else status.HTTP_502_BAD_GATEWAY
            )
        except requests.RequestException as exc:
            print(f"SOLCAST REQUEST ERROR: {type(exc).__name__}: {exc}")
            return Response(
                {
                    'error': 'Network error while contacting Solcast API',
                    'details': f'{type(exc).__name__}: {str(exc)}',
                    'suggestion': 'Please check your internet connection and try again'
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except ValueError as exc:
            print(f"SOLCAST DATA ERROR: {exc}")
            return Response(
                {
                    'error': 'Invalid data received from Solcast API',
                    'details': str(exc),
                    'suggestion': 'The Solcast API response format may have changed'
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except RuntimeError as exc:
            print(f"SOLCAST CONFIGURATION ERROR: {exc}")
            return Response(
                {
                    'error': 'Solcast API configuration error',
                    'details': str(exc),
                    'suggestion': 'Please contact the administrator'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as exc:
            print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
            return Response(
                {
                    'error': 'An unexpected error occurred',
                    'details': f'{type(exc).__name__}: {str(exc)}',
                    'suggestion': 'Please try again later or contact support if the issue persists'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeocodeSearchProxy(APIView):
    """
    Lightweight proxy for Nominatim search queries.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()
            if not query or len(query) < 3:
                return Response(
                    {
                        'error': 'Invalid search query',
                        'details': 'Query parameter "q" must be at least 3 characters long',
                        'received': query
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            results = _search_locations(query)
            return Response({'results': results})
        except Exception as exc:
            return Response(
                {
                    'error': 'Failed to search locations',
                    'details': str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardStatsView(APIView):
    """
    Dashboard statistics endpoint
    """
    permission_classes = [AllowAny]
    
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
            import traceback
            traceback.print_exc()
            return Response(
                {
                    'error': 'Failed to fetch dashboard statistics',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WeatherUploadViewSet(viewsets.ViewSet):
    """
    Handle weather data file uploads (CSV, XLSX, PDF)
    """
    def create(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {
                    'error': 'No file provided',
                    'details': 'Please upload a file (CSV, XLSX, or PDF)',
                    'allowed_formats': ['CSV', 'XLSX', 'PDF'],
                    'max_size_mb': 20
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            handler = FileHandler()
            data = handler.process_weather_csv(file)
            
            if not data or len(data) == 0:
                return Response(
                    {
                        'error': 'No data extracted from file',
                        'details': 'The file appears to be empty or could not be parsed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('weather_data').insert(data).execute()
            
            return Response({
                'message': f'Successfully uploaded {len(data)} weather records',
                'count': len(data),
                'file_type': file.name.split('.')[-1].upper()
            })
        except ValueError as e:
            return Response(
                {
                    'error': 'File validation error',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Error processing file',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductionUploadViewSet(viewsets.ViewSet):
    """
    Handle production data file uploads (CSV, XLSX, PDF)
    """
    def create(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {
                    'error': 'No file provided',
                    'details': 'Please upload a file (CSV, XLSX, or PDF)',
                    'allowed_formats': ['CSV', 'XLSX', 'PDF'],
                    'max_size_mb': 20
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            handler = FileHandler()
            data = handler.process_production_csv(file)
            
            if not data or len(data) == 0:
                return Response(
                    {
                        'error': 'No data extracted from file',
                        'details': 'The file appears to be empty or could not be parsed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save to Supabase
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('production_data').insert(data).execute()
            
            return Response({
                'message': f'Successfully uploaded {len(data)} production records',
                'count': len(data),
                'file_type': file.name.split('.')[-1].upper()
            })
        except ValueError as e:
            return Response(
                {
                    'error': 'File validation error',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Error processing file',
                    'details': str(e)
                },
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
    Serve pre-computed predictions first, fall back to on-demand inference.
    """

    def _get_supabase_client(self) -> Client:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def _fetch_trained_predictions(self, prediction_type: str, limit: int):
        """
        Pull the latest stored predictions produced by the active model.
        """
        supabase = self._get_supabase_client()
        result = (
            supabase.table('predictions')
            .select('*')
            .eq('prediction_type', prediction_type)
            .order('timestamp', desc=True)
            .limit(limit)
            .execute()
        )

        data = result.data or []
        # Return chronological order for charts
        return list(reversed(data))

    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily predictions sourced from trained data."""
        try:
            days = int(request.query_params.get('days', 7))
            stored_predictions = self._fetch_trained_predictions('daily', days)

            if stored_predictions:
                return Response(stored_predictions)

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
        """Get hourly predictions sourced from trained data."""
        try:
            hours = int(request.query_params.get('hours', 24))
            stored_predictions = self._fetch_trained_predictions('hourly', hours)

            if stored_predictions:
                return Response(stored_predictions)

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

