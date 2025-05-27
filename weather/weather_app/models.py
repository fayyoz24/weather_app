# weather_app/models.py
from django.db import models
from django.utils import timezone
import uuid

class User(models.Model):
    """Custom user model to track anonymous users via sessions"""
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"User {self.session_key[:8]}..."

class City(models.Model):
    """City information from geocoding API"""
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    admin1 = models.CharField(max_length=200, blank=True, null=True)  # State/Province
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        unique_together = ['name', 'country', 'latitude', 'longitude']
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return f"{self.name}, {self.country}"

class SearchHistory(models.Model):
    """Track user search history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='searches')
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'city']
        ordering = ['-last_searched']
    
    def __str__(self):
        return f"{self.user} searched {self.city} ({self.search_count} times)"
    