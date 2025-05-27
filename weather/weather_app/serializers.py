# weather_app/serializers.py
from rest_framework import serializers
from .models import City, SearchHistory, User

class CitySerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'admin1', 'latitude', 'longitude', 'display_name']
    
    def get_display_name(self, obj):
        if obj.admin1:
            return f"{obj.name}, {obj.admin1}, {obj.country}"
        return f"{obj.name}, {obj.country}"

class SearchHistorySerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = ['id', 'city', 'search_count', 'last_searched', 'created_at']

class WeatherDataSerializer(serializers.Serializer):
    """Serializer for weather data from Open-Meteo API"""
    city = CitySerializer(read_only=True)
    current_weather = serializers.DictField()
    hourly_forecast = serializers.ListField()
    daily_forecast = serializers.ListField()

class CitySearchSerializer(serializers.Serializer):
    """Serializer for city search input"""
    query = serializers.CharField(max_length=200, required=True)
    
    def validate_query(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("City name must be at least 2 characters long")
        return value.strip()

class WeatherRequestSerializer(serializers.Serializer):
    """Serializer for weather request input"""
    city_id = serializers.IntegerField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    
    def validate(self, data):
        if not data.get('city_id') and not (data.get('latitude') and data.get('longitude')):
            raise serializers.ValidationError(
                "Either city_id or both latitude and longitude must be provided"
            )
        return data