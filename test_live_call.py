"""
📞 LIVE CALL TEST - Make a real test call
Usage: python test_live_call.py --phone +1234567890
"""

import os
import sys
import django
import argparse
from decouple import config

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import HumeAgent, TwilioCall
from twilio.rest import Client

User = get_user_model()

# Environment variables
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
BASE_URL = config('BASE_URL', default='http://localhost:8000')


def create_test_agent():
    """Create or get a test agent"""
    user = User.objects.first()
    if not user:
        print("❌ No user found! Create a user first.")
        return None
    
    agent, created = HumeAgent.objects.get_or_create(
        name="Live Test Agent",
        defaults={
            'description': 'Agent for live call testing',
            'hume_config_id': config('HUME_CONFIG_ID', default=''),
            'voice_name': 'ITO',
            'language': 'en',
            'system_prompt': 'You are a friendly AI assistant testing the call system. Be brief and natural.',
            'greeting_message': 'Hello! This is a test call from the AI voice system. Can you hear me clearly?',
            'status': 'active',
            'created_by': user
        }
    )
    
    if created:
        print(f"✅ Created new agent: {agent.name}")
    else:
        print(f"✅ Using existing agent: {agent.name}")
    
    return agent


def initiate_call(to_number, agent):
    """Initiate a test call"""
    print(f"\n📞 Initiating call to {to_number}...")
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # WebSocket URL for this call
        # Note: This should point to your deployed server with WebSocket support
        webhook_url = f"{BASE_URL}/ws/hume-twilio/call/"
        
        # Create TwiML for the call
        from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
        
        response = VoiceResponse()
        
        # Greeting
        response.say(
            "Connecting you to the AI assistant. Please wait.",
            voice='alice',
            language='en-US'
        )
        
        # Connect to WebSocket
        connect = Connect()
        stream = Stream(url=webhook_url)
        connect.append(stream)
        response.append(connect)
        
        twiml = str(response)
        
        print(f"\n📝 TwiML generated:")
        print(twiml)
        
        # Make the call
        call = client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml,
            status_callback=f"{BASE_URL}/api/hume-twilio/webhooks/status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        print(f"\n✅ Call initiated!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   From: {call.from_}")
        print(f"   To: {call.to}")
        
        # Create database record
        db_call = TwilioCall.objects.create(
            agent=agent,
            twilio_call_sid=call.sid,
            to_number=to_number,
            from_number=TWILIO_PHONE_NUMBER,
            status='initiated',
            customer_name='Test Customer'
        )
        
        print(f"✅ Call record created (ID: {db_call.id})")
        
        print("\n📞 Call in progress...")
        print("   Check your phone and answer the call")
        print("   The AI assistant will greet you")
        print("\n⏳ Monitoring call status...")
        
        # Monitor call status
        import time
        for i in range(30):  # Monitor for 30 seconds
            time.sleep(1)
            call = client.calls(call.sid).fetch()
            print(f"   [{i+1}s] Status: {call.status}", end='\r')
            
            if call.status in ['completed', 'failed', 'busy', 'no-answer']:
                break
        
        print(f"\n\n✅ Final call status: {call.status}")
        
        # Update database
        db_call.status = call.status
        db_call.save()
        
        return call
        
    except Exception as e:
        print(f"\n❌ Call failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description='Make a live test call')
    parser.add_argument('--phone', type=str, required=True, help='Phone number to call (e.g., +1234567890)')
    parser.add_argument('--agent-id', type=int, help='Agent ID to use (optional)')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📞 LIVE CALL TEST")
    print("="*60)
    
    # Validate phone number format
    if not args.phone.startswith('+'):
        print("❌ Phone number must include country code (e.g., +1234567890)")
        return
    
    print(f"\n🎯 Target: {args.phone}")
    
    # Check environment
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("❌ Missing Twilio credentials in .env file!")
        print("   Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        return
    
    print(f"✅ Twilio Account: {TWILIO_ACCOUNT_SID[:10]}...")
    print(f"✅ From Number: {TWILIO_PHONE_NUMBER}")
    print(f"✅ Base URL: {BASE_URL}")
    
    # Get or create agent
    if args.agent_id:
        try:
            agent = HumeAgent.objects.get(id=args.agent_id)
            print(f"✅ Using agent: {agent.name} (ID: {agent.id})")
        except HumeAgent.DoesNotExist:
            print(f"❌ Agent with ID {args.agent_id} not found!")
            return
    else:
        agent = create_test_agent()
        if not agent:
            return
    
    # Confirm before calling
    print(f"\n⚠️  WARNING: This will make a REAL phone call!")
    print(f"   To: {args.phone}")
    print(f"   From: {TWILIO_PHONE_NUMBER}")
    print(f"   Agent: {agent.name}")
    
    confirm = input("\n   Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Call cancelled")
        return
    
    # Make the call
    call = initiate_call(args.phone, agent)
    
    if call:
        print("\n" + "="*60)
        print("✅ TEST COMPLETED")
        print("="*60)
        print("\nTo view call logs:")
        print(f"  python manage.py shell")
        print(f"  >>> from HumeAiTwilio.models import TwilioCall")
        print(f"  >>> call = TwilioCall.objects.get(twilio_call_sid='{call.sid}')")
        print(f"  >>> call.conversation_logs.all()")
    else:
        print("\n❌ Test failed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
