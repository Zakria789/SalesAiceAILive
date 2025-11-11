#!/usr/bin/env python
"""
🔧 CALL INITIATION API - SIMPLE TEST
Test using the existing API endpoint from frontend
"""

import requests
import json
from datetime import datetime
from decouple import config

BASE_URL = config('BASE_URL', default='http://localhost:8002')
API_ENDPOINT = f"{BASE_URL}/api/hume-twilio/initiate-call/"

print('='*80)
print('TESTING CALL INITIATION API')
print('='*80)

# Configuration
# Configuration
to_number = "+923403471112"  # Pakistan number (with + sign)
agent_id = 1  # Use first agent by index (1, 2, 3...)

print(f"\n📋 REQUEST PARAMETERS:")
print(f"   Endpoint: {API_ENDPOINT}")
print(f"   Phone: {to_number}")
print(f"   Agent ID: {agent_id}")
print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Prepare request
payload = {
    'phone_no': to_number,
    'agent_id': agent_id
}

print(f"\n📤 SENDING REQUEST:")
print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        API_ENDPOINT,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\n✅ RESPONSE RECEIVED!")
    print(f"   Status Code: {response.status_code}")
    print(f"\n📊 RESPONSE DATA:")
    
    try:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        print(f"\n{'='*80}")
        print('ANALYSIS')
        print('='*80)
        
        if result.get('success'):
            print(f"\n✅ CALL INITIATION SUCCESSFUL!")
            print(f"\n   Call ID: {result.get('call_id')}")
            print(f"   Call UUID: {result.get('call_uuid')}")
            print(f"   To: {result.get('to')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Agent: {result.get('agent_name')}")
            
            if result.get('call_id'):
                print(f"\n✅ NEXT STEPS:")
                print(f"   1. Answer the call on: +{to_number}")
                print(f"   2. Listen to agent greeting")
                print(f"   3. Speak something")
                print(f"   4. Agent will respond")
                print(f"   5. Check database for emotions")
        else:
            print(f"\n❌ CALL INITIATION FAILED!")
            print(f"   Error: {result.get('error')}")
            if result.get('hint'):
                print(f"   Hint: {result.get('hint')}")
    
    except json.JSONDecodeError:
        print(f"   Response Text: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"\n❌ CONNECTION ERROR!")
    print(f"   Could not connect to: {API_ENDPOINT}")
    print(f"   Make sure Django server is running!")
    print(f"\n   Start server with:")
    print(f"   python manage.py runserver 0.0.0.0:8000")
    
except Exception as e:
    print(f"\n❌ ERROR:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}\n")
