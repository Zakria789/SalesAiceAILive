"""
URL Configuration for HumeAI + Twilio Integration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HumeAgentViewSet,
    TwilioCallViewSet,
    ConversationLogViewSet,
    CallAnalyticsViewSet,
    twilio_webhook,
    twilio_twiml,
    hume_webhook,
    dashboard_stats,
    recent_calls,
)

# NEW: Import Twilio Voice Bridge (WebSocket version)
from .twilio_voice_bridge import (
    twilio_voice_webhook,
    twilio_status_callback,
)

# NEW: Import Simple Voice (NO WebSocket - FREE version)
from .twilio_simple_voice import (
    twilio_voice_webhook_simple,
    process_speech_simple,
    twilio_status_callback_simple,
)

# FIXED: Import ngrok-compatible webhooks
from .twilio_webhook_fixed import (
    twilio_voice_webhook_fixed,
    twilio_status_callback_fixed,
    health_check,
)

# VONAGE: Import Vonage voice bridge
from .vonage_voice_bridge import (
    vonage_voice_webhook,
    vonage_outgoing_answer_webhook,
    vonage_event_callback,
    vonage_stream_callback,
    vonage_health_check,
)

# Call Initiation APIs
from .api_views.call_initiation import (
    get_available_agents,
    initiate_call,
    get_call_status,
    get_call_data,
    get_all_calls,
    initiate_bulk_calls
)

# 🚀 Intelligent Scheduling APIs
from .scheduling_api import (
    initiate_call_with_scheduling,
    analyze_call_and_schedule,
    get_scheduling_stats,
    test_intelligent_scheduling,
    get_customer_call_history
)

# Dashboard APIs
from .api_views.dashboard_views import (
    get_all_active_calls,  # NEW: Unified endpoint for both inbound & outbound
    get_active_inbound_calls,
    get_inbound_call_history,
    quick_outbound_call,
    get_scheduled_bulk_calls,
    get_outbound_call_history,
    get_analytics_dashboard,
    upload_bulk_calls_csv,
    get_live_call_updates  # 🔴 NEW: Real-time polling endpoint
)

# 📊 CLARIFIES Analytics APIs
try:
    from .api_views.analytics_views import (
        conversation_metrics,
        objection_types,
        clarifies_flow_analysis,
        win_loss_rate,
        tone_trends,
        call_explainability,
        risk_flags_audit
    )
    print("✅ Analytics views imported successfully!")
except ImportError as e:
    print(f"❌ FAILED to import analytics views: {e}")
    import traceback
    traceback.print_exc()
    # Create dummy views to prevent URL errors
    from rest_framework.decorators import api_view
    from rest_framework.response import Response
    
    @api_view(['GET'])
    def conversation_metrics(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def objection_types(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def clarifies_flow_analysis(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def win_loss_rate(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def tone_trends(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def call_explainability(request, call_id):
        return Response({'error': 'View not loaded - import failed'}, status=500)
    
    @api_view(['GET'])
    def risk_flags_audit(request):
        return Response({'error': 'View not loaded - import failed'}, status=500)

# 🔍 DEBUG: Test endpoint
from .test_analytics_endpoint import test_analytics_debug
from .test_simple_view import test_simple_view
from .test_analytics_noauth import test_conversation_metrics as test_conv, test_objection_types as test_obj

app_name = 'HumeAiTwilio'

# Router for ViewSets
router = DefaultRouter()
router.register(r'agents', HumeAgentViewSet, basename='agent')
router.register(r'calls', TwilioCallViewSet, basename='call')
router.register(r'conversations', ConversationLogViewSet, basename='conversation')
router.register(r'analytics', CallAnalyticsViewSet, basename='analytics')

urlpatterns = [
    # ⚠️ IMPORTANT: Explicit paths MUST come BEFORE router.urls to avoid conflicts
    
    # 📊 CLARIFIES ANALYTICS ENDPOINTS - New Conversation Analysis System
    # These MUST be FIRST to avoid being captured by router's analytics/{id}/ pattern
    path('analytics/conversation-metrics/', conversation_metrics, name='analytics-conversation-metrics'),
    path('analytics/objection-types/', objection_types, name='analytics-objection-types'),
    path('analytics/clarifies-flow/', clarifies_flow_analysis, name='analytics-clarifies-flow'),
    path('analytics/win-loss-rate/', win_loss_rate, name='analytics-win-loss-rate'),
    path('analytics/tone-trends/', tone_trends, name='analytics-tone-trends'),
    path('analytics/risk-flags/', risk_flags_audit, name='analytics-risk-flags'),
    path('call/<str:call_id>/explainability/', call_explainability, name='call-explainability'),
    
    # 🔍 DEBUG ENDPOINTS
    path('debug/analytics-test/', test_analytics_debug, name='debug-analytics-test'),
    path('debug/simple-test/', test_simple_view, name='debug-simple-test'),
    path('debug/test-conv/', test_conv, name='debug-test-conv'),
    path('debug/test-obj/', test_obj, name='debug-test-obj'),
    
    # API endpoints (Router - comes AFTER explicit paths)
    path('', include(router.urls)),
    
    # Webhook endpoints (original)
    path('webhooks/twilio/', twilio_webhook, name='twilio-webhook'),
    path('webhooks/twilio/twiml/', twilio_twiml, name='twilio-twiml'),
    path('webhooks/hume/', hume_webhook, name='hume-webhook'),
    
    # NEW: Twilio Voice Bridge endpoints (WebSocket - requires paid plan)
    path('voice-webhook/', twilio_voice_webhook, name='twilio-voice-webhook'),
    path('status-callback/', twilio_status_callback, name='twilio-status-callback'),
    
    # NEW: Simple Voice endpoints (NO WebSocket - FREE PythonAnywhere)
    path('voice-webhook-simple/', twilio_voice_webhook_simple, name='voice-webhook-simple'),
    path('process-speech-simple/', process_speech_simple, name='process-speech-simple'),
    path('status-callback-simple/', twilio_status_callback_simple, name='status-callback-simple'),
    
    # FIXED: Ngrok-compatible webhooks (Use these with Twilio!)
    path('voice-webhook-fixed/', twilio_voice_webhook_fixed, name='voice-webhook-fixed'),
    path('status-callback-fixed/', twilio_status_callback_fixed, name='status-callback-fixed'),
    path('health/', health_check, name='health-check'),
    
    # VONAGE: Voice integration endpoints
    path('vonage-voice-webhook/', vonage_voice_webhook, name='vonage-voice-webhook'),
    path('vonage-outgoing-answer/', vonage_outgoing_answer_webhook, name='vonage-outgoing-answer'),
    path('vonage-event-callback/', vonage_event_callback, name='vonage-event-callback'),
    path('vonage-stream-callback/', vonage_stream_callback, name='vonage-stream-callback'),
    path('vonage-health/', vonage_health_check, name='vonage-health-check'),
    
    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('dashboard/recent-calls/', recent_calls, name='recent-calls'),
    
    # Dashboard API endpoints (NEW)
    path('dashboard/active-calls/', get_all_active_calls, name='dashboard-all-active'),  # NEW: Both inbound & outbound
    path('dashboard/live-updates/', get_live_call_updates, name='dashboard-live-updates'),  # 🔴 NEW: Real-time polling
    path('dashboard/inbound/active/', get_active_inbound_calls, name='dashboard-inbound-active'),
    path('dashboard/inbound/history/', get_inbound_call_history, name='dashboard-inbound-history'),
    path('dashboard/outbound/quick-call/', quick_outbound_call, name='dashboard-outbound-quick'),
    path('dashboard/outbound/scheduled/', get_scheduled_bulk_calls, name='dashboard-outbound-scheduled'),
    path('dashboard/outbound/history/', get_outbound_call_history, name='dashboard-outbound-history'),
    path('dashboard/analytics/', get_analytics_dashboard, name='dashboard-analytics'),
    path('dashboard/bulk-calls/upload/', upload_bulk_calls_csv, name='dashboard-bulk-upload'),
    
    # Call Initiation endpoints (same as /api/call/)
    path('agents-list/', get_available_agents, name='agents-list'),
    path('initiate-call/', initiate_call, name='initiate-call'),
    path('call-status/<str:call_sid>/', get_call_status, name='call-status'),
    path('get-call-data/<str:call_sid>/', get_call_data, name='get-call-data'),
    path('get-all-calls/', get_all_calls, name='get-all-calls'),
    path('initiate-bulk-calls/', initiate_bulk_calls, name='initiate-bulk-calls'),
    
    # 🚀 INTELLIGENT SCHEDULING ENDPOINTS - New Smart Auto-Call System
    path('intelligent/initiate-with-scheduling/', initiate_call_with_scheduling, name='initiate-call-with-scheduling'),
    path('intelligent/analyze-and-schedule/', analyze_call_and_schedule, name='analyze-call-and-schedule'),
    path('intelligent/scheduling-stats/', get_scheduling_stats, name='get-scheduling-stats'),
    path('intelligent/test-scheduling/', test_intelligent_scheduling, name='test-intelligent-scheduling'),
    path('intelligent/customer-history/', get_customer_call_history, name='get-customer-call-history'),
]
