# OmniSell API Documentation

This document provides comprehensive API documentation for the OmniSell eCommerce/social-commerce platform backend built with Django REST Framework.

---

## Table of Contents
1. [Base URL & Authentication](#base-url--authentication)
2. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication)
   - [Products](#products)
   - [Orders & Cart](#orders--cart)
   - [Chat](#chat)
   - [Notifications](#notifications)
   - [Social Media](#social-media)
   - [Analytics](#analytics)
   - [AI Services](#ai-services)
3. [Frontend Integration Guide](#frontend-integration-guide)
4. [WebSocket/Real-time Features](#websocketreal-time-features)
5. [Payment Integration](#payment-integration)
6. [Scalability & Security](#scalability--security)

---

## Base URL & Authentication

### Base URL
```
Production: https://api.omnisell.com/api/
Development: http://localhost:8000/api/
```

### Authentication
The API uses **JWT (JSON Web Tokens)** for authentication.

**Token Endpoints:**
- `POST /api/auth/login/` - Obtain token pair (access + refresh)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token validity

**Authentication Header:**
```http
Authorization: Bearer <your_access_token>
```

---

## API Endpoints

### 1. Authentication

#### Register User
```
POST /api/auth/register/
Content-Type: application/json

Request:
{
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+233501234567"
}

Response (201 Created):
{
    "message": "User registered successfully.",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": false,
        "onboarding_completed": false
    }
}
```

#### Login
```
POST /api/auth/login/
Content-Type: application/json

Request:
{
    "email": "user@example.com",
    "password": "securepassword123"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1Q...",
    "refresh": "eyJ0eXAiOiJKV1Q...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John"
    }
}
```

#### Get Current User
```
GET /api/auth/user/me/
Headers: Authorization: Bearer <token>

Response:
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+233501234567",
    "is_verified": false,
    "onboarding_completed": false,
    "ai_description_enabled": true,
    "ai_hashtags_enabled": true,
    "ai_replies_enabled": true
}
```

#### Update Profile
```
PUT /api/auth/profile/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Seller of premium electronics",
    "company_name": "TechGear Hub",
    "business_type": "business",
    "country": "Ghana",
    "city": "Accra",
    "currency": "GHS",
    "dark_mode": false
}
```

---

### 2. Products

#### List Seller's Products
```
GET /api/products/
Headers: Authorization: Bearer <token>

Query Parameters:
- status: filter by status (draft, active, inactive, archived)
- category: filter by category ID
- search: search by product name

Response:
[
    {
        "id": 1,
        "name": "Wireless Headphones",
        "description": "Premium noise-cancelling headphones",
        "price": "89.99",
        "stock_quantity": 50,
        "status": "active",
        "view_count": 120,
        "share_count": 15,
        "images": [...],
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

#### Create Product
```
POST /api/products/
Headers: Authorization: Bearer <token>
Content-Type: application/json
Content-Type: multipart/form-data

Request:
{
    "name": "Wireless Headphones",
    "description": "Premium noise-cancelling headphones",
    "price": "89.99",
    "compare_at_price": "129.99",
    "stock_quantity": 50,
    "sku": "WH-001",
    "category": 1,
    "tags": "audio,wireless,premium",
    "status": "active"
}

Response (201 Created):
{
    "id": 1,
    "name": "Wireless Headphones",
    "price": "89.99",
    "status": "active",
    ...
}
```

#### Upload Product Images
```
POST /api/products/{id}/upload_images/
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
images: [file1.jpg, file2.jpg]
```

#### Generate AI Content
```
POST /api/products/{id}/generate_ai_content/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "content_type": "description",  // or "hashtags", "social_post"
    "platform": "instagram"  // required for social_post
}

Response:
{
    "message": "Description generated successfully.",
    "description": "Experience unparalleled audio quality with our premium wireless headphones..."
}
```

#### Publish to Social Media
```
POST /api/products/{id}/create_social_post/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "platform": "facebook",
    "content": "Check out our new product!",
    "hashtags": "#Wireless #Tech",
    "is_scheduled": false
}
```

#### Public Product Listing (For Buyers)
```
GET /api/products/public/list/

Query Parameters:
- category: filter by category
- search: search products

Response:
[
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": "89.99",
        "images": [...],
        "seller": {...}
    }
]
```

#### Public Product Detail
```
GET /api/products/public/{id}/
Response: Full product details with seller info
```

#### Public Vendor Products
```
GET /api/products/public/vendor/{vendor_id}/
Response: Vendor info + their products
```

---

### 3. Orders & Cart

#### Get Cart
```
GET /api/orders/cart/
Headers: Authorization: Bearer <token>

Response:
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "Wireless Headphones",
            "price": "89.99",
            "quantity": 2,
            "total": "179.98"
        }
    ],
    "total": "179.98",
    "item_count": 2
}
```

#### Add to Cart
```
POST /api/orders/cart/add_item/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "product_id": 1,
    "quantity": 2
}

Response:
{
    "id": 1,
    "items": [...],
    "total": "179.98",
    "item_count": 2
}
```

#### Update Cart Item
```
PUT /api/orders/cart/update_item/{item_id}/
Headers: Authorization: Bearer <token>

Request:
{
    "quantity": 3
}
```

#### Remove Cart Item
```
DELETE /api/orders/cart/remove_item/{item_id}/
Headers: Authorization: Bearer <token>
```

#### Clear Cart
```
DELETE /api/orders/cart/clear/
Headers: Authorization: Bearer <token>
```

#### Checkout
```
POST /api/orders/checkout/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "full_name": "John Doe",
    "phone": "+233501234567",
    "address_line1": "123 Main Street",
    "address_line2": "Apt 4B",
    "city": "Accra",
    "state": "Greater Accra",
    "postal_code": "00233",
    "country": "Ghana",
    "delivery_instructions": "Leave at door",
    "payment_method": "card",
    "buyer_note": "Please gift wrap",
    "source": "instagram"  // track order source
}

Response (201 Created):
{
    "id": 1,
    "order_id": "SFABC12345",
    "status": "pending",
    "total_amount": "197.98",
    "items": [...],
    "shipping_address": {...},
    "payments": [...]
}
```

#### List My Orders
```
GET /api/orders/orders/
Headers: Authorization: Bearer <token>

Query Parameters:
- status: filter by status (pending, confirmed, shipped, delivered, cancelled)
```

#### Order Detail
```
GET /api/orders/orders/{id}/
Headers: Authorization: Bearer <token>
```

#### Seller Orders
```
GET /api/orders/orders/seller_orders/
Headers: Authorization: Bearer <token>
```

#### Process Payment
```
POST /api/orders/payments/{id}/process/
Headers: Authorization: Bearer <token>

Response:
{
    "status": "completed",
    "transaction_id": "TXN20240115103000"
}
```

---

### 4. Chat

#### List Conversations
```
GET /api/chat/conversations/
Headers: Authorization: Bearer <token>

Query Parameters:
- status: filter by status
- source: filter by source (facebook, instagram, website)
- search: search by customer name/email
```

#### Create Conversation
```
POST /api/chat/conversations/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "customer_email": "buyer@example.com",
    "customer_name": "Jane Doe",
    "product": 1,
    "source": "instagram"
}
```

#### Send Message
```
POST /api/chat/messages/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "conversation": 1,
    "content": "Hi, I'm interested in this product!",
    "message_type": "text"
}
```

#### Get AI Suggestions
```
GET /api/chat/conversations/{id}/ai_suggestions/
Headers: Authorization: Bearer <token>
```

---

### 5. Notifications

#### List Notifications
```
GET /api/notifications/
Headers: Authorization: Bearer <token>

Query Parameters:
- is_read: filter by read status
- type: filter by type (order, payment, chat, product, social, system)
```

#### Mark as Read
```
POST /api/notifications/{id}/mark_as_read/
Headers: Authorization: Bearer <token>
```

#### Mark All as Read
```
POST /api/notifications/mark_all_read/
Headers: Authorization: Bearer <token>
```

#### Update Preferences
```
PUT /api/notifications/preferences/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "in_app_enabled": true,
    "order_notifications": true,
    "chat_notifications": true,
    "email_enabled": true,
    "email_daily_digest": false
}
```

---

### 6. Social Media

#### List Connected Accounts
```
GET /api/social/accounts/
Headers: Authorization: Bearer <token>
```

#### Connect Platform
```
POST /api/social/accounts/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "platform": "facebook",
    "platform_user_id": "123456789",
    "platform_username": "mybusiness",
    "access_token": "..."
}
```

#### Get Platform Insights
```
GET /api/social/accounts/{id}/insights/
Headers: Authorization: Bearer <token>

