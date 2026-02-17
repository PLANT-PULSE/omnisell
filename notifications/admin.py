"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from .models import Notification, NotificationPreference, NotificationTemplate, PushDevice


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""
    list_display = ['user', 'title', 'notification_type', 'is_read', 'priority', 'created_at']
    list_filter = ['notification_type', 'is_read', 'priority', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    raw_id_fields = ['user']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Notification preference admin."""
    list_display = ['user', 'in_app_enabled', 'email_enabled', 'push_enabled', 'created_at']
    list_filter = ['in_app_enabled', 'email_enabled', 'push_enabled']
    raw_id_fields = ['user']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Notification template admin."""
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active']


@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    """Push device admin."""
    list_display = ['user', 'device_type', 'device_name', 'is_active', 'created_at']
    list_filter = ['device_type', 'is_active']
    raw_id_fields = ['user']

