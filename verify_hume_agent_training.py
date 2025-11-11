"""
Comprehensive check to verify if HumeAI agent is trained and ready
"""
import os
import requests
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent
from django.conf import settings

print("=" * 80)
print("HUME AI AGENT TRAINING VERIFICATION")
print("=" * 80)

# 1. Check Database Configuration
print("\n[1] DATABASE CONFIGURATION")
print("-" * 80)

try:
    default_agent = HumeAgent.objects.filter(status='active').first()
    if default_agent:
        print(f"[+] Default Agent Found: {default_agent.name}")
        print(f"    Config ID: {default_agent.hume_config_id}")
        print(f"    Voice Model: {default_agent.voice_name}")
        print(f"    Status: {default_agent.status}")
        print(f"    System Prompt: {default_agent.system_prompt[:100]}...")
        print(f"    Greeting: {default_agent.greeting_message}")
        
        config_id = default_agent.hume_config_id
    else:
        print("[!] No active agent found in database")
        config_id = None
except Exception as e:
    print(f"[!] Error checking database: {e}")
    config_id = None

# 2. Check Environment Variables
print("\n[2] ENVIRONMENT VARIABLES")
print("-" * 80)

api_key = os.getenv('HUME_API_KEY')
secret_key = os.getenv('HUME_SECRET_KEY')

if api_key:
    print(f"[+] HUME_API_KEY: {api_key[:20]}...{api_key[-10:]}")
else:
    print("[!] HUME_API_KEY not set")

if secret_key:
    print(f"[+] HUME_SECRET_KEY: {secret_key[:20]}...{secret_key[-10:]}")
else:
    print("[!] HUME_SECRET_KEY not set")

# 3. Test HumeAI API Connection
print("\n[3] HUME AI API CONNECTION TEST")
print("-" * 80)

if api_key and config_id:
    try:
        # Test if we can access HumeAI API
        headers = {
            'X-Hume-Api-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Try to get config details (if endpoint exists)
        print(f"[*] Testing connection to HumeAI API...")
        print(f"[*] Config ID: {config_id}")
        
        # Note: HumeAI doesn't have a public REST API to check config status
        # We can only verify by testing WebSocket connection
        print("[*] Note: HumeAI doesn't provide REST API to check config status")
        print("[*] Only way to verify is through actual call test")
        
    except Exception as e:
        print(f"[!] Error testing API: {e}")
else:
    print("[!] Missing API key or config ID")

# 4. Check Recent Call Success
print("\n[4] RECENT CALL ANALYSIS")
print("-" * 80)

from HumeAiTwilio.models import TwilioCall

recent_calls = TwilioCall.objects.filter(
    provider='vonage',
    agent=default_agent
).order_by('-created_at')[:5]

if recent_calls:
    successful_calls = 0
    total_duration = 0
    calls_with_session = 0
    
    for call in recent_calls:
        if call.started_at and call.ended_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            total_duration += duration
            
            if duration > 3:
                successful_calls += 1
            
            if call.hume_session_id:
                calls_with_session += 1
    
    avg_duration = total_duration / len(recent_calls) if recent_calls else 0
    
    print(f"Total Calls: {len(recent_calls)}")
    print(f"Average Duration: {avg_duration:.2f} seconds")
    print(f"Calls > 3 seconds: {successful_calls}")
    print(f"Calls with HumeAI Session: {calls_with_session}")
    
    if calls_with_session == 0:
        print("\n[!] CRITICAL: No calls have HumeAI session ID")
        print("    This means the answer webhook is NOT being called by Vonage")
        print("    Possible causes:")
        print("    1. Server not running when call is made")
        print("    2. Ngrok URL not accessible")
        print("    3. Webhook URL misconfigured in Vonage")
    
    if avg_duration < 3:
        print("\n[!] WARNING: Average call duration very short")
        print("    This suggests agent is not speaking or connection failing")
else:
    print("[!] No recent calls found")

# 5. Check Vonage Webhook Configuration
print("\n[5] VONAGE WEBHOOK URLS")
print("-" * 80)

base_url = os.getenv('BASE_URL', 'https://uncontortioned-na-ponderously.ngrok-free.dev')
print(f"Base URL: {base_url}")
print(f"Answer Webhook: {base_url}/api/hume-twilio/vonage-outgoing-answer/")
print(f"Event Webhook: {base_url}/api/hume-twilio/vonage-event-callback/")

print("\n[*] Testing if ngrok URL is accessible...")
try:
    response = requests.get(f"{base_url}/", timeout=5)
    print(f"[+] Ngrok URL is accessible (Status: {response.status_code})")
except Exception as e:
    print(f"[!] Ngrok URL NOT accessible: {e}")
    print("    Make sure server is running!")

# 6. Final Verdict
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

if config_id and api_key:
    print("\n[?] AGENT CONFIGURATION: OK")
    print("    Config ID and API key are properly set")
    
    if calls_with_session > 0:
        print("\n[+] WEBHOOK INTEGRATION: WORKING")
        print("    Answer webhook is being called successfully")
    else:
        print("\n[!] WEBHOOK INTEGRATION: FAILING")
        print("    Answer webhook is NOT being called by Vonage")
        print("\n    ACTION REQUIRED:")
        print("    1. Make sure Django server is RUNNING before making call")
        print("    2. Verify ngrok URL is accessible")
        print("    3. Check Vonage application webhook configuration")
    
    if avg_duration > 5:
        print("\n[+] AGENT SPEAKING: LIKELY YES")
        print("    Calls lasting 5+ seconds suggest agent is working")
    elif avg_duration > 2:
        print("\n[?] AGENT SPEAKING: UNCERTAIN")
        print("    Short calls (2-5s) - might be connection issue")
    else:
        print("\n[!] AGENT SPEAKING: LIKELY NO")
        print("    Very short calls suggest agent is NOT speaking")
        print("\n    POSSIBLE CAUSES:")
        print("    1. HumeAI config not trained/published on platform")
        print("    2. Audio format incompatibility")
        print("    3. API key or config ID incorrect")
        print("    4. Webhook not being called (check above)")
        
    print("\n[*] TO VERIFY AGENT TRAINING STATUS:")
    print("    1. Login to: https://platform.hume.ai")
    print("    2. Go to: Voice AI > Configs")
    print(f"    3. Find config: {config_id}")
    print("    4. Check if status is 'Published' (not 'Draft')")
    print("    5. Verify voice model is assigned")
    print("    6. Check system prompt is configured")
else:
    print("\n[!] CONFIGURATION INCOMPLETE")
    print("    Missing config ID or API key")

print("\n" + "=" * 80)
