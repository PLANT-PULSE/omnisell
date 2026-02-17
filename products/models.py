"""
Product models for SellFlow.
"""
from django.db import models
from django.conf import settings


class Category(models.Model):
    """Product category model."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children'
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Main product model."""
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Inventory
    sku = models.CharField(max_length=100, blank=True)
    stock_quantity = models.IntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    
    # Organization
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products'
    )
    tags = models.CharField(max_length=500, blank=True)  # Comma-separated
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ], default='draft')
    
    # AI Generated Content
    ai_description = models.TextField(blank=True)
    ai_hashtags = models.CharField(max_length=500, blank=True)
    ai_content_generated = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_main_image(self):
        """Get the main product image."""
        return self.images.first()
    
    def get_hashtags_list(self):
        """Return hashtags as a list."""
        if self.ai_hashtags:
            return [h.strip() for h in self.ai_hashtags.split(',') if h.strip()]
        return []
    
    def update_analytics(self, event_type):
        """Update product analytics counters."""
        if event_type == 'view':
            self.view_count += 1
        elif event_type == 'click':
            self.click_count += 1
        elif event_type == 'share':
            self.share_count += 1
        self.save(update_fields=[f'{event_type}_count', 'updated_at'])


class ProductImage(models.Model):
    """Product images."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Set as primary if it's the first image."""
        if not self.pk and not self.is_primary:
            if not ProductImage.objects.filter(product=self.product).exists():
                self.is_primary = True
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    """Product videos."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='videos'
    )
    video = models.FileField(upload_to='products/videos/', blank=True)
    video_url = models.URLField(blank=True)  # For hosted videos
    thumbnail = models.ImageField(upload_to='products/videos/thumbnails/', blank=True)
    title = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField(default=0)  # Duration in seconds
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Video'
        verbose_name_plural = 'Product Videos'
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Video for {self.product.name}"


class AIGeneratedContent(models.Model):
    """Track AI-generated content for products."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='ai_contents'
    )
    content_type = models.CharField(max_length=50, choices=[
        ('description', 'Product Description'),
        ('hashtags', 'Hashtags'),
        ('social_post_facebook', 'Facebook Post'),
        ('social_post_instagram', 'Instagram Post'),
        ('social_post_twitter', 'Twitter Post'),
        ('social_post_whatsapp', 'WhatsApp Message'),
    ])
    platform = models.CharField(max_length=20, blank=True)
    content = models.TextField()
    prompt = models.TextField(blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI Generated Content'
        verbose_name_plural = 'AI Generated Contents'
    
    def __str__(self):
        return f"AI {self.content_type} for {self.product.name}"


class SocialPost(models.Model):
    """Social media posts for products (kept in products app for simplicity)."""
    # Seller/User who created the post
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='product_social_posts'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_social_posts'
    )
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
    ])
    
    # Post content
    caption = models.TextField()
    hashtags = models.CharField(max_length=500, blank=True)
    
    # Media
    image = models.ImageField(upload_to='social/', blank=True, null=True)
    video = models.FileField(upload_to='social/videos/', blank=True, null=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ], default='draft')
    
    # External post ID
    external_post_id = models.CharField(max_length=200, blank=True)
    post_url = models.URLField(blank=True)
    
    # Analytics
    clicks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    engagements = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Social Post'
        verbose_name_plural = 'Social Posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.platform} post for {self.product.name}"


class ProductView(models.Model):
    """Track product views for analytics."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='views'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='product_views'
    )
    session_id = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, blank=True)  # facebook, instagram, etc.
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product View'
        verbose_name_plural = 'Product Views'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"View: {self.product.name}"

