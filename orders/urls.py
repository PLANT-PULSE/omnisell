"""
URL patterns for orders app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CartViewSet, OrderViewSet, CheckoutView,
    PaymentViewSet, PublicProductView, PublicOrderView
)

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    # Cart and Checkout
    path('', include(router.urls)),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    # Public URLs for social media sharing
    path('public/product/<int:product_id>/', PublicProductView.as_view(), name='public-product'),
    path('public/order/<uuid:order_uuid>/', PublicOrderView.as_view(), name='public-order'),
]
