"""
Chat and messaging models.
"""
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """Conversation between a seller and customer."""
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='seller_conversations'
    )
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200, blank=True)
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conversations'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ], default='active')
    
    # Metadata
    source = models.CharField(max_length=50, blank=True)  # facebook, instagram, website
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at']
    
    def __str__(self):
        return f"Conversation with {self.customer_email}"
    
    def get_last_message(self):
        """Get the last message in the conversation."""
        return self.messages.first()
    
    def mark_as_read(self, user):
        """Mark all unread messages as read for a user."""
        self.messages.filter(
            recipient=user,
            is_read=False
        ).update(is_read=True)
    
    def get_unread_count(self, user):
        """Get unread message count for a user."""
        return self.messages.filter(
            recipient=user,
            is_read=False
        ).count()


class Message(models.Model):
    """Individual message in a conversation."""
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='received_messages', null=True, blank=True
    )
    
    # Message content
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('product', 'Product'),
        ('order', 'Order'),
        ('system', 'System'),
    ], default='text')
    
    # Attachments
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    attachment = models.FileField(upload_to='chat/attachments/', blank=True, null=True)
    
    # Product reference (for product messages)
    product = models.ForeignKey(
        'products.Product', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='chat_messages'
    )
    
    # AI
    is_ai_generated = models.BooleanField(default=False)
    ai_suggestion_used = models.BooleanField(default=False)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email}"


class AIConversationContext(models.Model):
    """Store AI conversation context for smart replies."""
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='ai_contexts'
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='ai_contexts'
    )
    context_type = models.CharField(max_length=50, choices=[
        ('product_inquiry', 'Product Inquiry'),
        ('price_question', 'Price Question'),
        ('shipping_question', 'Shipping Question'),
        ('warranty_question', 'Warranty Question'),
        ('purchase_intent', 'Purchase Intent'),
        ('general', 'General'),
    ])
    extracted_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI Conversation Context'
        verbose_name_plural = 'AI Conversation Contexts'
    
    def __str__(self):
        return f"Context for conversation {self.conversation.id}"


class ChatSettings(models.Model):
    """User chat settings."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chat_settings'
    )
    
    # AI Settings
    ai_auto_reply_enabled = models.BooleanField(default=False)
    ai_reply_sensitivity = models.IntegerField(default=50)  # 0-100
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Business hours
    business_hours_enabled = models.BooleanField(default=False)
    business_hours_start = models.TimeField(default='09:00')
    business_hours_end = models.TimeField(default='18:00')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Auto-response
    auto_response_enabled = models.BooleanField(default=False)
    auto_response_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chat Settings'
        verbose_name_plural = 'Chat Settings'
    
    def __str__(self):
        return f"Chat settings for {self.user.email}"


class AISuggestion(models.Model):
    """Store AI reply suggestions."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )
    suggestion_type = models.CharField(max_length=50)
    content = models.TextField()
    was_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI Suggestion'
        verbose_name_plural = 'AI Suggestions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Suggestion for {self.conversation.id}"

