"""
Serializers for products app.
"""
from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, ProductVideo,
    AIGeneratedContent, SocialPost, ProductView
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent',
            'image', 'is_active', 'children', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []
    
    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'is_primary', 'sort_order',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading product images."""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary', 'sort_order']


class ProductVideoSerializer(serializers.ModelSerializer):
    """Serializer for product videos."""
    
    class Meta:
        model = ProductVideo
        fields = [
            'id', 'video', 'video_url', 'thumbnail', 'title',
            'duration', 'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AIGeneratedContentSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated content."""
    
    class Meta:
        model = AIGeneratedContent
        fields = [
            'id', 'content_type', 'platform', 'content', 'prompt',
            'is_used', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SocialPostSerializer(serializers.ModelSerializer):
    """Serializer for social media posts."""
    
    class Meta:
        model = SocialPost
        fields = [
            'id', 'product', 'platform', 'caption', 'hashtags',
            'image', 'video', 'is_scheduled', 'scheduled_at',
            'published_at', 'status', 'external_post_id', 'post_url',
            'clicks', 'impressions', 'engagements',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'published_at', 'external_post_id', 'post_url',
            'clicks', 'impressions', 'engagements',
            'created_at', 'updated_at'
        ]


class SocialPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating social posts."""
    
    class Meta:
        model = SocialPost
        fields = [
            'product', 'platform', 'caption', 'hashtags',
            'image', 'video', 'is_scheduled', 'scheduled_at'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Main product serializer."""
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    ai_contents = AIGeneratedContentSerializer(many=True, read_only=True)
    social_posts = SocialPostSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_email', 'name', 'description',
            'price', 'compare_at_price', 'currency',
            'sku', 'stock_quantity', 'track_inventory', 'allow_backorder',
            'category', 'category_name', 'tags', 'status',
            'ai_description', 'ai_hashtags', 'ai_content_generated',
            'meta_title', 'meta_description',
            'view_count', 'click_count', 'share_count',
            'images', 'videos', 'ai_contents', 'social_posts',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'seller', 'seller_email', 'view_count', 'click_count',
            'share_count', 'ai_content_generated', 'created_at',
            'updated_at', 'published_at'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'compare_at_price', 'currency',
            'category', 'category_name', 'status',
            'stock_quantity', 'view_count', 'click_count',
            'primary_image', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        first = obj.images.first()
        if first:
            return ProductImageSerializer(first).data
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'compare_at_price', 'currency',
            'sku', 'stock_quantity', 'track_inventory', 'allow_backorder',
            'category', 'tags', 'status',
            'meta_title', 'meta_description'
        ]
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class ProductStatsSerializer(serializers.Serializer):
    """Serializer for product statistics."""
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    draft_products = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_shares = serializers.IntegerField()


class BulkProductActionSerializer(serializers.Serializer):
    """Serializer for bulk product actions."""
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'delete'])

