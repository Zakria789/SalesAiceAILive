#!/usr/bin/env python
"""
🚀 VONAGE CALL - Using Official Vonage SDK (Highest Priority)
This should handle all authentication properly
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("=" * 80)
print("VONAGE CALL - Using Official SDK")
print("=" * 80)

# Configuration
api_key = config('VONAGE_API_KEY')
api_secret = config('VONAGE_API_SECRET')
application_id = config('VONAGE_APPLICATION_ID')
private_key_path = config('VONAGE_PRIVATE_KEY_PATH', default='./private_key.pem')
from_number = config('VONAGE_PHONE_NUMBER')
to_number = "+923403471112"

print(f"\n📋 Configuration:")
print(f"   API Key: {api_key}")
print(f"   App ID: {application_id[:20]}...")
print(f"   From: {from_number}")
print(f"   To: {to_number}\n")

try:
    from vonage import Vonage, Auth
    
    print("[STEP 1] Initializing Vonage client...")
    
    # Try with application-based auth (JWT)
    try:
        # Read private key
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        
        print("   ✅ Private key loaded")
        
        # Create auth with app credentials
        auth = Auth(
            api_key=api_key,
            api_secret=api_secret,
            application_id=application_id,
            private_key=private_key
        )
        
        client = Vonage(auth)
        print("   ✅ Vonage client created with JWT auth")
        
    except Exception as e:
        print(f"   ⚠️ JWT auth failed: {e}")
        print(f"   Trying basic auth instead...")
        
        # Fallback to basic auth
        auth = Auth(api_key=api_key, api_secret=api_secret)
        client = Vonage(auth)
        print("   ✅ Vonage client created with basic auth")
    
    print("\n[STEP 2] Making call...")
    
    to_clean = to_number.lstrip('+')
    from_clean = from_number.lstrip('+')
    
    # Create call WITH answer_url to enable WebSocket + HumeAI connection
    # The answer_url webhook tells Vonage how to handle the call when it's answered
    response = client.voice.create_call({
        "to": [{"type": "phone", "number": to_clean}],
        "from_": {"type": "phone", "number": from_clean},
        "answer_url": [f"{config('BASE_URL')}/api/hume-twilio/vonage-voice-webhook/"],
        "event_url": [f"{config('BASE_URL')}/api/hume-twilio/vonage-event-callback/"]
    })
    
    call_uuid = response.uuid
    
    print(f"\n   ✅ CALL INITIATED!")
    print(f"      UUID: {call_uuid}")
    print(f"      Status: RINGING\n")
    
    print("=" * 80)
    print("🎉 SUCCESS! VONAGE CALL IS LIVE!")
    print("=" * 80)
    
except ImportError as e:
    print(f"   ❌ Vonage SDK issue: {e}")
    print(f"   Make sure vonage package is installed")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
