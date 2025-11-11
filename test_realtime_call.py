"""
Complete Real-Time Call Test with Monitoring
Tests: WebSocket routes → Call initiation → Live monitoring
"""
import requests
import json
import time
import asyncio
import websockets
from datetime import datetime

# Configuration
BASE_URL = "https://uncontortioned-na-ponderously.ngrok-free.dev"
PHONE_NUMBER = "+923403471112"
AGENT_ID = "1"

def print_step(step, message):
    """Print formatted step"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] 🔹 STEP {step}: {message}")
    print("=" * 70)

def test_server_health():
    """Test if server is running"""
    print_step(1, "Testing Server Health")
    try:
        response = requests.get(
            f"{BASE_URL}/api/hume-twilio/health/",
            headers={"ngrok-skip-browser-warning": "true"}
        )
        if response.status_code == 200:
            print("✅ Server is RUNNING")
            return True
        else:
            print(f"⚠️  Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

async def test_websocket_route():
    """Test if WebSocket route is accessible"""
    print_step(2, "Testing WebSocket Route")
    test_uuid = "TEST-ROUTE-CHECK"
    ws_url = f"wss://uncontortioned-na-ponderously.ngrok-free.dev/api/vonage-stream/{test_uuid}/"
    
    try:
        print(f"📡 Connecting to: {ws_url}")
        async with websockets.connect(ws_url) as ws:
            print("✅ WebSocket route is ACCESSIBLE")
            print(f"   State: {ws.open}")
            await ws.close()
            return True
    except Exception as e:
        print(f"❌ WebSocket route failed: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False

def initiate_call():
    """Initiate Vonage call with real-time WebSocket"""
    print_step(3, "Initiating Real-Time Call")
    
    url = f"{BASE_URL}/api/hume-twilio/initiate-call/"
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    payload = {
        "phone_no": PHONE_NUMBER,
        "agent_id": AGENT_ID
    }
    
    print(f"📞 Calling: {PHONE_NUMBER}")
    print(f"🤖 Agent ID: {AGENT_ID}")
    print(f"🌐 URL: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("✅ Call initiated successfully!")
            print(f"\n📋 Call Details:")
            print(json.dumps(data, indent=2))
            
            # Extract call UUID from response
            call_uuid = data.get('call', {}).get('call_sid')
            return call_uuid
        else:
            print(f"❌ Call initiation failed!")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error initiating call: {e}")
        return None

def monitor_call(call_uuid, duration=30):
    """Monitor call for specified duration"""
    if not call_uuid:
        print("\n⚠️  No call UUID to monitor")
        return
    
    print_step(4, f"Monitoring Call for {duration} seconds")
    print(f"📱 Call UUID: {call_uuid}")
    print(f"⏱️  Monitoring duration: {duration}s")
    print("\n🔍 Watch for:")
    print("   - 'stream started' event from Vonage")
    print("   - WebSocket connection in Django logs")
    print("   - HumeAI connection established")
    print("   - Audio streaming messages")
    
    print(f"\n⏳ Waiting {duration} seconds...")
    print("   (Check Django server logs in another terminal)")
    
    for i in range(duration):
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   ... {duration - i}s remaining")
    
    print("\n✅ Monitoring period complete!")

def main():
    """Main test flow"""
    print("\n" + "="*70)
    print("🚀 COMPLETE REAL-TIME CALL TEST")
    print("="*70)
    print(f"Target: {PHONE_NUMBER}")
    print(f"Expected: Bidirectional real-time audio with HumeAI")
    print("="*70)
    
    # Step 1: Server health
    if not test_server_health():
        print("\n❌ Server not running! Start Django server first.")
        return
    
    # Step 2: WebSocket route
    ws_result = asyncio.run(test_websocket_route())
    if not ws_result:
        print("\n⚠️  WebSocket route has issues, but continuing...")
    
    # Step 3: Initiate call
    call_uuid = initiate_call()
    
    if not call_uuid:
        print("\n❌ Call initiation failed! Check Django logs for errors.")
        return
    
    # Step 4: Monitor
    monitor_call(call_uuid, duration=30)
    
    # Final summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print("✅ Server: Running")
    print(f"{'✅' if ws_result else '⚠️ '} WebSocket: {'Accessible' if ws_result else 'Has issues'}")
    print(f"✅ Call: Initiated (UUID: {call_uuid})")
    print("\n💡 Next Steps:")
    print("   1. Check Django server logs for:")
    print("      - 'Vonage stream started' message")
    print("      - 'Connected to HumeAI' message")
    print("      - Audio streaming logs")
    print("   2. Check if call stayed connected (should be > 30s)")
    print("   3. Listen for AI voice response on phone")
    print("="*70)

if __name__ == "__main__":
    main()
