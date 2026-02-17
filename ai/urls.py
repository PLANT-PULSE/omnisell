"""
URL patterns for AI app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AIGeneratorViewSet, AIChatViewSet

router = DefaultRouter()
router.register(r'generate', AIGeneratorViewSet, basename='ai-generate')
router.register(r'chat', AIChatViewSet, basename='ai-chat')

urlpatterns = [
    path('', include(router.urls)),
]

