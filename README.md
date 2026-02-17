# SellFlow - Django Backend

A complete Django backend for the SellFlow social commerce platform, designed to match the frontend behavior.

## Features

### Core Modules

1. **Accounts** (`accounts/`)
   - User authentication (register, login, logout)
   - JWT token authentication
   - User profiles with seller metrics
   - Onboarding state tracking
   - Theme preferences

2. **Products** (`products/`)
   - Product CRUD operations
   - Image upload and management
   - Categories and tags
   - Stock management
   - AI-powered content generation

3. **Chat** (`chat/`)
   - Customer conversations
   - Message threading
   - AI reply suggestions
   - Product sharing in chat

4. **Analytics** (`analytics/`)
   - Event tracking
   - Platform metrics (Facebook, Instagram, Twitter, WhatsApp)
   - Daily metrics dashboard
   - Conversion funnel analysis
   - Revenue tracking

5. **Social** (`social/`)
   - Social media account connections
   - Post scheduling
   - Cross-platform posting
   - OAuth integrations

6. **Notifications** (`notifications/`)
   - In-app notifications
   - Notification preferences
   - Push notification support
   - Notification templates

7. **AI Services** (`ai/`)
   - Product description generation
   - Hashtag generation
   - Social media post generation
   - Chat reply suggestions

## Requirements

- Python 3.10+
- Django 4.2+
- Django REST Framework

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
OPENAI_API_KEY=your-openai-api-key
```

### 4. Database Setup

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login (returns JWT tokens) |
| POST | `/api/auth/logout/` | Logout |
| POST | `/api/auth/token/refresh/` | Refresh JWT token |
| GET | `/api/auth/profile/` | Get user profile |
| PUT | `/api/auth/profile/` | Update profile |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Create product |
| GET | `/api/products/{id}/` | Get product details |
| PUT | `/api/products/{id}/` | Update product |
| DELETE | `/api/products/{id}/` | Delete product |
| POST | `/api/products/{id}/upload-images/` | Upload images |
| GET | `/api/products/categories/` | List categories |
| POST | `/api/ai/generate/description/` | Generate description |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/conversations/` | List conversations |
| POST | `/api/chat/conversations/` | Create conversation |
| GET | `/api/chat/conversations/{id}/` | Get conversation |
| GET | `/api/chat/conversations/{id}/messages/` | Get messages |
| POST | `/api/chat/conversations/{id}/messages/` | Send message |
| POST | `/api/ai/chat/suggestions/` | Get AI suggestions |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard/` | Dashboard metrics |
| GET | `/api/analytics/platforms/` | Platform metrics |
| GET | `/api/analytics/conversions/` | Conversion summary |
| GET | `/api/analytics/events/` | Event logs |
| POST | `/api/analytics/events/` | Track event |

### Social

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/social/accounts/` | List connected accounts |
| POST | `/api/social/accounts/` | Connect account |
| POST | `/api/social/posts/` | Create post |
| GET | `/api/social/schedules/` | List schedules |
| POST | `/api/social/schedules/` | Schedule post |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | List notifications |
| POST | `/api/notifications/{id}/mark_read/` | Mark as read |
| POST | `/api/notifications/mark_all_read/` | Mark all as read |
| GET | `/api/notifications/count/` | Get count |
| GET | `/api/notifications/preferences/` | Get preferences |
| PUT | `/api/notifications/preferences/` | Update preferences |

## AI Integration

### OpenAI Setup

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key
```

### Features

- **Product Descriptions**: Generate compelling descriptions from product details
- **Hashtags**: Create platform-specific hashtags for better discoverability
- **Social Posts**: Generate platform-optimized posts for Facebook, Instagram, Twitter, WhatsApp
- **Chat Replies**: AI-powered reply suggestions based on conversation context

## Social Media Integration

### Facebook/Instagram

1. Create a Meta Developer account
2. Create an app and get API credentials
3. Add credentials to `.env`:

```env
FACEBOOK_API_KEY=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

### Twitter

1. Create a Twitter Developer account
2. Create an app and get API keys
3. Add to `.env`:

```env
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
```

### WhatsApp

1. Set up WhatsApp Business API
2. Get credentials from Meta
3. Add to `.env`:

```env
WHATSAPP_API_KEY=your-whatsapp-api-key
```

## Testing

```bash
python manage.py test
```

## Project Structure

```
sellflow/
├── manage.py
├── requirements.txt
├── .env.example
├── sellflow/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── products/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── chat/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── analytics/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── social/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── notifications/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
└── ai/
    ├── __init__.py
    ├── apps.py
    ├── services.py
    ├── views.py
    └── urls.py
```

## License

MIT License

