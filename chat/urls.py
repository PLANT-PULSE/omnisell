"""
URL patterns for chat app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ConversationViewSet, MessageViewSet, ChatSettingsViewSet,
    AISuggestionViewSet
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'settings', ChatSettingsViewSet, basename='chat-settings')
router.register(r'suggestions', AISuggestionViewSet, basename='ai-suggestions')

urlpatterns = [
    path('', include(router.urls)),
]

