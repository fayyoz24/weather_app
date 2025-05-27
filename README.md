# Weather App 🌤️

A comprehensive weather application built with Django that provides accurate weather forecasts for cities worldwide using the Open-Meteo API.

## ✅ Implemented Features

### Core Requirements
- **✅ City Search**: Users can enter city names to get weather forecasts
- **✅ Weather Display**: Clean, readable weather forecast format
- **✅ Django Framework**: Built with Django REST Framework
- **✅ Open-Meteo API**: Integration with Open-Meteo weather API

### Bonus Features
- **✅ Comprehensive Tests**: Full test suite covering models, views, and services
- **✅ Docker Container**: Complete Docker setup with docker-compose
- **✅ City Autocomplete**: Real-time city search suggestions with autocomplete
- **✅ Recent Searches**: Users see their previously searched cities on return visits
- **✅ Search History**: Complete search history tracking for each user
- **✅ Statistics API**: API endpoints showing search statistics and popular cities

### Additional Features
- **✅ Responsive Design**: Modern, mobile-friendly UI
- **✅ Session-based Users**: Anonymous user tracking via sessions
- **✅ Detailed Weather Data**: Current weather, hourly, and 7-day forecasts
- **✅ Admin Interface**: Django admin for data management
- **✅ API Documentation**: RESTful API with proper error handling
- **✅ Production Ready**: Nginx, PostgreSQL, proper logging

## 🛠️ Technologies Used

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **Open-Meteo API** - Weather data source

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript (ES6+)** - Interactive features
- **Axios** - HTTP client for API calls

### DevOps & Deployment
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **Gunicorn** - WSGI HTTP Server

### Testing & Quality
- **Django TestCase** - Comprehensive test suite
- **Mock/Patch** - External API testing
- **Coverage** - Code coverage analysis

## 🏗️ Project Structure

```
weather_project/
├── weather_app/
│   ├── models.py          # Database models (User, City, SearchHistory)
│   ├── views.py           # API endpoints and main view
│   ├── services.py        # Business logic (WeatherService, UserService)
│   ├── serializers.py     # DRF serializers
│   ├── admin.py          # Django admin configuration
│   ├── tests.py          # Comprehensive test suite
│   └── urls.py           # URL routing
├── templates/
│   └── weather_app/
│       └── index.html    # Frontend application
├── weather_project/
│   ├── settings.py       # Django settings
│   └── urls.py          # Main URL configuration
├── docker-compose.yml    # Multi-container Docker setup
├── Dockerfile           # Django app container
├── nginx.conf          # Nginx configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 How to Run

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd weather_project
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Web App: http://localhost:80
   - Django Admin: http://localhost:80/admin/
   - API Health Check: http://localhost:80/api/health/

4. **Run migrations (first time only)**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb weather_db
   ```

3. **Configure environment variables**:
   ```bash
   export DB_NAME=weather_db
   export DB_USER=postgres
   export DB_PASSWORD=your_password
   export DB_HOST=localhost
   export DB_PORT=5432
   export SECRET_KEY=your-secret-key
   export DEBUG=True
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**: http://localhost:8000

## 🧪 Running Tests

### With Docker:
```bash
docker-compose exec web python manage.py test
```

### Locally:
```bash
python manage.py test
```

### Run specific test modules:
```bash
python manage.py test weather_app.tests.WeatherServiceTestCase
python manage.py test weather_app.tests.WeatherViewsTestCase
```

## 📡 API Endpoints

### Weather Data
- `POST /api/search-cities/` - Search for cities with autocomplete
- `POST /api/weather/` - Get weather data by city ID or coordinates
- `GET /api/search-history/` - Get user's search history
- `GET /api/recent-searches/` - Get user's recent searches for suggestions

### Statistics
- `GET /api/popular-cities/` - Get most searched cities
- `GET /api/stats/` - Get comprehensive search statistics
- `GET /api/health/` - Health check endpoint

### API Usage Examples

**Search Cities:**
```bash
curl -X POST http://localhost:8000/api/search-cities/ \
  -H "Content-Type: application/json" \
  -d '{"query": "London"}'
```

**Get Weather:**
```bash
curl -X POST http://localhost:8000/api/weather/ \
  -H "Content-Type: application/json" \
  -d '{"city_id": 1}'
```

## 🎨 Features Overview

### User Interface
- **Modern Design**: Clean, responsive interface with gradient backgrounds
- **Real-time Search**: Autocomplete suggestions as you type
- **Weather Cards**: Beautiful weather display with icons and details
- **Forecast Tabs**: Switch between hourly and daily forecasts
- **Recent Searches**: Quick access to previously searched cities

### Weather Data
- **Current Weather**: Temperature, feels like, humidity, pressure, wind
- **Hourly Forecast**: Next 24 hours with temperature and precipitation
- **Daily Forecast**: 7-day forecast with min/max temperatures
- **Weather Descriptions**: Human-readable weather conditions

### User Experience
- **Session Persistence**: Remembers users across visits without registration
- **Search History**: Tracks and displays user's search patterns
- **Error Handling**: Graceful error messages and loading states
- **Mobile Responsive**: Works perfectly on all device sizes

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `ALLOWED_HOSTS` - Comma-separated allowed hosts

### Docker Configuration
The application uses a multi-container setup:
- **web**: Django application with Gunicorn
- **db**: PostgreSQL database
- **nginx**: Reverse proxy and static file serving

## 📊 Database Schema

### Models
- **User**: Session-based user tracking
  - session_key (unique identifier)
  - created_at (timestamp)

- **City**: Geographic city information
  - name, country, admin1 (state/province)
  - latitude, longitude (coordinates)

- **SearchHistory**: User search tracking
  - user, city (foreign keys)
  - search_count (number of searches)
  - last_searched (timestamp)

## 🔍 Monitoring & Logging

- **Health Check**: `/api/health/` endpoint for monitoring
- **Comprehensive Logging**: File and console logging
- **