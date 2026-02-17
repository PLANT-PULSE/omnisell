"""
Views for analytics app.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from .models import (
    DailyAnalytics, PlatformAnalytics, ProductAnalytics,
    ConversionFunnel, TopProduct, AnalyticsEvent
)
from .serializers import (
    DailyAnalyticsSerializer, PlatformAnalyticsSerializer,
    ProductAnalyticsSerializer, ConversionFunnelSerializer,
    TopProductSerializer, AnalyticsEventSerializer,
    DashboardStatsSerializer, PerformanceOverviewSerializer,
    PlatformEngagementSerializer, ConversionSummarySerializer,
    ChartDataSerializer
)


class AnalyticsViewSet(viewsets.GenericViewSet):
    """Main analytics viewset."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DailyAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics."""
        user = request.user
        today = timezone.now().date()
        
        # Get today's analytics
        today_analytics = DailyAnalytics.objects.filter(
            user=user, date=today
        ).first()
        
        # Get product count
        from products.models import Product
        total_products = Product.objects.filter(seller=user).count()
        
        # Get total clicks from all products
        from products.models import Product
        total_clicks = Product.objects.filter(
            seller=user
        ).aggregate(total=Sum('click_count'))['total'] or 0
        
        # Get leads count (approximation from messages)
        from chat.models import Conversation
        total_leads = Conversation.objects.filter(
            seller=user, status='active'
        ).count()
        
        stats = {
            'today_revenue': float(today_analytics.revenue) if today_analytics else 0,
            'total_products': total_products,
            'total_clicks': total_clicks,
            'total_leads': total_leads,
            'recent_activity': self.get_recent_activity(user)
        }
        
        return Response(stats)
    
    def get_recent_activity(self, user):
        """Get recent user activity."""
        from accounts.models import UserActivity
        activities = UserActivity.objects.filter(user=user)[:5]
        
        return [{
            'type': a.activity_type,
            'title': a.title,
            'description': a.description,
            'time': a.created_at.isoformat()
        } for a in activities]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get performance overview."""
        user = request.user
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = self.get_queryset().filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Aggregate data
        total_revenue = analytics.aggregate(Sum('revenue'))['revenue__sum'] or 0
        total_clicks = analytics.aggregate(Sum('clicks'))['clicks__sum'] or 0
        total_leads = analytics.aggregate(Sum('leads'))['leads__sum'] or 0
        
        # Build chart data
        labels = [a.date.strftime('%b %d') for a in analytics]
        revenue_data = [float(a.revenue) for a in analytics]
        clicks_data = [a.clicks for a in analytics]
        leads_data = [a.leads for a in analytics]
        
        return Response({
            'period': f'Last {days} days',
            'labels': labels,
            'revenue_data': revenue_data,
            'clicks_data': clicks_data,
            'leads_data': leads_data,
            'total_revenue': float(total_revenue),
            'total_clicks': total_clicks,
            'total_leads': total_leads
        })
    
    @action(detail=False, methods=['get'])
    def platform_engagement(self, request):
        """Get platform engagement data."""
        user = request.user
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        platform_data = PlatformAnalytics.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('platform').annotate(
            total_clicks=Sum('clicks'),
            total_impressions=Sum('impressions'),
            total_engagements=Sum('engagements')
        )
        
        # Compare with previous period
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date - timedelta(days=1)
        
        prev_data = PlatformAnalytics.objects.filter(
            user=user,
            date__range=[prev_start, prev_end]
        ).values('platform').annotate(
            total_clicks=Sum('clicks')
        )
        
        prev_clicks_by_platform = {p['platform']: p['total_clicks'] for p in prev_data}
        
        result = []
        platforms = ['facebook', 'instagram', 'twitter', 'whatsapp']
        
        for platform in platforms:
            data = next((p for p in platform_data if p['platform'] == platform), None)
            if data:
                prev_clicks = prev_clicks_by_platform.get(platform, 0)
                current_clicks = data['total_clicks']
                
                if prev_clicks > 0:
                    change = ((current_clicks - prev_clicks) / prev_clicks) * 100
                else:
                    change = 0
                
                result.append({
                    'platform': platform,
                    'clicks': current_clicks,
                    'impressions': data['total_impressions'],
                    'engagements': data['total_engagements'],
                    'change_percent': round(change, 2)
                })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def conversion_summary(self, request):
        """Get conversion summary."""
        user = request.user
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = self.get_queryset().filter(
            date__range=[start_date, end_date]
        )
        
        total_clicks = analytics.aggregate(Sum('clicks'))['clicks__sum'] or 0
        total_leads = analytics.aggregate(Sum('leads'))['leads__sum'] or 0
        total_conversions = analytics.aggregate(Sum('conversions'))['conversions__sum'] or 0
        total_revenue = analytics.aggregate(Sum('revenue'))['revenue__sum'] or 0
        
        # Calculate rates
        click_to_lead_rate = (total_leads / total_clicks * 100) if total_clicks > 0 else 0
        lead_to_sale_rate = (total_conversions / total_leads * 100) if total_leads > 0 else 0
        aov = (total_revenue / total_conversions) if total_conversions > 0 else 0
        
        return Response({
            'click_to_lead_rate': round(click_to_lead_rate, 2),
            'lead_to_sale_rate': round(lead_to_sale_rate, 2),
            'average_order_value': round(float(aov), 2)
        })
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily analytics."""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        analytics = self.get_queryset().filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        serializer = DailyAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        """Get analytics by platform."""
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        platform_analytics = PlatformAnalytics.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        serializer = PlatformAnalyticsSerializer(platform_analytics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Get top performing products."""
        metric = request.query_params.get('metric', 'clicks')
        limit = int(request.query_params.get('limit', 5))
        
        from products.models import Product
        products = Product.objects.filter(
            seller=request.user
        ).order_by(f'-{metric}_count')[:limit]
        
        return Response([{
            'id': p.id,
            'name': p.name,
            'views': p.view_count,
            'clicks': p.click_count,
            'shares': p.share_count,
            'price': float(p.price)
        } for p in products])
    
    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """Track an analytics event."""
        serializer = AnalyticsEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        event = AnalyticsEvent.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.data.get('session_id', ''),
            event_type=request.data.get('event_type'),
            product_id=request.data.get('product'),
            platform=request.data.get('platform', ''),
            source=request.data.get('source', ''),
            medium=request.data.get('medium', ''),
            campaign=request.data.get('campaign', ''),
            metadata=request.data.get('metadata', {}),
            referrer=request.data.get('referrer', ''),
            user_agent=request.data.get('user_agent', '')
        )
        
        return Response({
            'event_id': event.id,
            'message': 'Event tracked successfully.'
        }, status=status.HTTP_201_CREATED)


class PlatformAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for platform analytics."""
    permission_classes = [IsAuthenticated]
    serializer_class = PlatformAnalyticsSerializer
    
    def get_queryset(self):
        return PlatformAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get platform summary."""
        queryset = self.get_queryset()
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        data = queryset.filter(date__range=[start_date, end_date]).values(
            'platform'
        ).annotate(
            total_clicks=Sum('clicks'),
            total_impressions=Sum('impressions'),
            total_engagements=Sum('engagements')
        )
        
        return Response(list(data))


class ConversionFunnelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for conversion funnel."""
    permission_classes = [IsAuthenticated]
    serializer_class = ConversionFunnelSerializer
    
    def get_queryset(self):
        return ConversionFunnel.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current funnel data."""
        today = timezone.now().date()
        funnel = self.get_queryset().filter(date=today).first()
        
        if funnel:
            return Response({
                'impressions': funnel.impressions,
                'visits': funnel.visits,
                'product_views': funnel.product_views,
                'add_to_carts': funnel.add_to_carts,
                'checkouts': funnel.checkouts,
                'purchases': funnel.purchases,
                'rates': {
                    'visit_to_product': float(funnel.visit_to_product_rate),
                    'product_to_cart': float(funnel.product_to_cart_rate),
                    'cart_to_checkout': float(funnel.cart_to_checkout_rate),
                    'checkout_to_purchase': float(funnel.checkout_to_purchase_rate),
                    'overall': float(funnel.overall_conversion_rate)
                }
            })
        
        return Response({
            'impressions': 0,
            'visits': 0,
            'product_views': 0,
            'add_to_carts': 0,
            'checkouts': 0,
            'purchases': 0,
            'rates': {
                'visit_to_product': 0,
                'product_to_cart': 0,
                'cart_to_checkout': 0,
                'checkout_to_purchase': 0,
                'overall': 0
            }
        })

