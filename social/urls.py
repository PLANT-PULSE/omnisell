"""
URL patterns for social media app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SocialAccountViewSet, SocialPostViewSet, SocialScheduleViewSet,
    OAuthCallbackViewSet
)

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='social-accounts')
router.register(r'posts', SocialPostViewSet, basename='social-posts')
router.register(r'schedules', SocialScheduleViewSet, basename='social-schedules')
router.register(r'oauth', OAuthCallbackViewSet, basename='oauth')

urlpatterns = [
    path('', include(router.urls)),
]

