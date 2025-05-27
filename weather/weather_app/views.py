# weather_app/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import City, SearchHistory, User
from .serializers import (
    CitySerializer, SearchHistorySerializer, WeatherDataSerializer,
    CitySearchSerializer, WeatherRequestSerializer
)
from .services import WeatherService, UserService


class CitySearchView(APIView):
    """API endpoint for city search with autocomplete"""
    
    def post(self, request):
        serializer = CitySearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        
        try:
            cities = WeatherService.search_cities(query)
            return Response({
                'cities': cities,
                'count': len(cities)
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WeatherView(APIView):
    """API endpoint for getting weather data"""
    
    def post(self, request):
        serializer = WeatherRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        user = UserService.get_or_create_user(session_key)
        
        try:
            if serializer.validated_data.get('city_id'):
                # Get weather by city ID
                try:
                    city = City.objects.get(id=serializer.validated_data['city_id'])
                    latitude = city.latitude
                    longitude = city.longitude
                    city_data = {
                        'name': city.name,
                        'country': city.country,
                        'admin1': city.admin1,
                        'latitude': city.latitude,
                        'longitude': city.longitude
                    }
                except City.DoesNotExist:
                    return Response(
                        {'error': 'City not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Get weather by coordinates
                latitude = serializer.validated_data['latitude']
                longitude = serializer.validated_data['longitude']
                city_data = None
            
            # Get weather data
            weather_data = WeatherService.get_weather_data(latitude, longitude)
            
            # Save search if city data is available
            if city_data:
                UserService.save_search(user, city_data)
                city_serializer = CitySerializer(city)
                weather_data['city'] = city_serializer.data
            
            return Response(weather_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SearchHistoryView(APIView):
    """API endpoint for user's search history"""
    
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return Response({'history': []})
        
        try:
            user = User.objects.get(session_key=session_key)
            history = SearchHistory.objects.filter(user=user).order_by('-last_searched')[:10]
            serializer = SearchHistorySerializer(history, many=True)
            return Response({'history': serializer.data})
        except User.DoesNotExist:
            return Response({'history': []})

class PopularCitiesView(APIView):
    """API endpoint for most searched cities"""
    
    def get(self, request):
        popular_cities = (
            SearchHistory.objects
            .values('city__name', 'city__country', 'city__id')
            .annotate(
                total_searches=Sum('search_count'),
                unique_users=Count('user', distinct=True)
            )
            .order_by('-total_searches')[:10]
        )
        
        return Response({
            'popular_cities': list(popular_cities)
        })

class StatsView(APIView):
    """API endpoint for search statistics"""
    
    def get(self, request):
        city_stats = (
            SearchHistory.objects
            .values('city__name', 'city__country')
            .annotate(
                search_count=Sum('search_count'),
                unique_users=Count('user', distinct=True)
            )
            .order_by('-search_count')
        )
        
        total_searches = SearchHistory.objects.aggregate(
            total=Sum('search_count')
        )['total'] or 0
        
        total_users = User.objects.count()
        total_cities = City.objects.count()
        
        return Response({
            'city_stats': list(city_stats),
            'total_searches': total_searches,
            'total_users': total_users,
            'total_cities': total_cities
        })

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({'status': 'healthy', 'message': 'Weather API is running'})

# Additional utility views
class RecentSearchesView(APIView):
    """Get user's recent searches for suggestions"""
    
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return Response({'recent_searches': []})
        
        try:
            user = User.objects.get(session_key=session_key)
            recent_searches = (
                SearchHistory.objects
                .filter(user=user)
                .select_related('city')
                .order_by('-last_searched')[:5]
            )
            
            suggestions = []
            for search in recent_searches:
                suggestions.append({
                    'city_id': search.city.id,
                    'display_name': f"{search.city.name}, {search.city.country}",
                    'last_searched': search.last_searched
                })
            
            return Response({'recent_searches': suggestions})
            
        except User.DoesNotExist:
            return Response({'recent_searches': []})