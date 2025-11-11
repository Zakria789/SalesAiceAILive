import os
import django
import time
from datetime import datetime
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from twilio.rest import Client
from HumeAiTwilio.models import TwilioCall, ConversationLog

# Twilio credentials from .env
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = config('TWILIO_PHONE_NUMBER')

# Target number
TARGET_NUMBER = "+923403471112"

print("=" * 80)
print("🎯 HUME AI + TWILIO LIVE CALL TEST")
print("=" * 80)
print(f"📞 From: {TWILIO_PHONE}")
print(f"📱 To: {TARGET_NUMBER}")
print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Make the call
print("\n🚀 Initiating call...")
call = client.calls.create(
    to=TARGET_NUMBER,
    from_=TWILIO_PHONE,
    url="https://uncontortioned-na-ponderously.ngrok-free.dev/hume-ai-twilio/voice/",
    status_callback="https://uncontortioned-na-ponderously.ngrok-free.dev/hume-ai-twilio/status/",
    status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
    status_callback_method='POST'
)

print(f"✅ Call initiated!")
print(f"📋 Call SID: {call.sid}")
print(f"📊 Status: {call.status}")

print("\n" + "=" * 80)
print("📊 REAL-TIME CALL STATUS MONITORING")
print("=" * 80)

# Monitor call status for 30 seconds
for i in range(30):
    time.sleep(1)
    
    # Fetch latest call status
    call_status = client.calls(call.sid).fetch()
    
    # Check database for call record
    try:
        db_call = TwilioCall.objects.filter(call_sid=call.sid).first()
        if db_call:
            print(f"\n[{i+1}s] 📞 Call Status: {call_status.status.upper()}")
            print(f"       ⏱️  Duration: {call_status.duration or 0} seconds")
            print(f"       🗄️  DB Status: {db_call.status}")
            print(f"       🤖 Agent: {db_call.agent.name if db_call.agent else 'N/A'}")
            
            # Check for conversation logs
            conv_logs = ConversationLog.objects.filter(call=db_call).order_by('-timestamp')
            if conv_logs.exists():
                print(f"       💬 Conversation Logs: {conv_logs.count()}")
                print("\n       📝 Latest Messages:")
                for log in conv_logs[:3]:
                    speaker = "🎤 USER" if log.speaker == 'user' else "🤖 AI"
                    print(f"          {speaker}: {log.text[:60]}...")
            else:
                print(f"       💬 Conversation Logs: 0 (waiting...)")
        else:
            print(f"\n[{i+1}s] 📞 Call Status: {call_status.status.upper()}")
            print(f"       ⏱️  Duration: {call_status.duration or 0} seconds")
            print(f"       🗄️  DB: Not found yet...")
    except Exception as e:
        print(f"\n[{i+1}s] 📞 Call Status: {call_status.status.upper()}")
        print(f"       ⚠️  Error: {str(e)}")
    
    # Stop if call completed
    if call_status.status in ['completed', 'failed', 'busy', 'no-answer']:
        print(f"\n{'=' * 80}")
        print(f"🏁 Call ended with status: {call_status.status.upper()}")
        break

print("\n" + "=" * 80)
print("📊 FINAL CALL SUMMARY")
print("=" * 80)

# Final database check
try:
    db_call = TwilioCall.objects.filter(call_sid=call.sid).first()
    if db_call:
        print(f"✅ Call Record Found in Database")
        print(f"   📋 Call SID: {db_call.call_sid}")
        print(f"   📊 Status: {db_call.status}")
        print(f"   ⏱️  Duration: {db_call.duration or 0} seconds")
        print(f"   🤖 Agent: {db_call.agent.name if db_call.agent else 'N/A'}")
        print(f"   📅 Time: {db_call.timestamp}")
        
        # Conversation logs
        conv_logs = ConversationLog.objects.filter(call=db_call).order_by('timestamp')
        print(f"\n💬 Total Conversation Logs: {conv_logs.count()}")
        
        if conv_logs.exists():
            print("\n📝 FULL CONVERSATION TRANSCRIPT:")
            print("-" * 80)
            for log in conv_logs:
                speaker = "👤 USER" if log.speaker == 'user' else "🤖 AI"
                print(f"\n{speaker} [{log.timestamp.strftime('%H:%M:%S')}]")
                print(f"   Audio→Text: {log.text}")
                if log.emotion:
                    print(f"   Emotion: {log.emotion}")
            print("-" * 80)
        else:
            print("\n⚠️  No conversation logs found!")
            print("   This means either:")
            print("   - HumeAI connection failed")
            print("   - No speech was detected")
            print("   - Audio streaming issue")
    else:
        print("❌ No call record found in database!")
except Exception as e:
    print(f"❌ Error checking database: {str(e)}")

print("\n" + "=" * 80)
print("🎯 TEST COMPLETE")
print("=" * 80)
print("\n💡 TIP: Check your Django server logs for detailed WebSocket activity!")
print("   Look for:")
print("   - ✅ HumeAI WebSocket connected successfully!")
print("   - ❌ HumeAI rejected connection: HTTP 404")
print("   - 🎤 User said: [transcription]")
print("   - 🤖 AI said: [response]")
