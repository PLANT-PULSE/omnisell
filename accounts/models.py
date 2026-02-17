"""
User and Profile models for SellFlow.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for SellFlow.
    Uses email as the primary identifier instead of username.
    """
    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Social media connections
    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    instagram_id = models.CharField(max_length=100, blank=True, null=True)
    twitter_id = models.CharField(max_length=100, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    
    # AI settings
    ai_description_enabled = models.BooleanField(default=True)
    ai_hashtags_enabled = models.BooleanField(default=True)
    ai_replies_enabled = models.BooleanField(default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Extended profile information for users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True)
    business_type = models.CharField(max_length=50, choices=[
        ('individual', 'Individual Seller'),
        ('business', 'Business'),
        ('retailer', 'Retailer'),
        ('wholesaler', 'Wholesaler'),
    ], default='individual')
    
    # Location
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Seller stats
    total_products = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.IntegerField(default=0)
    positive_feedback = models.IntegerField(default=0)
    
    # Currency preference
    currency = models.CharField(max_length=3, default='USD')
    
    # Theme preference
    dark_mode = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def update_stats(self):
        """Update seller statistics from related products and orders."""
        from products.models import Product
        from orders.models import Order
        
        products = Product.objects.filter(seller=self.user)
        self.total_products = products.count()
        
        orders = Order.objects.filter(seller=self.user, status='completed')
        self.total_sales = orders.aggregate(total=models.Sum('total_amount'))['total'] or 0
        
        self.save()


class ConnectedPlatform(models.Model):
    """
    Social media platforms connected by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connected_platforms')
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
    ])
    platform_user_id = models.CharField(max_length=100)
    platform_username = models.CharField(max_length=100, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Connected Platform'
        verbose_name_plural = 'Connected Platforms'
        unique_together = ['user', 'platform']
    
    def __str__(self):
        return f"{self.user.email} - {self.platform}"
    
    def is_token_expired(self):
        """Check if the access token is expired."""
        if self.token_expires_at:
            return timezone.now() >= self.token_expires_at
        return False


class UserActivity(models.Model):
    """
    Track user activities for activity feed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('order_received', 'New order received'),
        ('post_published', 'Post published'),
        ('product_added', 'Product added'),
        ('product_sold', 'Product sold'),
        ('payment_received', 'Payment received'),
        ('review_received', 'Review received'),
        ('platform_connected', 'Platform connected'),
        ('performance_increase', 'Performance increase'),
    ])
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"

