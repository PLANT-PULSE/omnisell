"""
URL patterns for analytics app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsViewSet, PlatformAnalyticsViewSet,
    ConversionFunnelViewSet
)

router = DefaultRouter()
router.register(r'', AnalyticsViewSet, basename='analytics')
router.register(r'platforms', PlatformAnalyticsViewSet, basename='platform-analytics')
router.register(r'funnel', ConversionFunnelViewSet, basename='funnel')

urlpatterns = [
    path('', include(router.urls)),
]

