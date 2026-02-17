"""
Admin configuration for orders app.
"""
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, Payment, Refund


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__email']
    raw_id_fields = ['user']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']
    raw_id_fields = ['cart', 'product']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity', 'total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_method', 'amount', 'status', 'transaction_id', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'buyer_email', 'seller', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['order_id', 'buyer_email', 'buyer_name']
    raw_id_fields = ['buyer', 'seller']
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ['order_id', 'uuid', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'quantity', 'price', 'total']
    search_fields = ['order__order_id', 'product_name']
    raw_id_fields = ['order', 'product']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'full_name', 'city', 'country', 'is_delivered']
    list_filter = ['country', 'is_delivered']
    search_fields = ['full_name', 'order__order_id']
    raw_id_fields = ['order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__order_id', 'transaction_id']
    raw_id_fields = ['order', 'user']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    raw_id_fields = ['order', 'payment']
