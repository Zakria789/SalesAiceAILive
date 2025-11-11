#!/usr/bin/env python
"""
🔧 TEST CALL INITIATION API
Test the fixed initiate_vonage_call() function directly
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from HumeAiTwilio.vonage_voice_bridge import initiate_vonage_call
from decouple import config
import json
from datetime import datetime

print('='*80)
print('TESTING CALL INITIATION API')
print('='*80)

# Configuration
to_number = "+923403471112"
from_number = config('VONAGE_PHONE_NUMBER')

print(f"\n📋 TEST PARAMETERS:")
print(f"   From: {from_number}")
print(f"   To: {to_number}")
print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n{'='*80}")
print('STEP 1: CALLING initiate_vonage_call()')
print('='*80)

try:
    result = initiate_vonage_call(
        to_number=to_number,
        from_number=from_number,
        agent_id=None  # Let it use default agent
    )
    
    print(f"\n✅ API RESPONSE RECEIVED!")
    print(f"\n📊 RESPONSE DETAILS:")
    print(json.dumps(result, indent=2))
    
    print(f"\n{'='*80}")
    print('VERIFICATION')
    print('='*80)
    
    if result.get('success'):
        print(f"\n✅ CALL INITIATION SUCCESSFUL!")
        print(f"\n   Call UUID: {result.get('call_uuid')}")
        print(f"   Call ID (DB): {result.get('call_id')}")
        print(f"   From: {result.get('from')}")
        print(f"   To: {result.get('to')}")
        print(f"   Status: {result.get('status')}")
        
        # Check database
        from HumeAiTwilio.models import TwilioCall
        
        try:
            call = TwilioCall.objects.get(id=result.get('call_id'))
            print(f"\n✅ DATABASE RECORD FOUND:")
            print(f"   ID: {call.id}")
            print(f"   Call SID: {call.call_sid}")
            print(f"   Agent: {call.agent}")
            print(f"   Agent ID: {call.agent_id if call.agent else 'NULL'}")
            print(f"   Status: {call.status}")
            print(f"   Provider: {call.provider}")
            print(f"   Created: {call.started_at}")
            
            if call.agent:
                print(f"\n✅ AGENT ASSIGNED:")
                print(f"   Agent Name: {call.agent.name}")
                print(f"   Agent Config ID: {call.agent.hume_config_id}")
                print(f"   Agent Status: {call.agent.status}")
            else:
                print(f"\n❌ NO AGENT ASSIGNED - THIS IS THE PROBLEM!")
        
        except Exception as e:
            print(f"\n❌ Database error: {e}")
    
    else:
        print(f"\n❌ CALL INITIATION FAILED!")
        print(f"   Error: {result.get('error')}")

except Exception as e:
    print(f"\n❌ ERROR CALLING API:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print('ANALYSIS')
print('='*80 + "\n")

print("""
✅ IF YOU SEE:
   - success: true
   - call_uuid: (some UUID)
   - call_id: (some ID)
   - Agent Assigned: (agent name)
   
   → API IS WORKING CORRECTLY! ✅

❌ IF YOU SEE:
   - success: true
   - BUT Agent Assigned: NULL
   
   → Agent assignment still broken
   → Need to debug further
""")

print('='*80 + '\n')
