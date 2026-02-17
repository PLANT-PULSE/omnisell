"""
Admin configuration for analytics app.
"""
from django.contrib import admin
from .models import (
    DailyAnalytics, PlatformAnalytics, ProductAnalytics
)


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    """Daily analytics admin."""
    list_display = ['user', 'date', 'revenue', 'orders_count', 'page_views', 'clicks']
    list_filter = ['date', 'user']
    search_fields = ['user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'date'


@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    """Platform analytics admin."""
    list_display = ['user', 'platform', 'date', 'impressions', 'clicks', 'leads', 'conversions']
    list_filter = ['platform', 'date']
    search_fields = ['user__email']
    raw_id_fields = ['user']
    date_hierarchy = 'date'


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    """Product analytics admin."""
    list_display = ['product', 'date', 'views', 'clicks', 'leads', 'conversions', 'revenue']
    list_filter = ['date', 'product']
    date_hierarchy = 'date'
    raw_id_fields = ['product']
