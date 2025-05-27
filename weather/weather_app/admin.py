# weather_app/admin.py
from django.contrib import admin
from .models import User, City, SearchHistory

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at', 'total_searches']
    list_filter = ['created_at']
    search_fields = ['session_key']
    readonly_fields = ['session_key', 'created_at']
    
    def total_searches(self, obj):
        return obj.searches.count()
    total_searches.short_description = 'Total Searches'

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'admin1', 'latitude', 'longitude', 'total_searches']
    list_filter = ['country']
    search_fields = ['name', 'country', 'admin1']
    readonly_fields = ['name', 'country', 'admin1', 'latitude', 'longitude']
    
    def total_searches(self, obj):
        return obj.searches.count()
    total_searches.short_description = 'Times Searched'

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_session', 'city', 'search_count', 'last_searched', 'created_at']
    list_filter = ['last_searched', 'created_at', 'city__country']
    search_fields = ['city__name', 'city__country', 'user__session_key']
    readonly_fields = ['user', 'city', 'created_at']
    ordering = ['-last_searched']
    
    def user_session(self, obj):
        return f"{obj.user.session_key[:8]}..."
    user_session.short_description = 'User Session'