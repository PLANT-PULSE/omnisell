"""
Serializers for chat app.
"""
from rest_framework import serializers
from .models import (
    Conversation, Message, AIConversationContext,
    ChatSettings, AISuggestion
)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages."""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'sender_email',
            'recipient', 'content', 'message_type',
            'image', 'attachment', 'product',
            'is_ai_generated', 'ai_suggestion_used',
            'is_read', 'is_delivered', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'sender_email', 'is_read',
            'is_delivered', 'created_at', 'updated_at'
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    class Meta:
        model = Message
        fields = [
            'conversation', 'content', 'message_type',
            'image', 'attachment', 'product',
            'is_ai_generated'
        ]
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations."""
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'seller', 'customer_email', 'customer_name', 'product',
            'product_name', 'product_price', 'status', 'source',
            'metadata', 'last_message', 'unread_count',
            'created_at', 'updated_at', 'last_message_at'
        ]
        read_only_fields = [
            'id', 'seller', 'created_at', 'updated_at', 'last_message_at'
        ]
    
    def get_last_message(self, obj):
        last = obj.messages.first()
        if last:
            return MessageSerializer(last).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(recipient=user, is_read=False).count()


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for conversation lists."""
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'customer_email', 'customer_name', 'product',
            'status', 'source', 'last_message_preview', 'unread_count',
            'created_at', 'last_message_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']
    
    def get_last_message_preview(self, obj):
        last = obj.messages.first()
        if last:
            return last.content[:100]
        return ''
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(recipient=user, is_read=False).count()


class AIConversationContextSerializer(serializers.ModelSerializer):
    """Serializer for AI conversation context."""
    
    class Meta:
        model = AIConversationContext
        fields = [
            'id', 'conversation', 'message', 'context_type',
            'extracted_info', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AISuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AI suggestions."""
    
    class Meta:
        model = AISuggestion
        fields = [
            'id', 'conversation', 'suggestion_type', 'content',
            'was_used', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ChatSettingsSerializer(serializers.ModelSerializer):
    """Serializer for chat settings."""
    
    class Meta:
        model = ChatSettings
        fields = [
            'id', 'ai_auto_reply_enabled', 'ai_reply_sensitivity',
            'email_notifications', 'push_notifications',
            'business_hours_enabled', 'business_hours_start',
            'business_hours_end', 'timezone',
            'auto_response_enabled', 'auto_response_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GenerateAISuggestionsSerializer(serializers.Serializer):
    """Serializer for generating AI suggestions."""
    conversation_id = serializers.IntegerField()
    suggestion_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read."""
    conversation_id = serializers.IntegerField()

