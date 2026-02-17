"""
Serializers for user authentication and profiles.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Profile, ConnectedPlatform, UserActivity

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create profile for the user
        Profile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'is_verified', 'onboarding_completed', 'onboarding_step',
            'ai_description_enabled', 'ai_hashtags_enabled', 'ai_replies_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with user details."""
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_verified',
            'avatar', 'bio', 'website', 'company_name', 'business_type',
            'country', 'city', 'total_products', 'total_sales', 'rating',
            'total_ratings', 'positive_feedback', 'currency', 'dark_mode',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'email', 'is_verified', 'total_products', 'total_sales',
            'rating', 'total_ratings', 'positive_feedback', 'created_at', 'updated_at'
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile."""
    class Meta:
        model = Profile
        fields = [
            'avatar', 'bio', 'website', 'company_name', 'business_type',
            'country', 'city', 'currency', 'dark_mode'
        ]


class ConnectedPlatformSerializer(serializers.ModelSerializer):
    """Serializer for connected social platforms."""
    class Meta:
        model = ConnectedPlatform
        fields = [
            'id', 'platform', 'platform_user_id', 'platform_username',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'platform_user_id', 'created_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user info."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['onboarding_completed'] = user.onboarding_completed
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = UserSerializer(self.user).data
        
        return data


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity."""
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'title', 'description',
            'related_object_type', 'related_object_id', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OnboardingProgressSerializer(serializers.Serializer):
    """Serializer for tracking onboarding progress."""
    current_step = serializers.IntegerField()
    total_steps = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    progress_percentage = serializers.IntegerField()

