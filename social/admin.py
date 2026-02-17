"""
Admin configuration for social app.
"""
from django.contrib import admin
from .models import SocialAccount, SocialPost, SocialSchedule


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    """Social account admin."""
    list_display = ['user', 'platform', 'platform_username', 'is_active', 'followers_count', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__email', 'platform_username']
    raw_id_fields = ['user']


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    """Social post admin."""
    list_display = ['user', 'platform', 'product', 'status', 'is_scheduled', 'scheduled_at', 'created_at']
    list_filter = ['platform', 'status', 'is_scheduled', 'created_at']
    search_fields = ['content', 'product__name']
    raw_id_fields = ['user', 'product', 'social_account']
    date_hierarchy = 'created_at'


@admin.register(SocialSchedule)
class SocialScheduleAdmin(admin.ModelAdmin):
    """Social schedule admin."""
    list_display = ['user', 'platform', 'time', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['user__email']
    raw_id_fields = ['user']
