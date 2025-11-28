"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'upload/weather', views.WeatherUploadViewSet, basename='weather-upload')
router.register(r'upload/production', views.ProductionUploadViewSet, basename='production-upload')
router.register(r'upload/images', views.ImageUploadViewSet, basename='image-upload')
router.register(r'predictions', views.PredictionViewSet, basename='predictions')
router.register(r'training', views.TrainingViewSet, basename='training')
router.register(r'health', views.HealthViewSet, basename='health')

urlpatterns = [
    path('test', lambda request: JsonResponse({'status': 'Django ALIVE', 'time': request.GET})),
    path('', include(router.urls)),
    path('dashboard/stats', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('forecast/solar', views.SolarForecastProxy.as_view(), name='solar-forecast'),
    path('geocode/search', views.GeocodeSearchProxy.as_view(), name='geocode-search'),
]



