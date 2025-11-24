"""
API Serializers
"""
from rest_framework import serializers


class WeatherDataSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    temperature = serializers.FloatField(required=False)
    humidity = serializers.FloatField(required=False)
    wind_speed = serializers.FloatField(required=False)
    cloud_cover = serializers.FloatField(required=False)
    solar_irradiance = serializers.FloatField(required=False)
    precipitation = serializers.FloatField(required=False)
    is_forecast = serializers.BooleanField(default=False)
    location = serializers.CharField(required=False, max_length=100)


class ProductionDataSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    energy_output_kwh = serializers.FloatField()
    panel_id = serializers.CharField(required=False, max_length=50)
    system_capacity_kw = serializers.FloatField(required=False)
    efficiency = serializers.FloatField(required=False)


class PredictionSerializer(serializers.Serializer):
    prediction_type = serializers.ChoiceField(choices=['hourly', 'daily'])
    timestamp = serializers.DateTimeField()
    predicted_output_kwh = serializers.FloatField()
    confidence_score = serializers.FloatField(required=False)
    model_version = serializers.CharField(required=False)
    weather_data_id = serializers.UUIDField(required=False)
    actual_output_kwh = serializers.FloatField(required=False)


class ImageUploadSerializer(serializers.Serializer):
    filename = serializers.CharField()
    file_path = serializers.CharField()
    panel_id = serializers.CharField(required=False)
    condition_score = serializers.FloatField(required=False)
    condition_status = serializers.ChoiceField(
        choices=['excellent', 'good', 'fair', 'poor'],
        required=False
    )


class TrainingJobSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'running', 'completed', 'failed'])
    model_type = serializers.CharField()
    training_data_count = serializers.IntegerField(required=False)
    started_at = serializers.DateTimeField(required=False)
    completed_at = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)


