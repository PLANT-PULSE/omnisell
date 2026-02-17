"""
AI Services for content generation.
"""
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIContentGenerator:
    """Service for generating AI content for products and social media."""
    
    def __init__(self):
        self.client = None
        self.last_prompt = ""
        
        # Initialize OpenAI client if API key is available
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
    
    def _call_openai(self, prompt, max_tokens=500):
        """Call OpenAI API with the given prompt."""
        if not self.client:
            # Return mock content for development
            return self._get_mock_content(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional marketing copywriter for e-commerce products."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_mock_content(prompt)
    
    def _get_mock_content(self, prompt):
        """Return mock content when API is not available."""
        if "description" in prompt.lower():
            return "Experience premium quality with our latest product. Designed for durability and style, this item offers exceptional value. Perfect for everyday use with features that enhance your lifestyle."
        elif "hashtag" in prompt.lower():
            return "#NewArrival #MustHave #Trending #ShopNow #LimitedEdition"
        elif "instagram" in prompt.lower():
            return "New drop alert! 🚀 Don't miss out on our latest collection. Link in bio! 👆 #NewArrival #ShopNow"
        elif "facebook" in prompt.lower():
            return "We're excited to introduce our latest product! Crafted with care and designed to impress. Shop now and experience the difference."
        elif "twitter" in prompt.lower():
            return "Just launched! Check out our newest product. Link below 👇 #NewProduct #Shopping"
        else:
            return "Thank you for your message! How can we help you today?"
    
    def generate_product_description(self, product, tone='professional'):
        """Generate a product description using AI."""
        prompt = f"""
        Write a compelling product description for an e-commerce product.
        
        Product Name: {product.name}
        Price: ${product.price}
        Category: {product.category.name if product.category else 'General'}
        
        Write a description that is:
        - {tone} in tone
        - Persuasive and engaging
        - Around 150-200 words
        - Highlighting key features and benefits
        - Including any relevant details from: {product.description if product.description else 'N/A'}
        
        Focus on the value proposition and make it compelling for potential buyers.
        """
        
        self.last_prompt = prompt
        return self._call_openai(prompt, max_tokens=300)
    
    def generate_hashtags(self, product, platform=None):
        """Generate relevant hashtags for a product."""
        prompt = f"""
        Generate relevant hashtags for the following product:
        
        Product: {product.name}
        Category: {product.category.name if product.category else 'General'}
        Existing tags: {product.tags}
        
        Generate 10-15 relevant hashtags that would help with discoverability.
        {"Focus on Instagram-style hashtags." if platform == 'instagram' else ""}
        {"Focus on Twitter-style hashtags." if platform == 'twitter' else ""}
        
        Return only the hashtags separated by spaces, no explanation.
        """
        
        self.last_prompt = prompt
        hashtags = self._call_openai(prompt, max_tokens=100)
        # Clean up hashtags
        hashtags = ' '.join([h.strip() for h in hashtags.split() if h.strip().startswith('#')])
        return hashtags or "#Product #Shopping #New"
    
    def generate_social_post(self, product, platform, tone='engaging'):
        """Generate a social media post for a specific platform."""
        platform_context = {
            'facebook': {
                'length': '150-200 characters',
                'style': 'professional but friendly',
                'include': 'emoji, call-to-action'
            },
            'instagram': {
                'length': '150-200 characters',
                'style': 'casual, visual-focused',
                'include': 'multiple emojis, call-to-action in bio'
            },
            'twitter': {
                'length': '280 characters max',
                'style': 'concise, punchy',
                'include': 'relevant hashtags (2-3)'
            },
            'whatsapp': {
                'length': '200-300 characters',
                'style': 'direct and personal',
                'include': 'emoji, clear call-to-action'
            }
        }
        
        context = platform_context.get(platform, {})
        
        prompt = f"""
        Write a social media post for {platform}.
        
        Product: {product.name}
        Price: ${product.price}
        Description: {product.description[:200] if product.description else 'Quality product'}
        
        Requirements:
        - Length: {context.get('length', '150-200 characters')}
        - Style: {context.get('style', 'engaging')}
        - Include: {', '.join(context.get('include', [])) or 'engaging content'}
        - Add 3-5 relevant hashtags at the end
        - Make it compelling and drive sales
        """
        
        self.last_prompt = prompt
        return self._call_openai(prompt, max_tokens=200)
    
    def generate_chat_reply_suggestion(self, conversation, context_type):
        """Generate AI reply suggestions for chat conversations."""
        last_message = conversation.messages.last()
        customer_name = conversation.customer_name or 'Customer'
        
        prompts = {
            'product_inquiry': f"""
            The customer {customer_name} is asking about a product.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a helpful, professional reply that:
            - Addresses their question about the product
            - Provides helpful information
            - Maintains a friendly tone
            - Is concise (1-2 sentences)
            """,
            'price_question': f"""
            {customer_name} is asking about pricing.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a reply that:
            - Clearly addresses the pricing question
            - Mentions any relevant discounts or promotions
            - Encourages the purchase
            """,
            'warranty_question': f"""
            {customer_name} is asking about warranty.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a reply that:
            - Clearly explains the warranty terms
            - Provides confidence in the purchase
            """,
            'shipping_question': f"""
            {customer_name} is asking about shipping.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a reply that:
            - Provides shipping information
            - Mentions delivery times if available
            """,
            'purchase_intent': f"""
            {customer_name} is ready to purchase.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a reply that:
            - Acknowledges their decision
            - Makes the purchase process easy
            - Offers assistance if needed
            """
        }
        
        prompt = prompts.get(context_type, prompts['general'])
        
        if context_type not in prompts:
            prompt = f"""
            {customer_name} sent a message.
            Last message: {last_message.content if last_message else 'N/A'}
            
            Write a helpful, professional reply.
            """
        
        self.last_prompt = prompt
        return self._call_openai(prompt, max_tokens=150)


class AIChatAssistant:
    """AI assistant for chat conversations."""
    
    def __init__(self):
        self.generator = AIContentGenerator()
    
    def analyze_conversation(self, conversation):
        """Analyze a conversation to determine context."""
        messages = conversation.messages.all()
        
        if not messages:
            return {'type': 'general', 'confidence': 0}
        
        last_message = messages.last()
        content = last_message.content.lower()
        
        # Simple keyword-based analysis
        context_types = {
            'price_question': ['price', 'cost', 'how much', 'expensive', 'cheap', 'discount'],
            'warranty_question': ['warranty', 'guarantee', 'return', 'refund'],
            'shipping_question': ['shipping', 'delivery', 'ship', 'arrive', 'time'],
            'purchase_intent': ['buy', 'purchase', 'order', 'take them', 'proceed'],
            'product_inquiry': ['does it', 'is it', 'can it', 'feature', 'specification'],
        }
        
        for context_type, keywords in context_types.items():
            for keyword in keywords:
                if keyword in content:
                    return {'type': context_type, 'confidence': 0.8}
        
        return {'type': 'general', 'confidence': 0.5}
    
    def generate_suggestions(self, conversation, types=None):
        """Generate reply suggestions for a conversation."""
        if types is None:
            types = ['general']
        
        context = self.analyze_conversation(conversation)
        suggestions = []
        
        for suggestion_type in types:
            reply = self.generator.generate_chat_reply_suggestion(
                conversation, suggestion_type
            )
            suggestions.append({
                'type': suggestion_type,
                'content': reply,
                'context': context
            })
        
        return suggestions
    
    def auto_reply(self, conversation):
        """Generate an automatic reply for a conversation."""
        context = self.analyze_conversation(conversation)
        
        reply = self.generator.generate_chat_reply_suggestion(
            conversation, context['type']
        )
        
        return {
            'reply': reply,
            'context': context,
            'confidence': context['confidence']
        }

