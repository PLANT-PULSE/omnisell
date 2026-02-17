"""
Views for products app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Sum, Count

from .models import (
    Category, Product, ProductImage, ProductVideo,
    AIGeneratedContent, SocialPost, ProductView
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer,
    ProductVideoSerializer, SocialPostSerializer,
    SocialPostCreateSerializer, ProductStatsSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for product categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get('parent')
        if parent_id == 'null':
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure."""
        categories = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for product operations."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.filter(seller=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def create(self, request):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(seller=request.user)
        
        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a product."""
        product = self.get_object()
        serializer = self.get_serializer(
            product, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(ProductSerializer(product).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get product statistics for the seller."""
        products = self.get_queryset()
        
        stats = {
            'total_products': products.count(),
            'active_products': products.filter(status='active').count(),
            'draft_products': products.filter(status='draft').count(),
            'total_views': products.aggregate(Sum('view_count'))['view_count__sum'] or 0,
            'total_clicks': products.aggregate(Sum('click_count'))['click_count__sum'] or 0,
            'total_shares': products.aggregate(Sum('share_count'))['share_count__sum'] or 0,
        }
        
        serializer = ProductStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for products."""
        products = self.get_queryset()
        
        recent_products = products[:5]
        
        data = {
            'total_products': products.count(),
            'active_products': products.filter(status='active').count(),
            'total_views': products.aggregate(Sum('view_count'))['view_count__sum'] or 0,
            'total_clicks': products.aggregate(Sum('click_count'))['click_count__sum'] or 0,
            'recent_products': ProductListSerializer(recent_products, many=True).data,
        }
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """Upload images for a product."""
        product = self.get_object()
        
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        
        images = product.images.all()
        return Response(
            ProductImageSerializer(images, many=True).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """Delete a product image."""
        product = self.get_object()
        image_id = request.data.get('image_id')
        
        if not image_id:
            return Response(
                {'error': 'Image ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image = get_object_or_404(ProductImage, id=image_id, product=product)
        image.delete()
        
        return Response({'message': 'Image deleted successfully.'})
    
    @action(detail=True, methods=['post'])
    def generate_ai_content(self, request, pk=None):
        """Generate AI content for a product."""
        product = self.get_object()
        content_type = request.data.get('content_type', 'description')
        platform = request.data.get('platform', '')
        
        # Import AI service
        try:
            from ai.services import AIContentGenerator
            generator = AIContentGenerator()
            
            if content_type == 'description':
                content = generator.generate_product_description(product)
                product.ai_description = content
                product.ai_content_generated = True
                product.save()
                
                # Save to AI content
                AIGeneratedContent.objects.create(
                    product=product,
                    content_type='description',
                    content=content,
                    prompt=generator.last_prompt
                )
                
                return Response({
                    'message': 'Description generated successfully.',
                    'description': content
                })
            
            elif content_type == 'hashtags':
                content = generator.generate_hashtags(product)
                product.ai_hashtags = content
                product.ai_content_generated = True
                product.save()
                
                AIGeneratedContent.objects.create(
                    product=product,
                    content_type='hashtags',
                    content=content,
                    prompt=generator.last_prompt
                )
                
                return Response({
                    'message': 'Hashtags generated successfully.',
                    'hashtags': content
                })
            
            elif content_type == 'social_post':
                content = generator.generate_social_post(product, platform)
                
                AIGeneratedContent.objects.create(
                    product=product,
                    content_type=f'social_post_{platform}',
                    platform=platform,
                    content=content,
                    prompt=generator.last_prompt
                )
                
                return Response({
                    'message': f'{platform.capitalize()} post generated.',
                    'caption': content
                })
                
        except ImportError:
            return Response(
                {'error': 'AI service not available.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response(
            {'error': 'Invalid content type.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def create_social_post(self, request, pk=None):
        """Create and publish a social media post for a product."""
        product = self.get_object()
        serializer = SocialPostCreateSerializer(data={
            **request.data,
            'product': product.id
        })
        serializer.is_valid(raise_exception=True)
        social_post = serializer.save()
        
        return Response(
            SocialPostSerializer(social_post).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def social_posts(self, request, pk=None):
        """Get all social posts for a product."""
        product = self.get_object()
        posts = product.social_posts.all()
        serializer = SocialPostSerializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a product."""
        product = self.get_object()
        product.status = 'active'
        product.save()
        
        return Response({
            'message': 'Product published successfully.',
            'status': product.status
        })
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a product."""
        product = self.get_object()
        product.status = 'archived'
        product.save()
        
        return Response({
            'message': 'Product archived successfully.',
            'status': product.status
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk action on products."""
        serializer = BulkProductActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_ids = serializer.validated_data['product_ids']
        action = serializer.validated_data['action']
        
        products = self.get_queryset().filter(id__in=product_ids)
        
        if action == 'delete':
            products.delete()
            return Response({'message': f'{len(product_ids)} products deleted.'})
        
        elif action == 'activate':
            products.update(status='active')
            return Response({'message': f'{len(product_ids)} products activated.'})
        
        elif action == 'deactivate':
            products.update(status='inactive')
            return Response({'message': f'{len(product_ids)} products deactivated.'})
        
        return Response(
            {'error': 'Invalid action.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for product images."""
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        return ProductImage.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        product = get_object_or_404(Product, id=product_id, seller=self.request.user)
        serializer.save(product=product)
    
    def create(self, request, product_pk=None):
        """Add image to product."""
        product = get_object_or_404(Product, id=product_pk, seller=request.user)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class SocialPostViewSet(viewsets.ModelViewSet):
    """ViewSet for social media posts."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SocialPostCreateSerializer
        return SocialPostSerializer
    
    def get_queryset(self):
        user = self.request.user
        return SocialPost.objects.filter(product__seller=user)
    
    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = get_object_or_404(Product, id=product_id, seller=self.request.user)
        serializer.save(product=product)
    
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
    def scheduled(self, request):
        """Get scheduled posts."""
        posts = self.get_queryset().filter(
            is_scheduled=True,
            status='scheduled'
        ).order_by('scheduled_at')
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish_now(self, request, pk=None):
        """Publish a scheduled post immediately."""
        post = self.get_object()
        
        # Import social media service
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
    def cancel(self, request, pk=None):
        """Cancel a scheduled post."""
        post = self.get_object()
        post.status = 'draft'
        post.is_scheduled = False
        post.scheduled_at = None
        post.save()
        
        return Response({'message': 'Post cancelled.'})


# Import timezone for publish_now
from django.utils import timezone


# =============================================================================
# PUBLIC APIS - For buyers viewing products from social media links
# =============================================================================

class PublicProductListView(APIView):
    """
    Public API for browsing active products.
    Accessible without authentication - for buyers from social media.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of public active products."""
        queryset = Product.objects.filter(status='active').order_by('-created_at')
        
        # Filter by category
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(tags__icontains=search)
            )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data)


class PublicProductDetailView(APIView):
    """
    Public API for viewing single product details.
    Accessible without authentication - for buyers viewing from social shares.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, pk=None):
        """Get public product details by ID."""
        product = get_object_or_404(Product, pk=pk, status='active')
        
        # Increment view count
        product.view_count += 1
        product.save(update_fields=['view_count'])
        
        # Record the view with source tracking
        source = request.query_params.get('source', 'direct')
        ProductView.objects.create(
            product=product,
            source=source,
            referrer=request.META.get('HTTP_REFERER', '')
        )
        
        serializer = ProductSerializer(product)
        data = serializer.data
        
        # Add seller info (limited)
        data['seller'] = {
            'id': product.seller.id,
            'name': product.seller.get_full_name() or product.seller.email,
            'rating': getattr(product.seller.profile, 'rating', 0) if hasattr(product.seller, 'profile') else 0,
        }
        
        return Response(data)


class PublicVendorProductsView(APIView):
    """
    Public API for viewing products from a specific vendor.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, vendor_id=None):
        """Get products from a specific seller/vendor."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        seller = get_object_or_404(User, id=vendor_id)
        products = Product.objects.filter(
            seller=seller,
            status='active'
        ).order_by('-created_at')
        
        # Get vendor info
        vendor_info = {
            'id': seller.id,
            'name': seller.get_full_name() or seller.email,
            'bio': getattr(seller.profile, 'bio', '') if hasattr(seller, 'profile') else '',
            'rating': getattr(seller.profile, 'rating', 0) if hasattr(seller, 'profile') else 0,
            'total_sales': getattr(seller.profile, 'total_sales', 0) if hasattr(seller, 'profile') else 0,
        }
        
        serializer = ProductListSerializer(products, many=True)
        return Response({
            'vendor': vendor_info,
            'products': serializer.data,
            'count': products.count()
        })

