"""
Views for chat app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

from .models import (
    Conversation, Message, AIConversationContext,
    ChatSettings, AISuggestion
)
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer,
    AIConversationContextSerializer, AISuggestionSerializer,
    ChatSettingsSerializer, GenerateAISuggestionsSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for conversations."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Conversation.objects.filter(seller=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer_email__icontains=search) |
                Q(customer_name__icontains=search)
            )
        
        return queryset.order_by('-last_message_at')
    
    def create(self, request):
        """Create a new conversation."""
        customer_email = request.data.get('customer_email')
        customer_name = request.data.get('customer_name', '')
        product_id = request.data.get('product')
        source = request.data.get('source', 'website')
        
        # Check if conversation already exists
        existing = Conversation.objects.filter(
            seller=request.user,
            customer_email=customer_email,
            status='active'
        ).first()
        
        if existing:
            return Response(
                ConversationSerializer(existing).data,
                status=status.HTTP_200_OK
            )
        
        conversation = Conversation.objects.create(
            seller=request.user,
            customer_email=customer_email,
            customer_name=customer_name,
            product_id=product_id,
            source=source
        )
        
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update conversation status."""
        conversation = self.get_object()
        
        if 'status' in request.data:
            conversation.status = request.data['status']
            conversation.save()
        
        return Response(ConversationSerializer(conversation).data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages in a conversation."""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in conversation as read."""
        conversation = self.get_object()
        conversation.mark_as_read(request.user)
        
        return Response({'message': 'Messages marked as read.'})
    
    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        """Get AI suggestions for a conversation."""
        conversation = self.get_object()
        
        # Get recent suggestions
        suggestions = AISuggestion.objects.filter(
            conversation=conversation
        )[:5]
        
        serializer = AISuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_suggestions(self, request, pk=None):
        """Generate AI suggestions for the conversation."""
        conversation = self.get_object()
        
        try:
            from ai.services import AIChatAssistant
            assistant = AIChatAssistant()
            
            # Generate suggestions
            suggestions_data = assistant.generate_suggestions(
                conversation,
                request.data.get('types', [])
            )
            
            # Save suggestions
            for suggestion in suggestions_data:
                AISuggestion.objects.create(
                    user=request.user,
                    conversation=conversation,
                    suggestion_type=suggestion['type'],
                    content=suggestion['content']
                )
            
            return Response({
                'message': 'Suggestions generated.',
                'suggestions': suggestions_data
            })
            
        except ImportError:
            return Response(
                {'error': 'AI service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get total unread message count."""
        user = request.user
        count = Message.objects.filter(
            conversation__seller=user,
            recipient=user,
            is_read=False
        ).exclude(sender=user).count()
        
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active conversations count."""
        count = self.get_queryset().filter(status='active').count()
        return Response({'active_conversations': count})


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for messages."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation')
        
        if conversation_id:
            return Message.objects.filter(
                conversation_id=conversation_id,
                conversation__seller=user
            )
        
        return Message.objects.filter(
            conversation__seller=user
        )
    
    def create(self, request):
        """Send a new message."""
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')
        
        if not conversation_id or not content:
            return Response(
                {'error': 'Conversation ID and content are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            seller=request.user
        )
        
        # Determine recipient
        recipient = None
        last_message = conversation.messages.last()
        if last_message and last_message.sender != request.user:
            recipient = last_message.sender
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            recipient=recipient,
            content=content,
            message_type=request.data.get('message_type', 'text'),
            product_id=request.data.get('product'),
            is_ai_generated=request.data.get('is_ai_generated', False)
        )
        
        # Update conversation timestamp
        conversation.save()
        
        # Create notification
        from notifications.models import Notification
        if recipient:
            Notification.objects.create(
                user=recipient,
                title='New Message',
                message=f"New message from {request.user.email}",
                notification_type='chat',
                related_object_type='message',
                related_object_id=message.id
            )
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a message (e.g., mark as read)."""
        message = self.get_object()
        
        if 'is_read' in request.data and request.user != message.sender:
            message.is_read = request.data['is_read']
            message.save()
        
        return Response(MessageSerializer(message).data)
    
    @action(detail=False, methods=['post'])
    def mark_multiple_read(self, request):
        """Mark multiple messages as read."""
        message_ids = request.data.get('message_ids', [])
        
        if not message_ids:
            return Response(
                {'error': 'Message IDs are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Message.objects.filter(
            id__in=message_ids,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'message': 'Messages marked as read.'})


class ChatSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for chat settings."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSettingsSerializer
    
    def get_queryset(self):
        return ChatSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        settings, created = ChatSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings
    
    def list(self, request):
        """Get chat settings."""
        settings = self.get_object()
        return Response(ChatSettingsSerializer(settings).data)
    
    def update(self, request):
        """Update chat settings."""
        settings = self.get_object()
        serializer = self.get_serializer(
            settings, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


class AISuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for AI suggestions."""
    permission_classes = [IsAuthenticated]
    serializer_class = AISuggestionSerializer
    
    def get_queryset(self):
        return AISuggestion.objects.filter(
            conversation__seller=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def mark_used(self, request, pk=None):
        """Mark a suggestion as used."""
        suggestion = self.get_object()
        suggestion.was_used = True
        suggestion.save()
        
        return Response({'message': 'Suggestion marked as used.'})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent suggestions."""
        suggestions = self.get_queryset()[:10]
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)

