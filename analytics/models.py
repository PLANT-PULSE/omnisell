"""
Analytics models for tracking performance metrics.
"""
from django.db import models
from django.conf import settings


class DailyAnalytics(models.Model):
    """Daily aggregated analytics data."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='daily_analytics'
    )
    date = models.DateField()
    
    # Revenue
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    orders_count = models.IntegerField(default=0)
    average_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    
    # Traffic
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    sessions = models.IntegerField(default=0)
    
    # Engagement
    clicks = models.IntegerField(default=0)
    leads = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    
    # Social Media
    social_clicks = models.IntegerField(default=0)
    social_impressions = models.IntegerField(default=0)
    social_engagements = models.IntegerField(default=0)
    
    # Platform breakdown (JSON for flexibility)
    platform_stats = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Daily Analytics'
        verbose_name_plural = 'Daily Analytics'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.user.email} on {self.date}"


class PlatformAnalytics(models.Model):
    """Analytics broken down by platform."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='platform_analytics'
    )
    date = models.DateField()
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
        ('website', 'Website'),
    ])
    
    # Metrics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    engagements = models.IntegerField(default=0)
    leads = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Engagement rates
    click_through_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    engagement_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    
    class Meta:
        verbose_name = 'Platform Analytics'
        verbose_name_plural = 'Platform Analytics'
        unique_together = ['user', 'date', 'platform']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.platform} analytics for {self.user.email} on {self.date}"


class ProductAnalytics(models.Model):
    """Per-product analytics."""
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()
    
    # Metrics
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    leads = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Sources
    views_by_source = models.JSONField(default=dict, blank=True)
    clicks_by_source = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Product Analytics'
        verbose_name_plural = 'Product Analytics'
        unique_together = ['product', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.product.name} on {self.date}"


class ConversionFunnel(models.Model):
    """Track conversion funnel metrics."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='conversion_funnels'
    )
    date = models.DateField()
    
    # Funnel stages
    impressions = models.IntegerField(default=0)
    visits = models.IntegerField(default=0)
    product_views = models.IntegerField(default=0)
    add_to_carts = models.IntegerField(default=0)
    checkouts = models.IntegerField(default=0)
    purchases = models.IntegerField(default=0)
    
    # Conversion rates
    visit_to_product_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    product_to_cart_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    cart_to_checkout_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    checkout_to_purchase_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    overall_conversion_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    
    class Meta:
        verbose_name = 'Conversion Funnel'
        verbose_name_plural = 'Conversion Funnels'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Conversion funnel for {self.user.email} on {self.date}"
    
    def calculate_rates(self):
        """Calculate conversion rates."""
        if self.visits > 0:
            self.visit_to_product_rate = (self.product_views / self.visits) * 100
        if self.product_views > 0:
            self.product_to_cart_rate = (self.add_to_carts / self.product_views) * 100
        if self.add_to_carts > 0:
            self.cart_to_checkout_rate = (self.checkouts / self.add_to_carts) * 100
        if self.checkouts > 0:
            self.checkout_to_purchase_rate = (self.purchases / self.checkouts) * 100
        if self.visits > 0:
            self.overall_conversion_rate = (self.purchases / self.visits) * 100


class TopProduct(models.Model):
    """Track top performing products."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='top_products'
    )
    date = models.DateField()
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='top_product_records'
    )
    metric_type = models.CharField(max_length=20, choices=[
        ('views', 'Views'),
        ('clicks', 'Clicks'),
        ('leads', 'Leads'),
        ('conversions', 'Conversions'),
        ('revenue', 'Revenue'),
    ])
    value = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Top Product'
        verbose_name_plural = 'Top Products'
        unique_together = ['user', 'date', 'metric_type', 'product']
        ordering = ['date', 'metric_type', '-value']
    
    def __str__(self):
        return f"Top {self.metric_type}: {self.product.name} on {self.date}"


class AnalyticsEvent(models.Model):
    """Individual analytics events for detailed tracking."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='analytics_events'
    )
    session_id = models.CharField(max_length=100, blank=True)
    
    event_type = models.CharField(max_length=50, choices=[
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('product_click', 'Product Click'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('checkout_started', 'Checkout Started'),
        ('checkout_completed', 'Checkout Completed'),
        ('social_share', 'Social Share'),
        ('social_click', 'Social Click'),
        ('search', 'Search'),
    ])
    
    # Event data
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        null=True, blank=True, related_name='events'
    )
    platform = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=50, blank=True)
    medium = models.CharField(max_length=50, blank=True)
    campaign = models.CharField(max_length=100, blank=True)
    
    # Location data
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Device data
    device_type = models.CharField(max_length=20, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # Referrer
    referrer = models.URLField(blank=True)
    
    # IP and user agent
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Analytics Event'
        verbose_name_plural = 'Analytics Events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'event_type', '-timestamp']),
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"

