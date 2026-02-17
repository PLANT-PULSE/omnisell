"""
Social media integration models.
"""
from django.db import models
from django.conf import settings


class SocialAccount(models.Model):
    """Store connected social media accounts."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='social_accounts'
    )
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
    ])
    
    # Platform-specific account info
    platform_user_id = models.CharField(max_length=200)
    platform_username = models.CharField(max_length=100, blank=True)
    platform_display_name = models.CharField(max_length=200, blank=True)
    
    # OAuth tokens
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account info
    profile_picture = models.URLField(blank=True)
    followers_count = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
        unique_together = ['user', 'platform']
    
    def __str__(self):
        return f"{self.user.email} - {self.platform}"
    
    def is_token_expired(self):
        """Check if the access token is expired."""
        if self.token_expires_at:
            from django.utils import timezone
            return timezone.now() >= self.token_expires_at
        return False


class SocialPost(models.Model):
    """Track social media posts."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='social_posts'
    )
    social_account = models.ForeignKey(
        SocialAccount, on_delete=models.CASCADE,
        related_name='posts', null=True, blank=True
    )
    
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
    ])
    
    # Post content
    content = models.TextField()
    hashtags = models.CharField(max_length=500, blank=True)
    media_urls = models.JSONField(default=list, blank=True)
    
    # Related product
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='seller_social_posts'
    )
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('publishing', 'Publishing'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ], default='draft')
    
    # Platform response
    external_post_id = models.CharField(max_length=200, blank=True)
    post_url = models.URLField(blank=True)
    platform_error = models.TextField(blank=True)
    
    # Analytics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    engagements = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Social Post'
        verbose_name_plural = 'Social Posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform} post by {self.user.email}"


class SocialSchedule(models.Model):
    """Schedule for automated posting."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='social_schedules'
    )
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
    ])
    
    # Schedule
    day_of_week = models.JSONField(default=list)  # [0, 1, 2, 3, 4, 5, 6]
    time = models.TimeField()  # Hour and minute
    
    # Content template
    content_template = models.TextField()
    include_product_link = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Social Schedule'
        verbose_name_plural = 'Social Schedules'
    
    def __str__(self):
        return f"Schedule for {self.user.email} - {self.platform}"


class PlatformInsight(models.Model):
    """Platform-specific insights and analytics."""
    social_account = models.ForeignKey(
        SocialAccount, on_delete=models.CASCADE,
        related_name='insights'
    )
    date = models.DateField()
    
    # Metrics
    followers = models.IntegerField(default=0)
    followers_gained = models.IntegerField(default=0)
    followers_lost = models.IntegerField(default=0)
    profile_visits = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    engagement_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    
    # Content performance
    posts_published = models.IntegerField(default=0)
    top_post_impressions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Platform Insight'
        verbose_name_plural = 'Platform Insights'
        unique_together = ['social_account', 'date']
    
    def __str__(self):
        return f"Insights for {self.social_account} on {self.date}"

