"""
Views for social media app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    SocialAccount, SocialPost, SocialSchedule, PlatformInsight
)
from .serializers import (
    SocialAccountSerializer, SocialPostSerializer,
    SocialPostCreateSerializer, SocialScheduleSerializer,
    PlatformInsightSerializer
)


class SocialAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for social accounts."""
    permission_classes = [IsAuthenticated]
    serializer_class = SocialAccountSerializer
    
    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def connected(self, request):
        """List connected platforms."""
        accounts = self.get_queryset().filter(is_active=True)
        return Response([{
            'platform': a.platform,
            'username': a.platform_username,
            'followers': a.followers_count,
            'connected': True
        } for a in accounts])
    
    @action(detail=False, methods=['post'])
    def disconnect(self, request):
        """Disconnect a social account."""
        platform = request.data.get('platform')
        if not platform:
            return Response(
                {'error': 'Platform is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        account = get_object_or_404(
            SocialAccount,
            user=request.user,
            platform=platform
        )
        account.is_active = False
        account.save()
        
        return Response({'message': f'{platform} disconnected successfully.'})
    
    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """Get insights for a social account."""
        account = self.get_object()
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=days)
        
        insights = account.insights.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        serializer = PlatformInsightSerializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh the access token for a social account."""
        account = self.get_object()
        
        try:
            from social.services import SocialMediaAuth
            auth = SocialMediaAuth()
            auth.refresh_token(account)
            
            return Response({'message': 'Token refreshed successfully.'})
        except ImportError:
            return Response(
                {'error': 'Social media service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class SocialPostViewSet(viewsets.ModelViewSet):
    """ViewSet for social posts."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SocialPostCreateSerializer
        return SocialPostSerializer
    
    def get_queryset(self):
        return SocialPost.objects.filter(user=self.request.user)
    
    def create(self, request):
        """Create a new social post."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=request.user)
        
        return Response(
            SocialPostSerializer(post).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a post to social media."""
        post = self.get_object()
        
        try:
            from social.services import SocialMediaPublisher
            publisher = SocialMediaPublisher()
            
            result = publisher.publish_post(post)
            
            if result['success']:
                post.status = 'published'
                post.published_at = timezone.now()
                post.external_post_id = result.get('post_id')
                post.post_url = result.get('post_url')
                post.save()
                
                return Response({
                    'message': 'Post published successfully.',
                    'post_url': post.post_url
                })
            else:
                post.status = 'failed'
                post.platform_error = result.get('error', 'Unknown error')
                post.save()
                return Response(
                    {'error': result.get('error', 'Publishing failed.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ImportError:
            return Response(
                {'error': 'Social media service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a post."""
        post = self.get_object()
        scheduled_at = request.data.get('scheduled_at')
        
        if not scheduled_at:
            return Response(
                {'error': 'Scheduled time is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import dateparse
        parsed_time = dateparse.parse_datetime(scheduled_at)
        
        if not parsed_time:
            return Response(
                {'error': 'Invalid datetime format.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.is_scheduled = True
        post.scheduled_at = parsed_time
        post.status = 'scheduled'
        post.save()
        
        return Response({
            'message': 'Post scheduled successfully.',
            'scheduled_at': post.scheduled_at
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled post."""
        post = self.get_object()
        post.status = 'draft'
        post.is_scheduled = False
        post.scheduled_at = None
        post.save()
        
        return Response({'message': 'Post cancelled.'})
    
    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Get scheduled posts."""
        posts = self.get_queryset().filter(
            is_scheduled=True,
            status='scheduled'
        ).order_by('scheduled_at')
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        """Get posts by platform."""
        platform = request.query_params.get('platform')
        if not platform:
            return Response(
                {'error': 'Platform is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        posts = self.get_queryset().filter(platform=platform)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent posts."""
        limit = int(request.query_params.get('limit', 10))
        posts = self.get_queryset()[:limit]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_publish(self, request):
        """Publish multiple posts."""
        post_ids = request.data.get('post_ids', [])
        platform = request.data.get('platform')
        
        if not post_ids or not platform:
            return Response(
                {'error': 'Post IDs and platform are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        posts = self.get_queryset().filter(id__in=post_ids)
        results = []
        
        for post in posts:
            try:
                from social.services import SocialMediaPublisher
                publisher = SocialMediaPublisher()
                result = publisher.publish_post(post)
                results.append({
                    'post_id': post.id,
                    'success': result['success'],
                    'error': result.get('error')
                })
            except ImportError:
                results.append({
                    'post_id': post.id,
                    'success': False,
                    'error': 'Service unavailable'
                })
        
        return Response({'results': results})


class SocialScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for social schedules."""
    permission_classes = [IsAuthenticated]
    serializer_class = SocialScheduleSerializer
    
    def get_queryset(self):
        return SocialSchedule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active schedules."""
        schedules = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle schedule active status."""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        
        return Response({
            'is_active': schedule.is_active,
            'message': f'Schedule {"activated" if schedule.is_active else "paused"}.'
        })


class OAuthCallbackViewSet(viewsets.GenericViewSet):
    """Handle OAuth callbacks from social platforms."""
    permission_classes = []
    authentication_classes = []
    
    @action(detail=False, methods=['get'])
    def facebook(self, request):
        """Handle Facebook OAuth callback."""
        code = request.query_params.get('code')
        if not code:
            return Response(
                {'error': 'Authorization code not provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from social.services import SocialMediaAuth
            auth = SocialMediaAuth()
            result = auth.handle_facebook_callback(code, request.user)
            
            return Response(result)
        except ImportError:
            return Response(
                {'error': 'Social media service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['get'])
    def instagram(self, request):
        """Handle Instagram OAuth callback."""
        code = request.query_params.get('code')
        if not code:
            return Response(
                {'error': 'Authorization code not provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from social.services import SocialMediaAuth
            auth = SocialMediaAuth()
            result = auth.handle_instagram_callback(code, request.user)
            
            return Response(result)
        except ImportError:
            return Response(
                {'error': 'Social media service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['get'])
    def twitter(self, request):
        """Handle Twitter OAuth callback."""
        code = request.query_params.get('code')
        if not code:
            return Response(
                {'error': 'Authorization code not provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from social.services import SocialMediaAuth
            auth = SocialMediaAuth()
            result = auth.handle_twitter_callback(code, request.user)
            
            return Response(result)
        except ImportError:
            return Response(
                {'error': 'Social media service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

