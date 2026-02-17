"""
URL patterns for notifications app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NotificationViewSet, NotificationPreferenceViewSet,
    NotificationTemplateViewSet, PushDeviceViewSet
)

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notifications')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preferences')
router.register(r'templates', NotificationTemplateViewSet, basename='notification-templates')
router.register(r'devices', PushDeviceViewSet, basename='push-devices')

urlpatterns = [
    path('', include(router.urls)),
]