Query Parameters:
- days: number of days (default: 7)
```

#### Disconnect Platform
```
POST /api/social/accounts/disconnect/
Headers: Authorization: Bearer <token>

Request:
{
    "platform": "facebook"
}
```

---

### 7. Analytics

#### Dashboard Stats
```
GET /api/analytics/dashboard/
Headers: Authorization: Bearer <token>
```

#### Sales Analytics
```
GET /api/analytics/sales/
Headers: Authorization: Bearer <token>

Query Parameters:
- period: daily, weekly, monthly
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD
```

#### Product Performance
```
GET /api/analytics/products/
Headers: Authorization: Bearer <token>
```

---

### 8. AI Services

#### Search Products (AI-Powered)
```
GET /api/ai/search/
Headers: Authorization: Bearer <token>

Query Parameters:
- q: search query (natural language)
- category: optional category filter
```

#### Generate Product Description
```
POST /api/ai/generate/description/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "product_id": 1,
    "style": "professional",  // professional, casual, persuasive
    "length": "medium"  // short, medium, long
}
```

#### Generate Hashtags
```
POST /api/ai/generate/hashtags/
Headers: Authorization: Bearer <token>
Content-Type: application/json

Request:
{
    "product_id": 1,
    "platform": "instagram",
    "count": 10
}
```

---

## Frontend Integration Guide

### Authentication Flow

1. **Registration:**
   ```javascript
   // Register new user
   const response = await fetch('/api/auth/register/', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(userData)
   });
   const data = await response.json();
   // Store tokens
   localStorage.setItem('access', data.access);
   localStorage.setItem('refresh', data.refresh);
   ```

2. **Login:**
   ```javascript
   // Login
   const response = await fetch('/api/auth/login/', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ email, password })
   });
   const { access, refresh, user } = await response.json();
   ```

3. **Token Refresh:**
   ```javascript
   // Auto-refresh token before expiry
   async function refreshToken() {
       const refresh = localStorage.getItem('refresh');
       const response = await fetch('/api/auth/token/refresh/', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ refresh })
       });
       const data = await response.json();
       localStorage.setItem('access', data.access);
   }
   ```

### Product Management Flow

1. **Create Product with Images:**
   ```javascript
   // Create product first
   const product = await createProduct(productData);
   
   // Upload images
   const formData = new FormData();
   images.forEach(img => formData.append('images', img));
   await uploadImages(product.id, formData);
   
   // Generate AI content
   const description = await generateAIContent(product.id, 'description');
   const hashtags = await generateAIContent(product.id, 'hashtags');
   ```

### Cart & Checkout Flow

1. **Add to Cart:**
   ```javascript
   await fetch('/api/orders/cart/add_item/', {
       method: 'POST',
       headers: { 
           'Authorization': `Bearer ${token}`,
           'Content-Type': 'application/json'
       },
       body: JSON.stringify({ product_id, quantity })
   });
   ```

2. **Checkout:**
   ```javascript
   const order = await fetch('/api/orders/checkout/', {
       method: 'POST',
       headers: { 
           'Authorization': `Bearer ${token}`,
           'Content-Type': 'application/json'
       },
       body: JSON.stringify(checkoutData)
   });
   
   // Process payment
   await processPayment(order.payments[0].id);
   ```

### Social Sharing Flow

1. **Generate Share Link:**
   ```javascript
   // Product detail page should have share buttons
   const shareUrl = `${window.location.origin}/product/${product.id}/`;
   const shareText = `Check out this product: ${product.name} - ${product.price}`;
   ```

---

## WebSocket/Real-time Features

For real-time chat, use WebSocket connections:

```
WebSocket Endpoint: wss://api.omnisell.com/ws/chat/

