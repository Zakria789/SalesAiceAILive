"""
Test HumeAI WebSocket Connection
"""
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

HUME_API_KEY = os.getenv('HUME_API_KEY')
HUME_CONFIG_ID = "13624648-658a-49b1-81cb-a0f2e2b05de5"

print("=" * 80)
print("HUME AI WEBSOCKET CONNECTION TEST")
print("=" * 80)
print(f"\nConfig ID: {HUME_CONFIG_ID}")
print(f"API Key: {HUME_API_KEY[:20]}...{HUME_API_KEY[-10:]}")

async def test_hume_websocket():
    ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
    
    print(f"\n[*] Connecting to: {ws_url}")
    print(f"[*] Headers: X-Hume-Api-Key: {HUME_API_KEY[:10]}...")
    
    try:
        headers = {
            "X-Hume-Api-Key": HUME_API_KEY
        }
        
        async with websockets.connect(ws_url, extra_headers=headers) as websocket:
            print("\n✅ WebSocket Connected!")
            
            # Wait for initial message from HumeAI
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"\n[+] Received from HumeAI:")
                print(f"    Type: {data.get('type', 'unknown')}")
                if 'message' in data:
                    print(f"    Message: {data['message']}")
                print("\n✅ HumeAI WebSocket is WORKING!")
                return True
                
            except asyncio.TimeoutError:
                print("\n⚠️ No immediate response (might be normal)")
                print("✅ Connection established successfully!")
                return True
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ Connection Failed: {e}")
        print(f"   Status: {e.status_code}")
        if e.status_code == 401:
            print("   Issue: Invalid API Key or Config ID")
        elif e.status_code == 404:
            print("   Issue: Config ID not found")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        return False

print("\n" + "-" * 80)
print("Starting WebSocket test...")
print("-" * 80)

result = asyncio.run(test_hume_websocket())

print("\n" + "=" * 80)
if result:
    print("✅ HUME AI WEBSOCKET: WORKING")
else:
    print("❌ HUME AI WEBSOCKET: FAILED")
print("=" * 80)
