"""
Serializers for analytics app.
"""
from rest_framework import serializers
from .models import (
    DailyAnalytics, PlatformAnalytics, ProductAnalytics,
    ConversionFunnel, TopProduct, AnalyticsEvent
)


class DailyAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for daily analytics."""
    
    class Meta:
        model = DailyAnalytics
        fields = [
            'id', 'date', 'revenue', 'orders_count', 'average_order_value',
            'page_views', 'unique_visitors', 'sessions',
            'clicks', 'leads', 'conversions',
            'social_clicks', 'social_impressions', 'social_engagements',
            'platform_stats', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for platform analytics."""
    
    class Meta:
        model = PlatformAnalytics
        fields = [
            'id', 'date', 'platform',
            'impressions', 'clicks', 'engagements',
            'leads', 'conversions', 'revenue',
            'click_through_rate', 'engagement_rate',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for product analytics."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductAnalytics
        fields = [
            'id', 'product', 'product_name', 'date',
            'views', 'unique_views', 'clicks', 'leads',
            'conversions', 'revenue',
            'views_by_source', 'clicks_by_source',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversionFunnelSerializer(serializers.ModelSerializer):
    """Serializer for conversion funnel."""
    
    class Meta:
        model = ConversionFunnel
        fields = [
            'id', 'date',
            'impressions', 'visits', 'product_views',
            'add_to_carts', 'checkouts', 'purchases',
            'visit_to_product_rate', 'product_to_cart_rate',
            'cart_to_checkout_rate', 'checkout_to_purchase_rate',
            'overall_conversion_rate',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TopProductSerializer(serializers.ModelSerializer):
    """Serializer for top products."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = TopProduct
        fields = [
            'id', 'product', 'product_name', 'date',
            'metric_type', 'value', 'rank',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events."""
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'user', 'session_id', 'event_type',
            'product', 'platform', 'source', 'medium', 'campaign',
            'country', 'city', 'device_type', 'browser', 'os',
            'metadata', 'referrer', 'ip_address', 'user_agent',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_products = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_leads = serializers.IntegerField()


class PerformanceOverviewSerializer(serializers.Serializer):
    """Serializer for performance overview."""
    period = serializers.CharField()
    revenue_data = serializers.ListField()
    clicks_data = serializers.ListField()
    leads_data = serializers.ListField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_clicks = serializers.IntegerField()
    total_leads = serializers.IntegerField()


class PlatformEngagementSerializer(serializers.Serializer):
    """Serializer for platform engagement data."""
    platform = serializers.CharField()
    clicks = serializers.IntegerField()
    change_percent = serializers.DecimalField(max_digits=6, decimal_places=2)


class ConversionSummarySerializer(serializers.Serializer):
    """Serializer for conversion summary."""
    click_to_lead_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    lead_to_sale_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)


class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data."""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.IntegerField())


class DateRangeSerializer(serializers.Serializer):
    """Serializer for date range queries."""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

