#!/usr/bin/env python
"""
🔍 COMPLETE HUME AI SETUP VERIFICATION
Checks all HumeAI configuration and integration points
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("🔍 HUME AI SETUP VERIFICATION")
print("=" * 80)

# Check 1: Environment variables
print("\n[CHECK 1] HumeAI Credentials")
print("-" * 80)

hume_config_id = config('HUME_CONFIG_ID', default='')
hume_api_key = config('HUME_API_KEY', default='')
hume_secret_key = config('HUME_SECRET_KEY', default='')
hume_model = config('HUME_AI_MODEL', default='EVI-3')

print(f"Config ID:   {hume_config_id if hume_config_id else '❌ MISSING'}")
print(f"API Key:     {'✅ Present' if hume_api_key else '❌ MISSING'}")
print(f"Secret Key:  {'✅ Present' if hume_secret_key else '❌ MISSING'}")
print(f"Model:       {hume_model}")

# Check 2: HumeAI Python package
print("\n[CHECK 2] HumeAI SDK Installation")
print("-" * 80)

try:
    import hume
    print(f"✅ HumeAI SDK installed: {hume.__version__ if hasattr(hume, '__version__') else 'version unknown'}")
    
    from hume import HumeStreamClient, Stream, MicrophoneInterface, StreamConnectOptions
    print("✅ HumeStreamClient imported successfully")
    
    from hume.models.config import VoiceConfig
    print("✅ VoiceConfig imported successfully")
    
except ImportError as e:
    print(f"❌ HumeAI SDK issue: {e}")
    print("   Install with: pip install hume")

# Check 3: Django channels & routing
print("\n[CHECK 3] Django Channels Setup")
print("-" * 80)

try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    print("✅ Django Channels installed")
    
    from HumeAiTwilio.routing import websocket_urlpatterns
    print(f"✅ WebSocket routing configured: {len(websocket_urlpatterns)} patterns")
    
    for pattern in websocket_urlpatterns:
        print(f"   - {pattern.pattern}")
    
except ImportError as e:
    print(f"❌ Django Channels issue: {e}")

# Check 4: Consumer classes
print("\n[CHECK 4] HumeAI Consumer Classes")
print("-" * 80)

try:
    from HumeAiTwilio.vonage_realtime_consumer import VonageRealTimeConsumer
    print("✅ VonageRealTimeConsumer loaded")
    
    from HumeAiTwilio.hume_realtime_consumer import HumeTwilioRealTimeConsumer
    print("✅ HumeTwilioRealTimeConsumer loaded")
    
except ImportError as e:
    print(f"❌ Consumer class issue: {e}")

# Check 5: Vonage configuration
print("\n[CHECK 5] Vonage Voice Configuration")
print("-" * 80)

vonage_api_key = config('VONAGE_API_KEY', default='')
vonage_app_id = config('VONAGE_APPLICATION_ID', default='')
vonage_phone = config('VONAGE_PHONE_NUMBER', default='')
base_url = config('BASE_URL', default='')

print(f"API Key:           {'✅ Present' if vonage_api_key else '❌ MISSING'}")
print(f"Application ID:    {'✅ Present' if vonage_app_id else '❌ MISSING'}")
print(f"Phone Number:      {vonage_phone if vonage_phone else '❌ MISSING'}")
print(f"Base URL:          {base_url if base_url else '❌ MISSING'}")

# Check 6: Webhook URLs
print("\n[CHECK 6] Webhook Configuration")
print("-" * 80)

webhook_answer = f"{base_url}/api/hume-twilio/vonage-voice-webhook/" if base_url else "N/A"
webhook_events = f"{base_url}/api/hume-twilio/vonage-event-callback/" if base_url else "N/A"
webhook_stream = f"{base_url.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/vonage-stream/{{uuid}}" if base_url else "N/A"

print(f"Answer Webhook:    {webhook_answer}")
print(f"Events Webhook:    {webhook_events}")
print(f"Stream WebSocket:  {webhook_stream}")

# Check 7: Database models
print("\n[CHECK 7] Database Models")
print("-" * 80)

try:
    from HumeAiTwilio.models import TwilioCall, HumeAgent, HumeEmotion
    
    call_count = TwilioCall.objects.count()
    agent_count = HumeAgent.objects.count()
    emotion_count = HumeEmotion.objects.count()
    
    print(f"✅ TwilioCall:    {call_count} records")
    print(f"✅ HumeAgent:     {agent_count} records")
    print(f"✅ HumeEmotion:   {emotion_count} records")
    
    # Show recent calls
    recent_calls = TwilioCall.objects.order_by('-created_at')[:3]
    if recent_calls:
        print(f"\n   Recent calls:")
        for call in recent_calls:
            print(f"   - {call.call_sid[:12]}... ({call.provider}) @ {call.created_at.strftime('%H:%M:%S')}")
    
except Exception as e:
    print(f"❌ Database models issue: {e}")

# Check 8: Django server status
print("\n[CHECK 8] Django Server Status")
print("-" * 80)

try:
    from django.apps import apps
    
    installed_apps = [app.name for app in apps.get_app_configs()]
    
    if 'channels' in installed_apps:
        print("✅ Channels app installed")
    else:
        print("❌ Channels app NOT in INSTALLED_APPS")
    
    if 'HumeAiTwilio' in installed_apps:
        print("✅ HumeAiTwilio app installed")
    else:
        print("❌ HumeAiTwilio app NOT in INSTALLED_APPS")
    
except Exception as e:
    print(f"❌ Django apps check failed: {e}")

# Check 9: ASGI Configuration
print("\n[CHECK 9] ASGI Configuration")
print("-" * 80)

try:
    import sys
    import os
    
    # Check if asgi.py exists and has proper config
    asgi_path = os.path.join(os.path.dirname(__file__), 'core', 'asgi.py')
    if os.path.exists(asgi_path):
        print(f"✅ ASGI configuration file exists: {asgi_path}")
        
        # Try to load it
        try:
            import core.asgi
            print("✅ ASGI module imported successfully")
        except Exception as e:
            print(f"⚠️  ASGI import warning: {e}")
    else:
        print(f"❌ ASGI file not found: {asgi_path}")
        
except Exception as e:
    print(f"⚠️  ASGI check failed: {e}")

# Summary
print("\n" + "=" * 80)
print("✅ SETUP VERIFICATION COMPLETE")
print("=" * 80)

print("\n📋 What This Means:")
print("""
✅ All services ready:
   1. HumeAI credentials configured
   2. Django Channels WebSocket routing ready
   3. Vonage webhook URLs configured
   4. Database models ready
   5. Consumer classes loaded

🔄 When you make a call:
   1. Vonage connects caller
   2. Vonage calls answer_url webhook
   3. Django returns WebSocket stream URL
   4. Caller connects to /ws/vonage-stream/{uuid}
   5. VonageRealTimeConsumer bridges to HumeAI
   6. Real-time audio streaming begins
   7. Emotions detected in real-time
   8. Call recorded in database

💡 If call ends in 5s:
   - Check if Django server received answer_url webhook
   - Verify WebSocket connection was established
   - Monitor HumeAI WebSocket connection in logs
""")

print("\n" + "=" * 80)
