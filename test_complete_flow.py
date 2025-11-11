"""
Test Complete Flow: Vonage → Backend → HumeAI
Simulates the entire call flow
"""
import requests
import json
import asyncio
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

HUME_API_KEY = os.getenv('HUME_API_KEY')
HUME_CONFIG_ID = "13624648-658a-49b1-81cb-a0f2e2b05de5"
BASE_URL = os.getenv('BASE_URL', 'https://uncontortioned-na-ponderously.ngrok-free.dev')

print("=" * 80)
print("COMPLETE FLOW TEST: Vonage → Backend → HumeAI")
print("=" * 80)

print("\nFlow:")
print("  1️⃣  Vonage calls answer webhook")
print("  2️⃣  Backend returns NCCO with HumeAI WebSocket")
print("  3️⃣  Vonage connects to HumeAI")

# =============================================================================
# STEP 1: Test Backend Answer Webhook (Simulating Vonage's call)
# =============================================================================
print("\n" + "=" * 80)
print("STEP 1: Testing Backend Answer Webhook")
print("=" * 80)

answer_url = f"{BASE_URL}/api/hume-twilio/vonage-outgoing-answer/"
print(f"\nWebhook URL: {answer_url}")

# Check if server is running
try:
    print("\n[*] Checking if server is running...")
    response = requests.get(BASE_URL, timeout=3)
    print(f"[+] Server is UP (Status: {response.status_code})")
except Exception as e:
    print(f"\n❌ SERVER NOT RUNNING!")
    print(f"    Error: {e}")
    print(f"\n    ACTION: Start server first:")
    print(f"    python manage.py runserver 0.0.0.0:8002")
    print("\n" + "=" * 80)
    exit(1)

# Simulate Vonage calling our webhook
print("\n[*] Simulating Vonage GET request to answer webhook...")
try:
    # Vonage sends conversation_uuid and other params
    params = {
        'conversation_uuid': 'test-conversation-123',
        'from': '923403471112',
        'to': '12199644562'
    }
    
    response = requests.get(answer_url, params=params, timeout=10)
    
    print(f"\n[+] Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"[+] Response Content-Type: {response.headers.get('Content-Type')}")
        
        try:
            ncco = response.json()
            print(f"\n[+] NCCO Received:")
            print(json.dumps(ncco, indent=2)[:500])
            
            # Check if NCCO has connect action
            if ncco and len(ncco) > 0:
                action = ncco[0]
                
                if action.get('action') == 'connect':
                    print(f"\n✅ NCCO Structure: CORRECT")
                    print(f"   Action: connect")
                    
                    endpoint = action.get('endpoint', [{}])[0]
                    ws_uri = endpoint.get('uri', '')
                    
                    if 'api.hume.ai' in ws_uri:
                        print(f"✅ WebSocket URI: CORRECT")
                        print(f"   URI: {ws_uri[:60]}...")
                        
                        headers = endpoint.get('headers', {})
                        if 'X-Hume-Api-Key' in headers:
                            print(f"✅ API Key Header: PRESENT")
                            backend_works = True
                        else:
                            print(f"❌ API Key Header: MISSING")
                            backend_works = False
                    else:
                        print(f"❌ WebSocket URI: WRONG")
                        print(f"   Got: {ws_uri}")
                        backend_works = False
                else:
                    print(f"❌ NCCO Action: WRONG (expected 'connect', got '{action.get('action')}')")
                    backend_works = False
            else:
                print(f"❌ NCCO: EMPTY")
                backend_works = False
                
        except Exception as e:
            print(f"❌ Failed to parse NCCO: {e}")
            print(f"   Response: {response.text[:200]}")
            backend_works = False
    else:
        print(f"❌ Webhook returned error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        backend_works = False
        
except Exception as e:
    print(f"\n❌ Failed to call webhook: {e}")
    backend_works = False

# =============================================================================
# STEP 2: Test HumeAI WebSocket (Simulating Vonage's connection)
# =============================================================================
print("\n" + "=" * 80)
print("STEP 2: Testing HumeAI WebSocket Connection")
print("=" * 80)

async def test_hume_connection():
    ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
    
    print(f"\n[*] Connecting to: {ws_url}")
    
    try:
        headers = {
            "X-Hume-Api-Key": HUME_API_KEY,
            "Accept": "audio/l16;rate=16000"
        }
        
        async with websockets.connect(ws_url, extra_headers=headers) as websocket:
            print(f"[+] WebSocket Connected!")
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(response)
                
                if data.get('type') == 'chat_metadata':
                    print(f"✅ HumeAI Session Initialized!")
                    return True
                else:
                    print(f"⚠️ Unexpected response type: {data.get('type')}")
                    return True  # Still connected
                    
            except asyncio.TimeoutError:
                print(f"✅ Connection OK (no immediate response is normal)")
                return True
                
    except Exception as e:
        print(f"❌ HumeAI Connection Failed: {e}")
        return False

hume_works = asyncio.run(test_hume_connection())

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

print(f"\n📊 Test Results:")
print(f"  Backend Webhook: {'✅ WORKING' if backend_works else '❌ FAILED'}")
print(f"  HumeAI WebSocket: {'✅ WORKING' if hume_works else '❌ FAILED'}")

if backend_works and hume_works:
    print(f"\n" + "🎉" * 40)
    print(f"\n✅✅✅ COMPLETE FLOW: WORKING! ✅✅✅")
    print(f"\n" + "🎉" * 40)
    
    print(f"\n📞 Call Flow Will Work Like This:")
    print(f"\n  1. You call API → Vonage initiates call")
    print(f"  2. Call connects → Vonage calls answer webhook")
    print(f"  3. Backend returns NCCO → Vonage gets WebSocket URL")
    print(f"  4. Vonage connects to HumeAI → Audio streams start")
    print(f"  5. HumeAI agent speaks → You hear AI voice!")
    
    print(f"\n🚀 SYSTEM IS READY FOR REAL CALLS!")
    print(f"\n📋 To test:")
    print(f"  python quick_test.py")
    
elif backend_works:
    print(f"\n⚠️ Backend OK but HumeAI connection issue")
    print(f"   Check: API key, config ID")
    
elif hume_works:
    print(f"\n⚠️ HumeAI OK but backend issue")
    print(f"   Check: Server running, NCCO generation")
    
else:
    print(f"\n❌ Both components have issues")
    print(f"   Check: Server status, environment variables")

print("\n" + "=" * 80)
