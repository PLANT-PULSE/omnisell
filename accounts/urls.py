"""
URL patterns for accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView
)

from .views import (
    UserRegistrationViewSet, CustomTokenObtainPairView,
    UserViewSet, ProfileViewSet, ConnectedPlatformViewSet,
    UserActivityViewSet
)

router = DefaultRouter()
router.register(r'register', UserRegistrationViewSet, basename='register')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'platforms', ConnectedPlatformViewSet, basename='platforms')
router.register(r'activities', UserActivityViewSet, basename='activities')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    # JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Router URLs
    path('', include(router.urls)),
]

