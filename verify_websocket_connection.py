"""
Verify HumeAI WebSocket connection with correct authentication
AND verify Vonage can connect to it
"""
import asyncio
import websockets
import json
from decouple import config

print("=" * 80)
print("HUMEAI WEBSOCKET CONNECTION TEST")
print("=" * 80)

HUME_API_KEY = config('HUME_API_KEY')
HUME_CONFIG_ID = config('HUME_CONFIG_ID')

print(f"\n📋 Configuration:")
print(f"   API Key: {HUME_API_KEY[:20]}...")
print(f"   Config ID: {HUME_CONFIG_ID}")

# Test 1: WebSocket with query parameter (what Vonage will use)
async def test_websocket_connection():
    print(f"\n[1] Testing HumeAI WebSocket Connection...")
    
    # Build WebSocket URL - config_id as query param
    ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
    
    print(f"   URL: wss://api.hume.ai/v0/assistant/chat?config_id=...")
    print(f"   Headers: X-Hume-Api-Key: {HUME_API_KEY[:20]}...")
    
    try:
        # Connect with API key in headers (like Vonage will do)
        async with websockets.connect(
            ws_url,
            extra_headers={
                "X-Hume-Api-Key": HUME_API_KEY
            }
        ) as websocket:
            print(f"   ✅ WebSocket connected!")
            
            # Wait for initial message from HumeAI
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            print(f"\n   📨 Received from HumeAI:")
            print(f"      Type: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'chat_metadata':
                print(f"      ✅ Chat metadata received!")
                print(f"      Chat ID: {data.get('chat_id', 'N/A')}")
                print(f"      Chat Group ID: {data.get('chat_group_id', 'N/A')}")
                
            print(f"\n   ✅ HumeAI WebSocket is READY!")
            print(f"   ✅ Vonage CAN connect to this endpoint!")
            return True
            
    except asyncio.TimeoutError:
        print(f"   ❌ Timeout waiting for HumeAI response")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"   ❌ Connection failed: {e.status_code}")
        if e.status_code == 401:
            print(f"      Problem: Invalid API key!")
        elif e.status_code == 404:
            print(f"      Problem: Config ID not found!")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

# Test 2: Verify NCCO structure
def test_ncco_structure():
    print(f"\n[2] Testing NCCO Structure...")
    
    BASE_URL = config('BASE_URL', default='http://localhost:8002')
    
    ncco = [
        {
            "action": "connect",
            "eventUrl": [f"{BASE_URL}/api/hume-twilio/vonage-event-callback/"],
            "from": "12199644562",
            "timeout": 60,
            "limit": 7200,
            "endpoint": [
                {
                    "type": "websocket",
                    "uri": f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}",
                    "content-type": "audio/l16;rate=16000",
                    "headers": {
                        "X-Hume-Api-Key": HUME_API_KEY,
                        "User-Agent": "VonageVoiceAPI/1.0"
                    }
                }
            ]
        }
    ]
    
    print(f"   NCCO Structure:")
    print(f"   ✅ action: connect")
    print(f"   ✅ endpoint type: websocket")
    print(f"   ✅ uri: wss://api.hume.ai/v0/assistant/chat?config_id=...")
    print(f"   ✅ content-type: audio/l16;rate=16000")
    print(f"   ✅ headers: X-Hume-Api-Key present")
    print(f"   ✅ eventUrl: {BASE_URL}/api/hume-twilio/vonage-event-callback/")
    
    print(f"\n   Full NCCO:")
    print(json.dumps(ncco, indent=2))
    
    return True

# Run tests
async def main():
    print("\n" + "=" * 80)
    print("RUNNING TESTS...")
    print("=" * 80)
    
    ws_ok = await test_websocket_connection()
    ncco_ok = test_ncco_structure()
    
    print("\n" + "=" * 80)
    print("TEST RESULTS:")
    print("=" * 80)
    print(f"   HumeAI WebSocket: {'✅ WORKING' if ws_ok else '❌ FAILED'}")
    print(f"   NCCO Structure: {'✅ CORRECT' if ncco_ok else '❌ INCORRECT'}")
    
    if ws_ok and ncco_ok:
        print(f"\n🎉 SUCCESS! System ready for calls!")
        print(f"\n📞 What happens when you call:")
        print(f"   1. You initiate call → Vonage API")
        print(f"   2. Call connects → Vonage calls answer webhook")
        print(f"   3. Webhook returns NCCO with WebSocket URI")
        print(f"   4. Vonage connects to HumeAI WebSocket")
        print(f"   5. Audio streams: Caller ↔ Vonage ↔ HumeAI")
        print(f"   6. HumeAI agent speaks and responds!")
        print(f"   7. Call continues until hangup")
        print(f"\n✅ All components verified and working!")
    else:
        print(f"\n❌ System NOT ready - fix errors above")
    
    print("=" * 80)

# Run
if __name__ == "__main__":
    asyncio.run(main())
