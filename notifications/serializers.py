"""
Serializers for notifications app.
"""
from rest_framework import serializers
from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    PushDevice
)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'icon', 'color', 'related_object_type', 'related_object_id',
            'action_url', 'is_read', 'read_at', 'priority',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'title', 'message', 'notification_type',
            'icon', 'color', 'related_object_type', 'related_object_id',
            'action_url', 'read_at', 'priority', 'created_at', 'updated_at'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'title', 'message', 'notification_type',
            'icon', 'color', 'related_object_type', 'related_object_id',
            'action_url', 'priority'
        ]
    
    def create(self, validated_data):
        return Notification.objects.create(**validated_data)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'in_app_enabled',
            'order_notifications', 'payment_notifications',
            'chat_notifications', 'product_notifications',
            'social_notifications', 'system_notifications',
            'marketing_notifications',
            'email_enabled', 'email_daily_digest', 'email_weekly_digest',
            'push_enabled',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type',
            'title_template', 'message_template',
            'icon', 'color', 'available_variables',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PushDeviceSerializer(serializers.ModelSerializer):
    """Serializer for push devices."""
    
    class Meta:
        model = PushDevice
        fields = [
            'id', 'device_token', 'device_type', 'device_name',
            'is_active', 'last_used_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_used_at', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)


class NotificationCountSerializer(serializers.Serializer):
    """Serializer for notification count response."""
    total = serializers.IntegerField()
    unread = serializers.IntegerField()