Authentication: Pass token in query string
wss://api.omnisell.com/ws/chat/?token=<access_token>
```

**Message Format:**
```json
{
    "type": "chat_message",
    "conversation_id": 1,
    "content": "Hello!",
    "sender_id": 1
}
```

---

## Payment Integration

### Currently Supported Methods

1. **Card Payments** (Stripe/Flutterwave integration ready)
2. **Mobile Money** (MTN, Vodafone, AirtelTigo)
3. **Bank Transfer**
4. **PayPal**

### Payment Flow

1. Create order → Get payment record
2. Redirect to payment provider OR collect card details
3. Provider processes payment
4. Webhook updates payment status → Order confirmed

### Webhook Endpoint

```
POST /api/webhooks/payment/
(Configure in payment provider dashboard)
```

---

## Scalability & Security

### Recommendations

1. **Caching:**
   - Use Redis for session storage and API caching
   - Cache product listings and categories

2. **CDN:**
   - Serve static/media files via CloudFront or similar
   - Configure proper CORS headers

3. **Database:**
   - Use PostgreSQL for production
   - Implement read replicas for heavy read operations
   - Use database connection pooling (PgBouncer)

4. **Security:**
   - Enable HTTPS in production
   - Implement rate limiting
   - Use Django's security middleware
   - Regular security audits

5. **File Storage:**
   - Use S3 or similar for media files
   - Configure proper bucket policies

---

## Error Responses

All errors follow this format:

```json
{
    "error": "Error message",
    "details": {}  // Optional detailed errors
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

---

## Support

For API issues or questions:
- Email: api-support@omnisell.com
- Documentation: https://docs.omnisell.com
