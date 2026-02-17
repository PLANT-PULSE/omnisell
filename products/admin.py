"""
Admin configuration for products app.
"""
from django.contrib import admin
from .models import Product, ProductImage, Category, AIGeneratedContent


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin."""
    list_display = ['name', 'seller', 'price', 'stock_quantity', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'description', 'seller__email']
    raw_id_fields = ['seller', 'category']
    date_hierarchy = 'created_at'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Product image admin."""
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    raw_id_fields = ['product']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin."""
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AIGeneratedContent)
class AIGeneratedContentAdmin(admin.ModelAdmin):
    """AI generated content admin."""
    list_display = ['product', 'content_type', 'platform', 'is_used', 'created_at']
    list_filter = ['content_type', 'platform', 'is_used']
    raw_id_fields = ['product']
