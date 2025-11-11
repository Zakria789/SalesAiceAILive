"""
🔴 LIVE WEBSOCKET TEST - HumeAI + Twilio Connection
Complete integration test for voice call system
"""

import os
import sys
import django
import asyncio
import json
import websockets
from decouple import config

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import HumeAgent, TwilioCall

User = get_user_model()

# Environment variables
HUME_API_KEY = config('HUME_AI_API_KEY', default=config('HUME_API_KEY', default=''))
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')


class WebSocketTester:
    """Test WebSocket connection to HumeAI EVI"""
    
    def __init__(self):
        self.hume_ws = None
        self.connected = False
        
    async def test_hume_connection(self):
        """Test HumeAI WebSocket connection"""
        print("\n" + "="*60)
        print("🔌 TESTING HUME AI WEBSOCKET CONNECTION")
        print("="*60)
        
        if not HUME_API_KEY:
            print("❌ HUME_API_KEY not found in environment!")
            return False
        
        print(f"✅ API Key found: {HUME_API_KEY[:10]}...{HUME_API_KEY[-5:]}")
        
        try:
            # Build WebSocket URL
            url = "wss://api.hume.ai/v0/assistant/chat"
            params = {
                "apiKey": HUME_API_KEY,
            }
            
            if HUME_CONFIG_ID:
                params["configId"] = HUME_CONFIG_ID
                print(f"✅ Config ID: {HUME_CONFIG_ID}")
            
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            print(f"\n🔌 Connecting to: {url}")
            print(f"📝 With params: {list(params.keys())}")
            
            # Connect
            self.hume_ws = await websockets.connect(
                full_url,
                extra_headers={
                    "X-Hume-Api-Key": HUME_API_KEY,
                }
            )
            
            print("✅ Connected to HumeAI EVI WebSocket!")
            self.connected = True
            
            # Configure audio settings
            config_msg = {
                "type": "session_settings",
                "audio": {
                    "encoding": "mulaw",
                    "sample_rate": 8000,
                    "channels": 1
                }
            }
            
            await self.hume_ws.send(json.dumps(config_msg))
            print("✅ Audio settings configured (mulaw, 8kHz)")
            
            # Listen for initial response
            print("\n⏳ Waiting for server response...")
            try:
                response = await asyncio.wait_for(self.hume_ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received: {data.get('type', 'unknown')}")
                print(f"📦 Response: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⚠️  No response within 5 seconds (this may be normal)")
            
            # Test text message
            print("\n📤 Sending test message...")
            test_msg = {
                "type": "user_input",
                "text": "Hello, can you hear me?"
            }
            await self.hume_ws.send(json.dumps(test_msg))
            print("✅ Test message sent")
            
            # Listen for response
            print("⏳ Waiting for AI response...")
            try:
                for i in range(5):  # Try to receive 5 messages
                    response = await asyncio.wait_for(self.hume_ws.recv(), timeout=3.0)
                    data = json.loads(response)
                    msg_type = data.get('type', 'unknown')
                    print(f"📥 [{i+1}] {msg_type}")
                    
                    if msg_type == 'assistant_message':
                        content = data.get('message', {}).get('content', '')
                        print(f"   🤖 AI Response: {content}")
                    elif msg_type == 'audio_output':
                        print(f"   🔊 Audio output received!")
                    
            except asyncio.TimeoutError:
                print("⏹️  No more messages")
            
            print("\n✅ WebSocket connection test SUCCESSFUL!")
            return True
            
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ Invalid status code: {e.status_code}")
            print(f"   Response: {e.response}")
            return False
            
        except websockets.exceptions.WebSocketException as e:
            print(f"❌ WebSocket error: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if self.hume_ws:
                await self.hume_ws.close()
                print("🔌 Connection closed")
    
    async def test_twilio_config(self):
        """Test Twilio configuration"""
        print("\n" + "="*60)
        print("📞 TESTING TWILIO CONFIGURATION")
        print("="*60)
        
        if not TWILIO_ACCOUNT_SID:
            print("❌ TWILIO_ACCOUNT_SID not found!")
            return False
        
        if not TWILIO_AUTH_TOKEN:
            print("❌ TWILIO_AUTH_TOKEN not found!")
            return False
        
        if not TWILIO_PHONE_NUMBER:
            print("❌ TWILIO_PHONE_NUMBER not found!")
            return False
        
        print(f"✅ Account SID: {TWILIO_ACCOUNT_SID[:10]}...{TWILIO_ACCOUNT_SID[-5:]}")
        print(f"✅ Auth Token: {TWILIO_AUTH_TOKEN[:10]}...{TWILIO_AUTH_TOKEN[-5:]}")
        print(f"✅ Phone Number: {TWILIO_PHONE_NUMBER}")
        
        try:
            from twilio.rest import Client
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Test API access
            print("\n🔍 Testing Twilio API access...")
            account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
            print(f"✅ Account Status: {account.status}")
            print(f"✅ Account Name: {account.friendly_name}")
            
            # Get phone number details
            print("\n🔍 Verifying phone number...")
            incoming_numbers = client.incoming_phone_numbers.list(
                phone_number=TWILIO_PHONE_NUMBER
            )
            
            if incoming_numbers:
                number = incoming_numbers[0]
                print(f"✅ Number verified: {number.phone_number}")
                print(f"   Voice URL: {number.voice_url or 'Not set'}")
                print(f"   Capabilities: Voice={number.capabilities['voice']}, SMS={number.capabilities['sms']}")
            else:
                print(f"⚠️  Phone number {TWILIO_PHONE_NUMBER} not found in your account")
            
            print("\n✅ Twilio configuration test SUCCESSFUL!")
            return True
            
        except Exception as e:
            print(f"❌ Twilio test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_database_setup(self):
        """Check database configuration"""
        print("\n" + "="*60)
        print("💾 CHECKING DATABASE SETUP")
        print("="*60)
        
        try:
            # Check if agents exist
            agents = HumeAgent.objects.all()
            print(f"✅ HumeAgent model accessible")
            print(f"   Total agents: {agents.count()}")
            
            if agents.exists():
                for agent in agents[:3]:
                    print(f"   - {agent.name} (ID: {agent.id}, Status: {agent.status})")
            else:
                print("   ⚠️  No agents found")
            
            # Check calls
            calls = TwilioCall.objects.all()
            print(f"✅ TwilioCall model accessible")
            print(f"   Total calls: {calls.count()}")
            
            if calls.exists():
                recent_calls = calls.order_by('-created_at')[:3]
                for call in recent_calls:
                    print(f"   - {call.twilio_call_sid} ({call.status})")
            else:
                print("   ⚠️  No calls found")
            
            # Check users
            users = User.objects.all()
            print(f"✅ User model accessible")
            print(f"   Total users: {users.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main test function"""
    print("\n" + "🚀"*30)
    print("WEBSOCKET + TWILIO + HUME AI - INTEGRATION TEST")
    print("🚀"*30)
    
    tester = WebSocketTester()
    
    # Check database
    db_ok = tester.check_database_setup()
    
    # Test Twilio
    twilio_ok = await tester.test_twilio_config()
    
    # Test HumeAI
    hume_ok = await tester.test_hume_connection()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Database Setup:    {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Twilio Config:     {'✅ PASS' if twilio_ok else '❌ FAIL'}")
    print(f"HumeAI WebSocket:  {'✅ PASS' if hume_ok else '❌ FAIL'}")
    print("="*60)
    
    if db_ok and twilio_ok and hume_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ System is ready for live calls!")
        print("\n📞 To test a live call, use:")
        print("   python test_live_call.py --phone +1234567890")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
