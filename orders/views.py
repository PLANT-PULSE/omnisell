"""
Views for orders app - Cart, Order, and Payment handling.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
import decimal

from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, Payment, Refund
from .serializers import (
    CartSerializer, CartItemSerializer, CartAddItemSerializer,
    CartUpdateItemSerializer, OrderSerializer, OrderListSerializer,
    OrderCreateSerializer, ShippingAddressSerializer, PaymentSerializer,
    PaymentCreateSerializer, CheckoutSerializer, RefundSerializer
)
from products.models import Product


class CartViewSet(viewsets.GenericViewSet):
    """ViewSet for cart operations."""
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_or_create_cart(self):
        """Get or create cart for current user."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request):
        """Get current user's cart."""
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], serializer_class=CartAddItemSerializer)
    def add_item(self, request):
        """Add item to cart."""
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Get product
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Check stock
        if product.track_inventory and product.stock_quantity < quantity:
            return Response(
                {'error': f'Only {product.stock_quantity} items available in stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = self.get_or_create_cart()
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            # Check stock
            if product.track_inventory and product.stock_quantity < cart_item.quantity:
                cart_item.quantity = product.stock_quantity
            cart_item.save()
        
        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['put'], url_path='update_item/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update cart item quantity."""
        serializer = CartUpdateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_or_create_cart()
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        quantity = serializer.validated_data['quantity']
        
        # Check stock
        if cart_item.product.track_inventory:
            if cart_item.product.stock_quantity < quantity:
                return Response(
                    {'error': f'Only {cart_item.product.stock_quantity} items available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if quantity <= 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart.'})
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response(CartSerializer(cart).data)
    
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart."""
        cart = self.get_or_create_cart()
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return Response(CartSerializer(cart).data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart."""
        cart = self.get_or_create_cart()
        cart.clear()
        
        return Response({'message': 'Cart cleared successfully.'})


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for order operations."""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(buyer=user)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('-created_at')
    
    def get_seller_orders(self):
        """Get orders for sellers."""
        user = self.request.user
        return Order.objects.filter(seller=user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def seller_orders(self, request):
        """Get orders for sellers."""
        queryset = self.get_seller_orders()
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an order (seller action)."""
        order = self.get_object()
        order.confirm()
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Mark order as shipped."""
        order = self.get_object()
        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.save()
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Mark order as delivered."""
        order = self.get_object()
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        
        # Update shipping address
        shipping = order.shipping_address
        if shipping:
            shipping.is_delivered = True
            shipping.delivered_at = timezone.now()
            shipping.save()
        
        order.save()
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        reason = request.data.get('reason', '')
        
        if order.status in ['delivered', 'cancelled', 'refunded']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.cancel()
        if reason:
            order.seller_note = reason
            order.save()
        
        return Response(OrderSerializer(order).data)


class CheckoutView(APIView):
    """View for checkout process."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process checkout."""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Get cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get items to checkout
        item_ids = data.get('item_ids')
        if item_ids:
            cart_items = cart.items.filter(id__in=item_ids)
        else:
            cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response(
                {'error': 'No items selected for checkout.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate totals
        subtotal = decimal.Decimal('0')
        for item in cart_items:
            subtotal += item.get_total()
        
        tax = (subtotal * decimal.Decimal('0.10')).quantize(decimal.Decimal('0.01'))
        shipping_cost = decimal.Decimal('0') if subtotal >= 50 else decimal.Decimal('5.00')
        total = subtotal + tax + shipping_cost
        
        # Create order
        order = Order.objects.create(
            buyer=request.user,
            buyer_email=request.user.email,
            buyer_name=data.get('full_name'),
            seller=cart_items.first().product.seller,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total_amount=total,
            buyer_note=data.get('buyer_note', ''),
            source=data.get('source', 'website')
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_image=item.product.images.first().image.url if item.product.images.exists() else None,
                price=item.product.price,
                quantity=item.quantity,
                total=item.get_total()
            )
        
        # Create shipping address
        ShippingAddress.objects.create(
            order=order,
            full_name=data['full_name'],
            phone=data['phone'],
            address_line1=data['address_line1'],
            address_line2=data.get('address_line2', ''),
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country=data.get('country', 'Ghana'),
            delivery_instructions=data.get('delivery_instructions', '')
        )
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=data['payment_method'],
            amount=total,
            status='pending'
        )
        
        # Clear cart items
        cart_items.delete()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payment operations."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process payment (mock implementation - integrate with payment gateway)."""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': f'Payment is already {payment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, integrate with Stripe, Flutterwave, etc.
        # For now, simulate successful payment
        payment.status = 'completed'
        payment.transaction_id = f'TXN{timezone.now().strftime("%Y%m%d%H%M%S")}'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order status
        order = payment.order
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        
        return Response(PaymentSerializer(payment).data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify payment status with provider."""
        payment = self.get_object()
        
        # In production, verify with payment provider
        # For now, return current status
        return Response(PaymentSerializer(payment).data)


class PublicProductView(APIView):
    """
    Public API for viewing products from social media shares.
    Accessible without authentication.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, product_id=None):
        """Get public product details."""
        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id, status='active')
        
        # Increment view count
        product.view_count += 1
        product.save(update_fields=['view_count'])
        
        from products.serializers import ProductSerializer
        serializer = ProductSerializer(product)
        
        return Response({
            'product': serializer.data,
            'seller': {
                'name': product.seller.get_full_name() or product.seller.email,
                'profile': getattr(product.seller, 'profile', None)
            }
        })


class PublicOrderView(APIView):
    """
    Public API for viewing order details via UUID link.
    Used for order tracking from social media.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, order_uuid=None):
        """Get order details by UUID."""
        if not order_uuid:
            return Response(
                {'error': 'Order UUID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(Order, uuid=order_uuid)
        
        # Return limited order info for public tracking
        return Response({
            'order_id': order.order_id,
            'status': order.status,
            'items': OrderItemSerializer(order.items.all(), many=True).data,
            'shipping_address': ShippingAddressSerializer(order.shipping_address).data,
            'created_at': order.created_at,
            'delivered_at': order.delivered_at
        })
