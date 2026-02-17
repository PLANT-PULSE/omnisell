"""
Serializers for orders app.
"""
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, Payment, Refund


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2, read_only=True
    )
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'price',
            'quantity', 'total', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']
    
    def get_product_image(self, obj):
        """Get primary product image URL."""
        if obj.product and obj.product.images.exists():
            image = obj.product.images.filter(is_primary=True).first()
            if not image:
                image = obj.product.images.first()
            if image and image.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(image.image.url)
                return image.image.url
        return None
    
    def get_total(self, obj):
        """Get total price."""
        return obj.get_total()


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart."""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        """Get cart total."""
        return obj.get_total()
    
    def get_item_count(self, obj):
        """Get total item count."""
        return obj.get_item_count()


class CartAddItemSerializer(serializers.Serializer):
    """Serializer for adding item to cart."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartUpdateItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image',
            'price', 'quantity', 'total'
        ]


class ShippingAddressSerializer(serializers.ModelSerializer):
    """Serializer for shipping address."""
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'full_name', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country',
            'delivery_instructions', 'is_delivered', 'delivered_at'
        ]
        read_only_fields = ['id', 'is_delivered', 'delivered_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_method', 'amount', 'currency', 'status',
            'provider', 'transaction_id', 'card_last4', 'card_brand',
            'payment_description', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'transaction_id', 'created_at', 'completed_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payment."""
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    order_id = serializers.CharField()
    # Card details (for card payments) - should be tokenized
    card_token = serializers.CharField(required=False, allow_blank=True)
    # Mobile money details
    phone_number = serializers.CharField(required=False, allow_blank=True)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    seller_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'uuid', 'buyer', 'buyer_email', 'buyer_name',
            'seller', 'seller_name', 'status', 'subtotal', 'tax',
            'shipping_cost', 'discount', 'total_amount', 'currency',
            'buyer_note', 'seller_note', 'source', 'referral_code',
            'items', 'shipping_address', 'payments',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at',
            'delivered_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'order_id', 'uuid', 'created_at', 'updated_at',
            'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at'
        ]
    
    def get_seller_name(self, obj):
        if obj.seller:
            return obj.seller.get_full_name() or obj.seller.email
        return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating order from cart."""
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(allow_blank=True)
        )
    )
    shipping_address = ShippingAddressSerializer()
    buyer_note = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    source = serializers.CharField(required=False, allow_blank=True)


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list."""
    item_count = serializers.SerializerMethodField()
    first_item_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'status', 'total_amount', 'currency',
            'item_count', 'first_item_name', 'created_at'
        ]
    
    def get_item_count(self, obj):
        return obj.items.count()
    
    def get_first_item_name(self, obj):
        first_item = obj.items.first()
        return first_item.product_name if first_item else None


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout process."""
    # Items from cart
    item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    # Shipping info
    full_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20)
    address_line1 = serializers.CharField(max_length=255)
    address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100, default='Ghana')
    delivery_instructions = serializers.CharField(required=False, allow_blank=True)
    
    # Payment
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    
    # Additional
    buyer_note = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refunds."""
    class Meta:
        model = Refund
        fields = [
            'id', 'order', 'payment', 'amount', 'reason',
            'status', 'refunded_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'refunded_at', 'created_at']
