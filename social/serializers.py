"""
Serializers for social media app.
"""
from rest_framework import serializers
from .models import (
    SocialAccount, SocialPost, SocialSchedule, PlatformInsight
)


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social accounts."""
    
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'platform_user_id', 'platform_username',
            'platform_display_name', 'profile_picture', 'followers_count',
            'is_active', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'platform_user_id', 'platform_username',
            'platform_display_name', 'profile_picture', 'followers_count',
            'is_verified', 'created_at', 'updated_at'
        ]


class SocialPostSerializer(serializers.ModelSerializer):
    """Serializer for social posts."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SocialPost
        fields = [
            'id', 'user', 'social_account', 'platform', 'content',
            'hashtags', 'media_urls', 'product', 'product_name',
            'is_scheduled', 'scheduled_at', 'published_at',
            'status', 'external_post_id', 'post_url', 'platform_error',
            'impressions', 'clicks', 'likes', 'comments', 'shares',
            'engagements', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'published_at', 'status', 'external_post_id',
            'post_url', 'platform_error', 'impressions', 'clicks',
            'likes', 'comments', 'shares', 'engagements',
            'created_at', 'updated_at'
        ]


class SocialPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating social posts."""
    
    class Meta:
        model = SocialPost
        fields = [
            'platform', 'content', 'hashtags', 'media_urls',
            'product', 'is_scheduled', 'scheduled_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SocialScheduleSerializer(serializers.ModelSerializer):
    """Serializer for social schedules."""
    
    class Meta:
        model = SocialSchedule
        fields = [
            'id', 'platform', 'day_of_week', 'time',
            'content_template', 'include_product_link',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PlatformInsightSerializer(serializers.ModelSerializer):
    """Serializer for platform insights."""
    
    class Meta:
        model = PlatformInsight
        fields = [
            'id', 'date', 'followers', 'followers_gained', 'followers_lost',
            'profile_visits', 'reach', 'impressions', 'engagement_rate',
            'posts_published', 'top_post_impressions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PublishPostSerializer(serializers.Serializer):
    """Serializer for publishing posts."""
    post_id = serializers.IntegerField()
    platform = serializers.CharField()


class BulkPublishSerializer(serializers.Serializer):
    """Serializer for bulk publishing."""
    post_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    platform = serializers.CharField()

