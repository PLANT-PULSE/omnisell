"""
Admin configuration for chat app.
"""
from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin."""
    list_display = ['id', 'customer_name', 'customer_email', 'product', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'product__name']
    raw_id_fields = ['product', 'seller']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin."""
    list_display = ['id', 'conversation', 'sender', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'created_at']
    search_fields = ['content']
    raw_id_fields = ['conversation', 'sender', 'recipient']
    date_hierarchy = 'created_at'
