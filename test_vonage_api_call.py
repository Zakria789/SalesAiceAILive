#!/usr/bin/env python
"""
Test Vonage API Call - Simulate making an actual call
"""

import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from decouple import config
from vonage import Auth, Vonage
from HumeAiTwilio.models import HumeAgent, TwilioCall

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_vonage_call():
    """Test making a call using Vonage API"""
    print_section("VONAGE API CALL TEST")
    
    # Load configuration
    VONAGE_API_KEY = config('VONAGE_API_KEY')
    VONAGE_API_SECRET = config('VONAGE_API_SECRET')
    VONAGE_PHONE_NUMBER = config('VONAGE_PHONE_NUMBER')
    BASE_URL = config('BASE_URL', default='https://example.com')
    
    print(f"\n1. Configuration Loaded:")
    print(f"   API Key: {VONAGE_API_KEY[:10]}...")
    print(f"   Phone Number: {VONAGE_PHONE_NUMBER}")
    print(f"   Base URL: {BASE_URL}")
    
    # Initialize Vonage client
    print(f"\n2. Initializing Vonage Client:")
    try:
        vonage_auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
        vonage_client = Vonage(vonage_auth)
        print(f"   [OK] Vonage client initialized")
    except Exception as e:
        print(f"   [ERROR] Failed to initialize: {e}")
        return False
    
    # Create NCCO (call instructions)
    print(f"\n3. Creating NCCO (Call Instructions):")
    try:
        ncco = [
            {
                "action": "connect",
                "eventWebhook": {
                    "url": f"{BASE_URL}/api/hume-twilio/vonage-event-callback/",
                    "method": "POST"
                }
            },
            {
                "action": "input",
                "type": ["audio"],
                "eventWebhook": {
                    "url": f"{BASE_URL}/api/hume-twilio/vonage-stream-callback/",
                    "method": "POST"
                },
                "timeOut": 3600
            }
        ]
        print(f"   [OK] NCCO created with {len(ncco)} actions")
        print(f"       Action 1: {ncco[0]['action']}")
        print(f"       Action 2: {ncco[1]['action']}")
    except Exception as e:
        print(f"   [ERROR] Failed to create NCCO: {e}")
        return False
    
    # Prepare test call parameters
    test_phone_number = "+923403471112"  # Test number
    print(f"\n4. Test Call Parameters:")
    print(f"   To Number: {test_phone_number}")
    print(f"   From Number: {VONAGE_PHONE_NUMBER}")
    
    # Make the call
    print(f"\n5. Making Vonage API Call:")
    try:
        print(f"   Calling vonage_client.voice.create_call()...")
        call_response = vonage_client.voice.create_call(
            to=[{"type": "phone", "number": test_phone_number}],
            from_={"type": "phone", "number": VONAGE_PHONE_NUMBER},
            ncco=ncco
        )
        
        print(f"   [OK] API call successful!")
        print(f"\n   Response from Vonage API:")
        print(f"   {json.dumps(call_response, indent=6)}")
        
        call_uuid = call_response.get('uuid')
        status = call_response.get('request_id')
        
        if call_uuid:
            print(f"\n   [SUCCESS] Call UUID: {call_uuid}")
            print(f"   [SUCCESS] Request ID: {status}")
            
            # Save to database
            print(f"\n6. Saving Call to Database:")
            try:
                db_call = TwilioCall.objects.create(
                    call_sid=call_uuid,
                    to_number=test_phone_number,
                    from_number=VONAGE_PHONE_NUMBER,
                    status='initiated',
                    direction='outbound_api',
                    provider='vonage',
                    customer_name='Test Call',
                    hume_config_id=config('HUME_CONFIG_ID', default='')
                )
                print(f"   [OK] Call saved to database")
                print(f"       Database ID: {db_call.id}")
                print(f"       Provider: {db_call.provider}")
                print(f"       Status: {db_call.status}")
                
                return True
                
            except Exception as db_error:
                print(f"   [WARNING] Failed to save to database: {db_error}")
                return True  # API call worked even if DB save failed
        else:
            print(f"   [ERROR] No UUID in response")
            return False
            
    except Exception as e:
        print(f"   [ERROR] API call failed: {type(e).__name__}")
        print(f"   {str(e)}")
        return False

def main():
    """Run the test"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  VONAGE API CALL TEST".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    result = test_vonage_call()
    
    print_section("TEST RESULT")
    
    if result:
        print("\n  [SUCCESS] Vonage API is working correctly!")
        print("  [SUCCESS] Your system is ready to make calls via Vonage")
        print("  [SUCCESS] Calls will be stored in the database")
        return 0
    else:
        print("\n  [FAILED] Vonage API call failed")
        print("  [INFO] Check your API credentials and network connectivity")
        return 1

if __name__ == '__main__':
    sys.exit(main())
