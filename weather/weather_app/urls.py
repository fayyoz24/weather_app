# weather_app/urls.py
from django.urls import path
from . import views


urlpatterns = [
    
    # API endpoints
    path('api/search-cities/', views.CitySearchView.as_view(), name='search_cities'),
    path('api/weather/', views.WeatherView.as_view(), name='weather'),
    path('api/history/', views.SearchHistoryView.as_view(), name='search_history'),
    path('api/popular/', views.PopularCitiesView.as_view(), name='popular_cities'),
    path('api/stats/', views.StatsView.as_view(), name='stats'),
    path('api/recent/', views.RecentSearchesView.as_view(), name='recent_searches'),
    path('api/health/', views.health_check, name='health_check'),
]

