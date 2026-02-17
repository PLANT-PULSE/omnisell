"""
Notification models.
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notification model."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('chat', 'Chat'),
        ('product', 'Product'),
        ('social', 'Social Media'),
        ('system', 'System'),
        ('analytics', 'Analytics'),
        ('marketing', 'Marketing'),
    ], default='system')
    
    # Icon and color (for UI customization)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    
    # Related object reference
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    
    # Action URL
    action_url = models.URLField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='normal')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])


class NotificationPreference(models.Model):
    """User notification preferences."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # In-app notifications
    in_app_enabled = models.BooleanField(default=True)
    
    # Notification types
    order_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    chat_notifications = models.BooleanField(default=True)
    product_notifications = models.BooleanField(default=True)
    social_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    marketing_notifications = models.BooleanField(default=False)
    
    # Email notifications
    email_enabled = models.BooleanField(default=True)
    email_daily_digest = models.BooleanField(default=False)
    email_weekly_digest = models.BooleanField(default=True)
    
    # Push notifications
    push_enabled = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"


class NotificationTemplate(models.Model):
    """Templates for notifications."""
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50, choices=[
        ('order', 'Order'),
        ('payment', 'Payment'),
        ('chat', 'Chat'),
        ('product', 'Product'),
        ('social', 'Social Media'),
        ('system', 'System'),
        ('analytics', 'Analytics'),
        ('marketing', 'Marketing'),
    ])
    
    # Template content
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    
    # Variables that can be used in templates
    available_variables = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.name} ({self.notification_type})"
    
    def render(self, context):
        """Render the template with given context."""
        title = self.title_template
        message = self.message_template
        
        for key, value in context.items():
            title = title.replace(f'{{{{ {key} }}}}', str(value))
            message = message.replace(f'{{{{ {key} }}}}', str(value))
        
        return title, message


class PushDevice(models.Model):
    """Store push notification device tokens."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='push_devices'
    )
    device_token = models.CharField(max_length=255)
    device_type = models.CharField(max_length=20, choices=[
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ])
    device_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Push Device'
        verbose_name_plural = 'Push Devices'
        unique_together = ['user', 'device_token']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type}"

