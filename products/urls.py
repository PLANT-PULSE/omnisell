"""
URL patterns for products app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, ProductViewSet, ProductImageViewSet,
    SocialPostViewSet, PublicProductListView, PublicProductDetailView,
    PublicVendorProductsView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'', ProductViewSet, basename='products')
router.register(r'posts', SocialPostViewSet, basename='social-posts')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Public APIs - for buyers from social media
    path('public/list/', PublicProductListView.as_view(), name='public-product-list'),
    path('public/<int:pk>/', PublicProductDetailView.as_view(), name='public-product-detail'),
    path('public/vendor/<int:vendor_id>/', PublicVendorProductsView.as_view(), name='public-vendor-products'),
]
