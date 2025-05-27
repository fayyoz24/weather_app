# weather_app/services.py
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import City, User, SearchHistory

class WeatherService:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    
    @classmethod
    def search_cities(cls, query):
        """Search for cities using Open-Meteo Geocoding API"""
        try:
            params = {
                'name': query,
                'count': 10,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(cls.GEOCODING_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            cities = []
            
            if 'results' in data:
                for result in data['results']:
                    city_data = {
                        'name': result.get('name', ''),
                        'country': result.get('country', ''),
                        'admin1': result.get('admin1', ''),
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude'),
                    }
                    cities.append(city_data)
            
            return cities
            
        except requests.RequestException as e:
            raise Exception(f"Failed to search cities: {str(e)}")
    
    @classmethod
    def get_weather_data(cls, latitude, longitude):
        """Get weather data from Open-Meteo API"""
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'apparent_temperature',
                    'is_day',
                    'precipitation',
                    'weather_code',
                    'cloud_cover',
                    'pressure_msl',
                    'wind_speed_10m',
                    'wind_direction_10m'
                ],
                'hourly': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'precipitation_probability',
                    'precipitation',
                    'weather_code',
                    'wind_speed_10m'
                ],
                'daily': [
                    'weather_code',
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'apparent_temperature_max',
                    'apparent_temperature_min',
                    'precipitation_sum',
                    'wind_speed_10m_max',
                    'wind_direction_10m_dominant'
                ],
                'timezone': 'auto',
                'forecast_days': 7
            }
            
            response = requests.get(cls.WEATHER_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return cls._format_weather_data(data)
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")
    
    @classmethod
    def _format_weather_data(cls, raw_data):
        """Format raw weather data into a more readable format"""
        current = raw_data.get('current', {})
        hourly = raw_data.get('hourly', {})
        daily = raw_data.get('daily', {})
        
        # Format current weather
        current_weather = {
            'temperature': current.get('temperature_2m'),
            'feels_like': current.get('apparent_temperature'),
            'humidity': current.get('relative_humidity_2m'),
            'precipitation': current.get('precipitation'),
            'weather_code': current.get('weather_code'),
            'weather_description': cls._get_weather_description(current.get('weather_code')),
            'cloud_cover': current.get('cloud_cover'),
            'pressure': current.get('pressure_msl'),
            'wind_speed': current.get('wind_speed_10m'),
            'wind_direction': current.get('wind_direction_10m'),
            'is_day': current.get('is_day'),
            'time': current.get('time')
        }
        
        # Format hourly forecast (next 24 hours)
        hourly_forecast = []
        if hourly.get('time'):
            for i in range(min(24, len(hourly['time']))):
                hourly_forecast.append({
                    'time': hourly['time'][i],
                    'temperature': hourly['temperature_2m'][i] if i < len(hourly.get('temperature_2m', [])) else None,
                    'humidity': hourly['relative_humidity_2m'][i] if i < len(hourly.get('relative_humidity_2m', [])) else None,
                    'precipitation_probability': hourly['precipitation_probability'][i] if i < len(hourly.get('precipitation_probability', [])) else None,
                    'precipitation': hourly['precipitation'][i] if i < len(hourly.get('precipitation', [])) else None,
                    'weather_code': hourly['weather_code'][i] if i < len(hourly.get('weather_code', [])) else None,
                    'weather_description': cls._get_weather_description(
                        hourly['weather_code'][i] if i < len(hourly.get('weather_code', [])) else None
                    ),
                    'wind_speed': hourly['wind_speed_10m'][i] if i < len(hourly.get('wind_speed_10m', [])) else None,
                })
        
        # Format daily forecast
        daily_forecast = []
        if daily.get('time'):
            for i in range(len(daily['time'])):
                daily_forecast.append({
                    'date': daily['time'][i],
                    'temperature_max': daily['temperature_2m_max'][i] if i < len(daily.get('temperature_2m_max', [])) else None,
                    'temperature_min': daily['temperature_2m_min'][i] if i < len(daily.get('temperature_2m_min', [])) else None,
                    'feels_like_max': daily['apparent_temperature_max'][i] if i < len(daily.get('apparent_temperature_max', [])) else None,
                    'feels_like_min': daily['apparent_temperature_min'][i] if i < len(daily.get('apparent_temperature_min', [])) else None,
                    'precipitation': daily['precipitation_sum'][i] if i < len(daily.get('precipitation_sum', [])) else None,
                    'wind_speed_max': daily['wind_speed_10m_max'][i] if i < len(daily.get('wind_speed_10m_max', [])) else None,
                    'wind_direction': daily['wind_direction_10m_dominant'][i] if i < len(daily.get('wind_direction_10m_dominant', [])) else None,
                    'weather_code': daily['weather_code'][i] if i < len(daily.get('weather_code', [])) else None,
                    'weather_description': cls._get_weather_description(
                        daily['weather_code'][i] if i < len(daily.get('weather_code', [])) else None
                    ),
                })
        
        return {
            'current_weather': current_weather,
            'hourly_forecast': hourly_forecast,
            'daily_forecast': daily_forecast,
            'timezone': raw_data.get('timezone'),
            'elevation': raw_data.get('elevation')
        }
    
    @classmethod
    def _get_weather_description(cls, code):
        """Convert weather code to human-readable description"""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")

class UserService:
    @classmethod
    def get_or_create_user(cls, session_key):
        """Get or create user based on session key"""
        user, created = User.objects.get_or_create(
            session_key=session_key,
            defaults={'session_key': session_key}
        )
        return user
    
    @classmethod
    def save_search(cls, user, city_data):
        """Save or update search history"""
        # Get or create city
        city, created = City.objects.get_or_create(
            name=city_data['name'],
            country=city_data['country'],
            latitude=city_data['latitude'],
            longitude=city_data['longitude'],
            defaults={
                'admin1': city_data.get('admin1', ''),
            }
        )
        
        # Update or create search history
        search_history, created = SearchHistory.objects.get_or_create(
            user=user,
            city=city,
            defaults={'search_count': 1}
        )
        
        if not created:
            search_history.search_count += 1
            search_history.last_searched = datetime.now()
            search_history.save()
        
        return search_history