"""
Views for user authentication and profiles.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Profile, ConnectedPlatform, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserProfileSerializer,
    ProfileUpdateSerializer, ConnectedPlatformSerializer,
    UserActivitySerializer, CustomTokenObtainPairSerializer
)

User = get_user_model()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    """ViewSet for user registration."""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request):
        """Register a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create activity
        UserActivity.objects.create(
            user=user,
            activity_type='platform_connected',
            title='Account created',
            description='New seller account created on SellFlow',
            metadata={'action': 'registration'}
        )
        
        return Response({
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with user info in response."""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet for user operations."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user
    
    def list(self, request):
        """Get current user details."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def update(self, request):
        """Update current user."""
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details (alias for list)."""
        return self.list(request)
    
    @action(detail=False, methods=['post'])
    def complete_onboarding(self, request):
        """Mark onboarding as completed."""
        user = request.user
        user.onboarding_completed = True
        user.onboarding_step = 3
        user.save()
        
        return Response({
            'message': 'Onboarding completed successfully.',
            'onboarding_completed': True
        })
    
    @action(detail=False, methods=['post'])
    def update_onboarding_step(self, request):
        """Update onboarding step."""
        step = request.data.get('step', 0)
        user = request.user
        user.onboarding_step = step
        user.save()
        
        return Response({
            'message': 'Onboarding step updated.',
            'current_step': user.onboarding_step,
            'is_completed': user.onboarding_completed
        })
    
    @action(detail=False, methods=['get'])
    def onboarding_progress(self, request):
        """Get onboarding progress."""
        user = request.user
        total_steps = 3
        current_step = user.onboarding_step
        is_completed = user.onboarding_completed
        progress_percentage = int((current_step / total_steps) * 100) if not is_completed else 100
        
        return Response({
            'current_step': current_step,
            'total_steps': total_steps,
            'is_completed': is_completed,
            'progress_percentage': progress_percentage
        })


class ProfileViewSet(viewsets.GenericViewSet):
    """ViewSet for user profile operations."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    def list(self, request):
        """Get user profile."""
        profile = self.get_object()
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def update(self, request):
        """Update user profile."""
        profile = self.get_object()
        serializer = ProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Update related user fields if provided
        user_data = {}
        for field in ['first_name', 'last_name']:
            if field in request.data:
                user_data[field] = request.data[field]
        
        if user_data:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.filter(id=request.user.id).update(**user_data)
        
        return Response(UserProfileSerializer(profile).data)
    
    @action(detail=False, methods=['post'])
    def update_theme(self, request):
        """Update theme preference."""
        profile = self.get_object()
        dark_mode = request.data.get('dark_mode', False)
        profile.dark_mode = dark_mode
        profile.save()
        
        return Response({
            'dark_mode': profile.dark_mode,
            'message': 'Theme updated successfully.'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get seller statistics."""
        profile = self.get_object()
        return Response({
            'total_products': profile.total_products,
            'total_sales': float(profile.total_sales),
            'rating': float(profile.rating),
            'total_ratings': profile.total_ratings,
            'positive_feedback': profile.positive_feedback
        })


class ConnectedPlatformViewSet(viewsets.ModelViewSet):
    """ViewSet for connected social platforms."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectedPlatformSerializer
    
    def get_queryset(self):
        return ConnectedPlatform.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def list_platforms(self, request):
        """List all connected platforms."""
        platforms = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(platforms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def disconnect(self, request):
        """Disconnect a platform."""
        platform = request.data.get('platform')
        if not platform:
            return Response(
                {'error': 'Platform is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        connected = get_object_or_404(
            ConnectedPlatform,
            user=request.user,
            platform=platform
        )
        connected.is_active = False
        connected.save()
        
        return Response({'message': f'{platform} disconnected successfully.'})


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user activities."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserActivitySerializer
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities."""
        limit = request.query_params.get('limit', 10)
        activities = self.get_queryset()[:int(limit)]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get activities by type."""
        activity_type = request.query_params.get('type')
        if not activity_type:
            return Response(
                {'error': 'Activity type is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        activities = self.get_queryset().filter(activity_type=activity_type)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

