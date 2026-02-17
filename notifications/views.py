"""
Views for notifications app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    PushDevice
)
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationPreferenceSerializer, NotificationTemplateSerializer,
    PushDeviceSerializer, MarkAsReadSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications."""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request):
        """Get user notifications."""
        queryset = self.get_queryset()
        
        # Filter by read status
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by type
        notification_type = request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Limit results
        limit = int(request.query_params.get('limit', 20))
        queryset = queryset[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Create a new notification (for internal use)."""
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response({
            'is_read': notification.is_read,
            'read_at': notification.read_at
        })
    
    @action(detail=False, methods=['post'])
    def mark_read_multiple(self, request):
        """Mark multiple notifications as read."""
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        if data.get('mark_all'):
            self.get_queryset().filter(is_read=False).update(
                is_read=True, read_at=timezone.now()
            )
            return Response({'message': 'All notifications marked as read.'})
        
        notification_ids = data.get('notification_ids', [])
        if notification_ids:
            self.get_queryset().filter(
                id__in=notification_ids,
                is_read=False
            ).update(is_read=True, read_at=timezone.now())
        
        return Response({'message': f'{len(notification_ids)} notifications marked as read.'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        
        return Response({'message': 'All notifications marked as read.'})
    
    @action(detail=False, methods=['delete'])
    def clear_read(self, request):
        """Delete all read notifications."""
        deleted_count, _ = self.get_queryset().filter(is_read=True).delete()
        
        return Response({
            'message': f'{deleted_count} notifications deleted.'
        })
    
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get notification counts."""
        queryset = self.get_queryset()
        
        total = queryset.count()
        unread = queryset.filter(is_read=False).count()
        
        return Response({
            'total': total,
            'unread': unread
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent unread notifications."""
        notifications = self.get_queryset().filter(
            is_read=False
        ).order_by('-created_at')[:5]
        
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for notification preferences."""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        pref, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return pref
    
    def list(self, request):
        """Get notification preferences."""
        pref = self.get_object()
        return Response(NotificationPreferenceSerializer(pref).data)
    
    def update(self, request):
        """Update notification preferences."""
        pref = self.get_object()
        serializer = self.get_serializer(
            pref, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for notification templates."""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationTemplateSerializer
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get templates by notification type."""
        notification_type = request.query_params.get('type')
        if not notification_type:
            return Response(
                {'error': 'Type is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = self.get_queryset().filter(
            notification_type=notification_type
        )
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class PushDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for push notification devices."""
    permission_classes = [IsAuthenticated]
    serializer_class = PushDeviceSerializer
    
    def get_queryset(self):
        return PushDevice.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['delete'])
    def unregister(self, request):
        """Unregister a push device."""
        device_token = request.data.get('device_token')
        if not device_token:
            return Response(
                {'error': 'Device token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device = get_object_or_404(
            PushDevice,
            user=request.user,
            device_token=device_token
        )
        device.delete()
        
        return Response({'message': 'Device unregistered.'})
    
    @action(detail=False, methods=['get'])
    def registered(self, request):
        """List registered devices."""
        devices = self.get_queryset().filter(is_active=True)
        return Response([{
            'id': d.id,
            'device_type': d.device_type,
            'device_name': d.device_name
        } for d in devices])


# Import timezone
from django.utils import timezone

