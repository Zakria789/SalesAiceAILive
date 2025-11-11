#!/usr/bin/env python3
"""
Test script to verify broadcasting fix
This will test if the CallSession broadcasting works without errors
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeai_backend.settings')
django.setup()

def test_broadcasting():
    from calls.models import CallSession
    from calls.broadcasting import CallsBroadcaster
    from agents.models import Agent
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    
    User = get_user_model()
    
    print("🧪 TESTING CALL BROADCASTING FIX")
    print("=" * 40)
    
    try:
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        
        # Get a test agent
        agent = Agent.objects.first()
        if not agent:
            print("❌ No agents found in database")
            return
        
        # Create a test call session
        call_session = CallSession(
            user=user,
            caller_number='+12295152040',
            callee_number='+1234567890',
            caller_name='Test User',
            call_type='outbound',
            status='initiated',
            agent=agent,
            started_at=timezone.now()
        )
        
        # Don't save to database, just test broadcasting
        print("✅ Test CallSession created")
        print(f"   ID: {call_session.id}")
        print(f"   Status: {call_session.status}")
        print(f"   Started: {call_session.started_at}")
        print(f"   Caller: {call_session.caller_number}")
        
        # Test broadcasting
        broadcaster = CallsBroadcaster()
        print("\n🔔 Testing broadcast_call_created...")
        
        try:
            broadcaster.broadcast_call_created(
                call_session=call_session,
                user_id=user.id,
                agent_id=agent.id
            )
            print("✅ broadcast_call_created: SUCCESS")
        except Exception as e:
            print(f"❌ broadcast_call_created: FAILED - {e}")
            return
        
        print("\n🔔 Testing broadcast_call_status_update...")
        
        try:
            broadcaster.broadcast_call_status_update(
                call_session=call_session,
                user_id=user.id,
                agent_id=agent.id
            )
            print("✅ broadcast_call_status_update: SUCCESS")
        except Exception as e:
            print(f"❌ broadcast_call_status_update: FAILED - {e}")
            return
        
        print("\n🎯 ALL BROADCASTING TESTS PASSED!")
        print("✅ The updated_at field error has been fixed")
        print("✅ Call initiation should now work without broadcasting errors")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_broadcasting()