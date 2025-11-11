"""
🔴 LIVE CALL TEST WITH REAL-TIME LOGGING
Make actual call and show all logs in terminal
- Twilio audio → text transcription
- HumeAI responses (text + audio)
- Real-time conversation flow
"""

import os
import sys
import django
import time
from datetime import datetime
from decouple import config

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import HumeAgent, TwilioCall, ConversationLog
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

User = get_user_model()

# Live Configuration (using ngrok)
NGROK_URL = config('BASE_URL', default='https://roguishly-oncogenic-amiyah.ngrok-free.dev')
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')

# Target phone number
TARGET_PHONE = '+923403471112'


class LiveCallTester:
    """Live call testing with real-time logs"""
    
    def __init__(self):
        self.call_sid = None
        self.db_call = None
        self.agent = None
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"🔴 {title}")
        print("="*70)
    
    def create_test_agent(self):
        """Create or get test agent"""
        self.print_header("CREATING AI AGENT")
        
        user = User.objects.first()
        if not user:
            print("❌ No user found! Create a user first.")
            return None
        
        agent, created = HumeAgent.objects.get_or_create(
            name="Live Test Agent - Pakistan Call",
            defaults={
                'description': 'AI agent for live call testing to Pakistan',
                'hume_config_id': HUME_CONFIG_ID,
                'voice_name': 'ITO',
                'language': 'en',
                'system_prompt': '''You are a friendly AI assistant testing a voice call system. 
                Be natural, conversational, and brief. 
                Ask the caller how they are doing and if they can hear you clearly.
                Keep responses short (2-3 sentences max).''',
                'greeting_message': 'Hello! This is an AI voice assistant calling to test the system. Can you hear me clearly? How are you doing today?',
                'status': 'active',
                'created_by': user
            }
        )
        
        if created:
            print(f"✅ Created new agent: {agent.name}")
        else:
            print(f"✅ Using existing agent: {agent.name} (ID: {agent.id})")
        
        print(f"   Voice: {agent.voice_name}")
        print(f"   Config ID: {agent.hume_config_id}")
        
        self.agent = agent
        return agent
    
    def initiate_call(self):
        """Initiate the live call"""
        self.print_header(f"INITIATING CALL TO {TARGET_PHONE}")
        
        print(f"📞 From: {TWILIO_PHONE_NUMBER}")
        print(f"📞 To: {TARGET_PHONE}")
        print(f"🌐 Webhook: {NGROK_URL}/api/hume-twilio/voice-webhook/")
        print(f"🔌 WebSocket: Will be created when call connects")
        
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Create TwiML with WebSocket stream
            response = VoiceResponse()
            
            # Initial greeting
            response.say(
                "Connecting you to the AI assistant. Please wait a moment.",
                voice='alice',
                language='en-US'
            )
            
            # Start WebSocket stream
            connect = Connect()
            # Use the live ngrok WebSocket URL
            ws_url = f"{NGROK_URL.replace('https://', 'wss://')}/ws/hume-twilio/stream/CALL_SID_PLACEHOLDER"
            stream = Stream(url=ws_url)
            connect.append(stream)
            response.append(connect)
            
            twiml = str(response)
            
            print(f"\n📝 Generated TwiML:")
            print(twiml)
            
            # Make the call using live ngrok URL
            print(f"\n🚀 Making call...")
            
            call = client.calls.create(
                to=TARGET_PHONE,
                from_=TWILIO_PHONE_NUMBER,
                url=f"{NGROK_URL}/api/hume-twilio/voice-webhook/",
                status_callback=f"{NGROK_URL}/api/hume-twilio/status-callback/",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST',
                method='POST'
            )
            
            self.call_sid = call.sid
            
            print(f"\n✅ Call initiated successfully!")
            print(f"   Call SID: {call.sid}")
            print(f"   Status: {call.status}")
            print(f"   Direction: {call.direction}")
            
            # Create database record
            self.db_call = TwilioCall.objects.create(
                agent=self.agent,
                call_sid=call.sid,
                to_number=TARGET_PHONE,
                from_number=TWILIO_PHONE_NUMBER,
                direction='outbound',
                status='initiated',
                customer_name='Test User - Pakistan'
            )
            
            print(f"✅ Database record created (ID: {self.db_call.id})")
            
            return call
            
        except Exception as e:
            print(f"\n❌ Failed to initiate call: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def monitor_call(self, initial_call):
        """Monitor call status in real-time"""
        self.print_header("MONITORING CALL - LIVE STATUS")
        
        print(f"📞 Call SID: {self.call_sid}")
        print(f"⏳ Waiting for call to be answered...")
        print(f"\n{'Time':<12} {'Status':<15} {'Duration':<10} {'Event'}")
        print("-" * 70)
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        last_status = initial_call.status
        start_time = time.time()
        
        # Monitor for up to 120 seconds
        for i in range(120):
            try:
                # Fetch current call status
                call = client.calls(self.call_sid).fetch()
                current_status = call.status
                elapsed = int(time.time() - start_time)
                
                # Print status update if changed
                if current_status != last_status:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    duration = call.duration or 0
                    
                    # Status emojis
                    status_icons = {
                        'queued': '⏳',
                        'ringing': '📞',
                        'in-progress': '🎤',
                        'answered': '✅',
                        'completed': '✔️',
                        'busy': '📵',
                        'failed': '❌',
                        'no-answer': '📭'
                    }
                    
                    icon = status_icons.get(current_status, '📌')
                    print(f"{timestamp:<12} {icon} {current_status:<13} {duration}s {' '*8} Status changed")
                    
                    last_status = current_status
                    
                    # Update database
                    if self.db_call:
                        self.db_call.status = current_status
                        self.db_call.save()
                
                # Break if call ended
                if current_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{timestamp:<12} 🏁 {'CALL ENDED':<13} {call.duration or 0}s")
                    break
                
                # Show progress every 5 seconds
                if i > 0 and i % 5 == 0 and current_status == 'in-progress':
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{timestamp:<12}    {current_status:<13} {elapsed}s {' '*8} Call in progress...")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️  Error monitoring: {e}")
                break
        
        # Final status
        try:
            final_call = client.calls(self.call_sid).fetch()
            print(f"\n" + "="*70)
            print(f"📊 FINAL CALL DETAILS")
            print(f"="*70)
            print(f"Status: {final_call.status}")
            print(f"Duration: {final_call.duration or 0} seconds")
            print(f"Price: {final_call.price or 'N/A'} {final_call.price_unit or ''}")
            print(f"Direction: {final_call.direction}")
            
            return final_call
            
        except Exception as e:
            print(f"⚠️  Could not fetch final status: {e}")
            return None
    
    def show_conversation_logs(self):
        """Show conversation logs from database"""
        self.print_header("CONVERSATION LOGS (Audio → Text)")
        
        if not self.db_call:
            print("⚠️  No call record found")
            return
        
        # Wait a bit for logs to be written
        time.sleep(2)
        
        try:
            logs = ConversationLog.objects.filter(call=self.db_call).order_by('timestamp')
            
            if not logs.exists():
                print("⚠️  No conversation logs found yet")
                print("   (Logs are written during the call in real-time)")
                return
            
            print(f"Found {logs.count()} conversation entries:\n")
            
            for log in logs:
                timestamp = log.timestamp.strftime("%H:%M:%S")
                speaker_icon = {
                    'user': '👤 USER',
                    'agent': '🤖 AI',
                    'system': '⚙️  SYSTEM'
                }.get(log.speaker, '📌 UNKNOWN')
                
                print(f"[{timestamp}] {speaker_icon}")
                print(f"  {log.message}")
                print()
            
        except Exception as e:
            print(f"❌ Error fetching logs: {e}")
            import traceback
            traceback.print_exc()
    
    def run_live_test(self):
        """Run complete live test"""
        print("\n" + "🔴"*35)
        print("LIVE CALL TEST - REAL-TIME LOGGING")
        print("Target: +923403471112 (Pakistan)")
        print("Using: Live Ngrok URL + WebSocket + HumeAI")
        print("🔴"*35)
        
        # Step 1: Create agent
        if not self.create_test_agent():
            return
        
        # Step 2: Confirm
        print("\n" + "="*70)
        print("⚠️  WARNING: This will make a REAL phone call!")
        print("="*70)
        print(f"To: {TARGET_PHONE}")
        print(f"From: {TWILIO_PHONE_NUMBER}")
        print(f"Cost: ~$0.02-0.05 per minute (Pakistan)")
        print(f"\nLive URLs:")
        print(f"  Webhook: {NGROK_URL}/api/hume-twilio/voice-webhook/")
        print(f"  WebSocket: {NGROK_URL.replace('https://', 'wss://')}/ws/hume-twilio/stream/")
        
        confirm = input("\nProceed with LIVE call? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Call cancelled")
            return
        
        # Step 3: Make call
        call = self.initiate_call()
        if not call:
            return
        
        # Step 4: Monitor call
        final_call = self.monitor_call(call)
        
        # Step 5: Show logs
        self.show_conversation_logs()
        
        # Step 6: Summary
        print("\n" + "="*70)
        print("✅ LIVE TEST COMPLETED")
        print("="*70)
        
        if final_call:
            print(f"Call Status: {final_call.status}")
            print(f"Duration: {final_call.duration or 0} seconds")
        
        print(f"\nTo view full logs:")
        print(f"  python manage.py shell")
        print(f"  >>> from HumeAiTwilio.models import TwilioCall")
        print(f"  >>> call = TwilioCall.objects.get(twilio_call_sid='{self.call_sid}')")
        print(f"  >>> for log in call.conversation_logs.all():")
        print(f"  >>>     print(f'{{log.speaker}}: {{log.message}}')")
        
        print(f"\n🌐 Live URLs used:")
        print(f"  Ngrok: {NGROK_URL}")
        print(f"  WebSocket: {NGROK_URL.replace('https://', 'wss://')}/ws/hume-twilio/stream/{self.call_sid}/")
        
        print("\n" + "="*70)


def main():
    """Main function"""
    print("\n" + "🔴 LIVE CALL SYSTEM - REAL-TIME TEST")
    print("="*70)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Phone: {TARGET_PHONE}")
    print(f"Using Live Ngrok: {NGROK_URL}")
    print("="*70)
    
    tester = LiveCallTester()
    
    try:
        tester.run_live_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
