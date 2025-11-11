#!/usr/bin/env python
"""Test actual Vonage call creation"""

from vonage import Auth, Vonage
from decouple import config

VONAGE_API_KEY = config('VONAGE_API_KEY', default='')
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default='')
VONAGE_PHONE_NUMBER = config('VONAGE_PHONE_NUMBER', default='')
BASE_URL = config('BASE_URL', default='https://uncontortioned-na-ponderously.ngrok-free.dev')

print("Testing Vonage call creation with API key auth...")
print(f"API_KEY: {VONAGE_API_KEY}")
print(f"PHONE: {VONAGE_PHONE_NUMBER}")
print()

try:
    # Create auth
    auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
    client = Vonage(auth)
    print("✅ Auth and client created")
    
    # Try to make a call (will fail with actual numbers but we're testing the SDK call)
    phone_number = "+923403471112"
    to_clean = phone_number.lstrip('+')
    from_clean = VONAGE_PHONE_NUMBER.lstrip('+')
    
    print(f"📞 Calling create_call with:")
    print(f"   to: {to_clean}")
    print(f"   from: {from_clean}")
    
    try:
        call = client.voice.create_call({
            "to": [{"type": "phone", "number": to_clean}],
            "from_": {"type": "phone", "number": from_clean},
            "answer_url": [f"{BASE_URL}/api/hume-twilio/vonage-voice-webhook/"],
            "event_url": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"]
        })
        print(f"✅ Call created: {call.uuid}")
    except Exception as call_error:
        print(f"❌ Call creation error: {call_error}")
        print(f"   Type: {type(call_error).__name__}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
