"""
Routing configuration for WebSocket connections
PRODUCTION: Using HumeTwilioRealTimeConsumer for complete HumeAI EVI integration
           Using VonageRealTimeConsumer for Vonage real-time audio streaming
"""

from django.urls import re_path
from .hume_realtime_consumer import HumeTwilioRealTimeConsumer  # MAIN: Full HumeAI EVI integration
from .vonage_realtime_consumer import VonageRealTimeConsumer  # VONAGE: Real-time Vonage integration

websocket_urlpatterns = [
    # MAIN PRODUCTION ROUTE: Complete HumeAI + Twilio real-time integration
    # This handles all voice calls with full EVI support
    re_path(r'^ws/hume-twilio/stream/(?P<call_sid>[^/]+)/?$', HumeTwilioRealTimeConsumer.as_asgi()),
    
    # Alternative path (same consumer, different URL pattern for compatibility)
    re_path(r'^api/hume-twilio/stream/(?P<call_sid>[^/]+)/?$', HumeTwilioRealTimeConsumer.as_asgi()),
    
    # VONAGE REAL-TIME ROUTES: WebSocket streaming for Vonage calls
    # Mirrors Twilio consumer with Vonage-specific audio handling
    re_path(r'^ws/vonage-stream/(?P<uuid>[^/]+)/?$', VonageRealTimeConsumer.as_asgi()),
    
    # Alternative Vonage path (for API compatibility)
    re_path(r'^api/vonage-stream/(?P<uuid>[^/]+)/?$', VonageRealTimeConsumer.as_asgi()),
]

# NOTE: Old routes removed to avoid conflicts:
# - TwilioHumeStreamConsumer (was causing "Handle media error" issues)
# - TwilioHumeEVIConsumer (incomplete implementation)
# - consumers.HumeTwilioStreamConsumer (placeholder only)
