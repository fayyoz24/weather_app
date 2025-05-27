# weather_app/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
import json
from .models import User, City, SearchHistory
from .services import WeatherService, UserService

class WeatherServiceTestCase(TestCase):
    """Test cases for WeatherService"""
    
    def setUp(self):
        self.sample_geocoding_response = {
            "results": [
                {
                    "name": "London",
                    "country": "United Kingdom",
                    "admin1": "England",
                    "latitude": 51.5074,
                    "longitude": -0.1278
                }
            ]
        }
        
        self.sample_weather_response = {
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "Europe/London",
            "current": {
                "time": "2024-01-15T12:00",
                "temperature_2m": 15.5,
                "apparent_temperature": 14.2,
                "relative_humidity_2m": 75,
                "pressure_msl": 1013.2,
                "wind_speed_10m": 10.5,
                "wind_direction_10m": 180,
                "weather_code": 1
            },
            "hourly": {
                "time": ["2024-01-15T13:00", "2024-01-15T14:00"],
                "temperature_2m": [16.0, 17.0],
                "weather_code": [1, 2],
                "precipitation_probability": [10, 20]
            },
            "daily": {
                "time": ["2024-01-15"],
                "temperature_2m_max": [18.0],
                "temperature_2m_min": [12.0],
                "weather_code": [1]
            }
        }

    @patch('weather_app.services.requests.get')
    def test_search_cities_success(self, mock_get):
        """Test successful city search"""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_geocoding_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        cities = WeatherService.search_cities("London")
        
        self.assertEqual(len(cities), 1)
        self.assertEqual(cities[0]['name'], 'London')
        self.assertEqual(cities[0]['country'], 'United Kingdom')
        
        # Check that city was saved to database
        self.assertTrue(City.objects.filter(name='London', country='United Kingdom').exists())

    @patch('weather_app.services.requests.get')
    def test_search_cities_no_results(self, mock_get):
        """Test city search with no results"""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        cities = WeatherService.search_cities("NonexistentCity")
        
        self.assertEqual(len(cities), 0)

    @patch('weather_app.services.requests.get')
    def test_get_weather_data_success(self, mock_get):
        """Test successful weather data retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = self.sample_weather_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        weather_data = WeatherService.get_weather_data(51.5074, -0.1278)
        
        self.assertIn('current_weather', weather_data)
        self.assertIn('hourly_forecast', weather_data)
        self.assertIn('daily_forecast', weather_data)
        self.assertEqual(weather_data['current_weather']['temperature'], 15.5)

    def test_weather_description(self):
        """Test weather code to description conversion"""
        self.assertEqual(WeatherService._get_weather_description(0), "Clear sky")
        self.assertEqual(WeatherService._get_weather_description(61), "Slight rain")
        self.assertEqual(WeatherService._get_weather_description(999), "Unknown")


class UserServiceTestCase(TestCase):
    """Test cases for UserService"""
    
    def setUp(self):
        self.session_key = "test_session_123"
        self.city_data = {
            'name': 'London',
            'country': 'United Kingdom',
            'admin1': 'England',
            'latitude': 51.5074,
            'longitude': -0.1278
        }

    def test_get_or_create_user_new(self):
        """Test creating a new user"""
        user = UserService.get_or_create_user(self.session_key)
        
        self.assertEqual(user.session_key, self.session_key)
        self.assertTrue(User.objects.filter(session_key=self.session_key).exists())

    def test_get_or_create_user_existing(self):
        """Test getting an existing user"""
        # Create user first
        User.objects.create(session_key=self.session_key)
        
        user = UserService.get_or_create_user(self.session_key)
        
        self.assertEqual(user.session_key, self.session_key)
        self.assertEqual(User.objects.filter(session_key=self.session_key).count(), 1)

    def test_save_search_new(self):
        """Test saving a new search"""
        user = User.objects.create(session_key=self.session_key)
        
        search_history = UserService.save_search(user, self.city_data)
        
        self.assertEqual(search_history.search_count, 1)
        self.assertEqual(search_history.city.name, 'London')
        self.assertTrue(City.objects.filter(name='London').exists())

    def test_save_search_existing(self):
        """Test updating an existing search"""
        user = User.objects.create(session_key=self.session_key)
        city = City.objects.create(**self.city_data)
        SearchHistory.objects.create(user=user, city=city, search_count=1)
        
        search_history = UserService.save_search(user, self.city_data)
        
        self.assertEqual(search_history.search_count, 2)


class WeatherViewsTestCase(TestCase):
    """Test cases for weather views"""
    
    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(
            name='London',
            country='United Kingdom',
            admin1='England',
            latitude=51.5074,
            longitude=-0.1278
        )

    def test_index_view(self):
        """Test main page renders correctly"""
        response = self.client.get(reverse('weather_app:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weather App')

    @patch('weather_app.services.WeatherService.search_cities')
    def test_city_search_view_success(self, mock_search):
        """Test successful city search API"""
        mock_search.return_value = [
            {
                'id': self.city.id,
                'name': 'London',
                'country': 'United Kingdom',
                'admin1': 'England',
                'latitude': 51.5074,
                'longitude': -0.1278,
                'display_name': 'London, England, United Kingdom'
            }
        ]
        
        response = self.client.post(
            reverse('weather_app:search_cities'),
            data=json.dumps({'query': 'London'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['cities']), 1)
        self.assertEqual(data['cities'][0]['name'], 'London')

    def test_city_search_view_invalid_data(self):
        """Test city search API with invalid data"""
        response = self.client.post(
            reverse('weather_app:search_cities'),
            data=json.dumps({'query': 'L'}),  # Too short
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('weather_app.services.WeatherService.get_weather_data')
    def test_weather_view_success(self, mock_weather):
        """Test successful weather data API"""
        mock_weather.return_value = {
            'current_weather': {
                'temperature': 15.5,
                'weather_description': 'Clear sky'
            },
            'hourly_forecast': [],
            'daily_forecast': []
        }
        
        response = self.client.post(
            reverse('weather_app:weather'),
            data=json.dumps({'city_id': self.city.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('current_weather', data)

    def test_weather_view_city_not_found(self):
        """Test weather API with non-existent city"""
        response = self.client.post(
            reverse('weather_app:weather'),
            data=json.dumps({'city_id': 99999}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)

    def test_search_history_view_no_user(self):
        """Test search history API with no user session"""
        response = self.client.get(reverse('weather_app:search_history'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['history']), 0)

    def test_search_history_view_with_user(self):
        """Test search history API with user session"""
        # Create session
        session = self.client.session
        session.create()
        session.save()
        
        user = User.objects.create(session_key=session.session_key)
        SearchHistory.objects.create(user=user, city=self.city, search_count=1)
        
        response = self.client.get(reverse('weather_app:search_history'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['history']), 1)

    def test_popular_cities_view(self):
        """Test popular cities API"""
        user = User.objects.create(session_key='test_session')
        SearchHistory.objects.create(user=user, city=self.city, search_count=5)
        
        response = self.client.get(reverse('weather_app:popular_cities'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['popular_cities']), 1)

    def test_stats_view(self):
        """Test statistics API"""
        user = User.objects.create(session_key='test_session')
        SearchHistory.objects.create(user=user, city=self.city, search_count=3)
        
        response = self.client.get(reverse('weather_app:stats'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_searches', data)
        self.assertIn('total_users', data)
        self.assertIn('total_cities', data)
        self.assertEqual(data['total_searches'], 3)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get(reverse('weather_app:health_check'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')


class ModelsTestCase(TestCase):
    """Test cases for models"""
    
    def test_user_model(self):
        """Test User model"""
        user = User.objects.create(session_key='test_session_123')
        
        self.assertEqual(str(user), 'User test_ses...')
        self.assertTrue(user.created_at)

    def test_city_model(self):
        """Test City model"""
        city = City.objects.create(
            name='London',
            country='United Kingdom',
            admin1='England',
            latitude=51.5074,
            longitude=-0.1278
        )
        
        self.assertEqual(str(city), 'London, United Kingdom')

    def test_search_history_model(self):
        """Test SearchHistory model"""
        user = User.objects.create(session_key='test_session')
        city = City.objects.create(
            name='London',
            country='United Kingdom',
            latitude=51.5074,
            longitude=-0.1278
        )
        search = SearchHistory.objects.create(user=user, city=city)
        
        self.assertEqual(search.search_count, 1)
        self.assertTrue(search.created_at)
        self.assertTrue(search.last_searched)
        self.assertIn('London', str(search))

    def test_city_unique_constraint(self):
        """Test city unique constraint"""
        City.objects.create(
            name='London',
            country='United Kingdom',
            latitude=51.5074,
            longitude=-0.1278
        )
        
        # This should not create a duplicate
        city2, created = City.objects.get_or_create(
            name='London',
            country='United Kingdom',
            latitude=51.5074,
            longitude=-0.1278
        )
        
        self.assertFalse(created)
        self.assertEqual(City.objects.filter(name='London').count(), 1)