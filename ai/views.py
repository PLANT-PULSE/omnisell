"""
Views for AI services.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .services import AIContentGenerator, AIChatAssistant


class AIGeneratorViewSet(viewsets.GenericViewSet):
    """ViewSet for AI content generation."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_description(self, request):
        """Generate product description using AI."""
        product_id = request.data.get('product_id')
        tone = request.data.get('tone', 'professional')
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from products.models import Product
        product = get_object_or_404(
            Product, id=product_id, seller=request.user
        )
        
        try:
            generator = AIContentGenerator()
            description = generator.generate_product_description(product, tone)
            
            return Response({
                'description': description,
                'prompt': generator.last_prompt
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_hashtags(self, request):
        """Generate hashtags using AI."""
        product_id = request.data.get('product_id')
        platform = request.data.get('platform')
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from products.models import Product
        product = get_object_or_404(
            Product, id=product_id, seller=request.user
        )
        
        try:
            generator = AIContentGenerator()
            hashtags = generator.generate_hashtags(product, platform)
            
            return Response({
                'hashtags': hashtags,
                'prompt': generator.last_prompt
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_social_post(self, request):
        """Generate social media post using AI."""
        product_id = request.data.get('product_id')
        platform = request.data.get('platform')
        tone = request.data.get('tone', 'engaging')
        
        if not product_id or not platform:
            return Response(
                {'error': 'Product ID and platform are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from products.models import Product
        product = get_object_or_404(
            Product, id=product_id, seller=request.user
        )
        
        try:
            generator = AIContentGenerator()
            post = generator.generate_social_post(product, platform, tone)
            
            return Response({
                'post': post,
                'platform': platform,
                'prompt': generator.last_prompt
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIChatViewSet(viewsets.GenericViewSet):
    """ViewSet for AI chat assistance."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def analyze_conversation(self, request):
        """Analyze a conversation for context."""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'Conversation ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from chat.models import Conversation
        conversation = get_object_or_404(
            Conversation, id=conversation_id, seller=request.user
        )
        
        try:
            assistant = AIChatAssistant()
            context = assistant.analyze_conversation(conversation)
            
            return Response(context)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_suggestions(self, request):
        """Generate reply suggestions for a conversation."""
        conversation_id = request.data.get('conversation_id')
        types = request.data.get('types', ['general'])
        
        if not conversation_id:
            return Response(
                {'error': 'Conversation ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from chat.models import Conversation
        conversation = get_object_or_404(
            Conversation, id=conversation_id, seller=request.user
        )
        
        try:
            assistant = AIChatAssistant()
            suggestions = assistant.generate_suggestions(conversation, types)
            
            return Response({
                'suggestions': suggestions,
                'conversation_context': assistant.analyze_conversation(conversation)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def auto_reply(self, request):
        """Generate automatic reply for a conversation."""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'Conversation ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from chat.models import Conversation
        conversation = get_object_or_404(
            Conversation, id=conversation_id, seller=request.user
        )
        
        try:
            assistant = AIChatAssistant()
            result = assistant.auto_reply(conversation)
            
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def quick_suggestions(self, request):
        """Get predefined quick reply suggestions."""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'Conversation ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from chat.models import Conversation
        conversation = get_object_or_404(
            Conversation, id=conversation_id, seller=request.user
        )
        
        # Return predefined suggestions based on product context
        suggestions = [
            {
                'type': 'product_info',
                'content': "I'd be happy to help! Could you tell me more about what specific features you're looking for?"
            },
            {
                'type': 'warranty',
                'content': "Yes, all our products come with a 1-year manufacturer warranty."
            },
            {
                'type': 'shipping',
                'content': "We offer free shipping on orders over $50. Delivery typically takes 3-5 business days."
            },
            {
                'type': 'purchase',
                'content': "You can purchase directly through our secure checkout. Would you like me to send you the purchase link?"
            }
        ]
        
        return Response({
            'suggestions': suggestions,
            'conversation_id': conversation_id
        })

