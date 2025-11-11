"""
Test WebSocket and HumeAI connectivity independently
"""
import asyncio
import websockets
import json
from decouple import config

print("=" * 80)
print("🧪 TESTING WEBSOCKET & HUMEAI CONNECTIVITY")
print("=" * 80)

# Load credentials
HUME_API_KEY = config('HUME_API_KEY', default='')
HUME_SECRET_KEY = config('HUME_SECRET_KEY', default='')
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
BASE_URL = config('BASE_URL', default='')

print(f"\n📋 Configuration:")
print(f"   API Key: {HUME_API_KEY[:20]}..." if HUME_API_KEY else "   ❌ API Key missing")
print(f"   Secret: {HUME_SECRET_KEY[:20]}..." if HUME_SECRET_KEY else "   ❌ Secret missing")
print(f"   Config ID: {HUME_CONFIG_ID}")
print(f"   Base URL: {BASE_URL}")

# Test 1: HumeAI Connection
async def test_hume_connection():
    """Test direct connection to HumeAI EVI API"""
    print("\n" + "=" * 80)
    print("TEST 1: HUMEAI EVI API CONNECTION")
    print("=" * 80)
    
    try:
        # Try the endpoint we're using in code
        hume_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
        
        print(f"\n🔌 Attempting to connect to HumeAI...")
        print(f"   URL: {hume_url}")
        
        headers = {
            'X-Hume-Api-Key': HUME_API_KEY,
            'Content-Type': 'application/json'
        }
        
        print(f"   Headers: X-Hume-Api-Key: {HUME_API_KEY[:20]}...")
        
        # Try connection with timeout
        print(f"\n⏳ Connecting (10s timeout)...")
        
        async with websockets.connect(
            hume_url, 
            extra_headers=headers,
            ping_interval=20,
            ping_timeout=20
        ) as ws:
            print(f"✅ SUCCESS! HumeAI WebSocket connected!")
            print(f"   Connection state: {ws.state.name}")
            
            # Try sending initial config
            session_config = {
                "type": "session_settings",
                "config_id": HUME_CONFIG_ID,
                "audio": {
                    "encoding": "linear16",
                    "channels": 1,
                    "sample_rate": 8000
                }
            }
            
            print(f"\n📤 Sending session config...")
            await ws.send(json.dumps(session_config))
            print(f"✅ Config sent successfully!")
            
            # Try to receive response
            print(f"\n⏳ Waiting for HumeAI response (5s timeout)...")
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                print(f"✅ Received response from HumeAI!")
                response_data = json.loads(response)
                print(f"   Type: {response_data.get('type', 'unknown')}")
                print(f"   Full response: {json.dumps(response_data, indent=2)}")
            except asyncio.TimeoutError:
                print(f"⚠️  No response received (timeout)")
            
            print(f"\n🎉 HumeAI connection test PASSED!")
            return True
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n❌ HumeAI REJECTED connection!")
        print(f"   HTTP Status: {e.status_code}")
        print(f"   Headers: {e.headers}")
        
        if e.status_code == 404:
            print(f"\n💡 Possible issues:")
            print(f"   1. Wrong endpoint URL (trying v0/assistant/chat)")
            print(f"   2. Config ID invalid: {HUME_CONFIG_ID}")
            print(f"   3. API version changed (might need v1 or v2)")
        elif e.status_code == 401 or e.status_code == 403:
            print(f"\n💡 Authentication issue:")
            print(f"   1. API Key invalid")
            print(f"   2. Wrong authentication method")
        
        # Try alternative endpoints
        print(f"\n🔄 Trying alternative endpoints...")
        
        alternatives = [
            f"wss://api.hume.ai/v1/evi/chat?config_id={HUME_CONFIG_ID}",
            f"wss://api.hume.ai/v2/evi/chat?config_id={HUME_CONFIG_ID}",
            f"wss://api.hume.ai/evi/v0/chat?config_id={HUME_CONFIG_ID}",
        ]
        
        for alt_url in alternatives:
            try:
                print(f"\n   Trying: {alt_url[:60]}...")
                async with websockets.connect(alt_url, extra_headers=headers) as ws:
                    print(f"   ✅ SUCCESS with this endpoint!")
                    print(f"\n🎉 Working endpoint found: {alt_url}")
                    return True
            except Exception as alt_e:
                print(f"   ❌ Failed: {type(alt_e).__name__}")
        
        return False
        
    except asyncio.TimeoutError:
        print(f"\n❌ Connection TIMEOUT (10 seconds)")
        print(f"   Possible issues:")
        print(f"   1. Network/firewall blocking WebSocket")
        print(f"   2. HumeAI service down")
        print(f"   3. Internet connection issue")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection FAILED!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False


# Test 2: Django WebSocket Endpoint
async def test_django_websocket():
    """Test connection to Django WebSocket endpoint"""
    print("\n" + "=" * 80)
    print("TEST 2: DJANGO WEBSOCKET ENDPOINT")
    print("=" * 80)
    
    try:
        # Convert BASE_URL to WebSocket URL
        ws_base = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
        ws_url = f"{ws_base}/ws/hume-twilio/stream/TEST_CALL_SID/"
        
        print(f"\n🔌 Attempting to connect to Django WebSocket...")
        print(f"   URL: {ws_url}")
        
        # Try connection with timeout
        print(f"\n⏳ Connecting (5s timeout)...")
        
        async with websockets.connect(ws_url) as ws:
            print(f"✅ SUCCESS! Django WebSocket connected!")
            print(f"   Connection state: {ws.state.name}")
            
            # Send test message (simulating Twilio 'connected' event)
            test_message = {
                "event": "connected",
                "protocol": "Call",
                "version": "1.0.0"
            }
            
            print(f"\n📤 Sending test message...")
            await ws.send(json.dumps(test_message))
            print(f"✅ Message sent successfully!")
            
            print(f"\n🎉 Django WebSocket test PASSED!")
            return True
            
    except websockets.exceptions.InvalidHandshake as e:
        print(f"\n❌ WebSocket HANDSHAKE FAILED!")
        print(f"   Status: {e.status_code if hasattr(e, 'status_code') else 'unknown'}")
        print(f"   This usually means:")
        print(f"   1. Django server not running")
        print(f"   2. WebSocket route not registered")
        print(f"   3. ASGI not configured properly")
        return False
        
    except asyncio.TimeoutError:
        print(f"\n❌ Connection TIMEOUT")
        print(f"   Django server might not be running")
        return False
        
    except ConnectionRefusedError:
        print(f"\n❌ CONNECTION REFUSED!")
        print(f"   Django server is NOT running or wrong port")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection FAILED!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False


# Run tests
async def run_all_tests():
    """Run all connectivity tests"""
    print("\n" + "=" * 80)
    print("🚀 STARTING CONNECTIVITY TESTS")
    print("=" * 80)
    
    # Test 1: HumeAI
    hume_ok = await test_hume_connection()
    
    # Small delay
    await asyncio.sleep(2)
    
    # Test 2: Django WebSocket
    django_ok = await test_django_websocket()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    print(f"\nTest 1 - HumeAI EVI API:     {'✅ PASS' if hume_ok else '❌ FAIL'}")
    print(f"Test 2 - Django WebSocket:   {'✅ PASS' if django_ok else '❌ FAIL'}")
    
    print("\n" + "=" * 80)
    if hume_ok and django_ok:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR CALLS!")
    elif django_ok and not hume_ok:
        print("⚠️  Django OK but HumeAI needs fixing")
    elif hume_ok and not django_ok:
        print("⚠️  HumeAI OK but Django needs fixing")
    else:
        print("❌ BOTH TESTS FAILED - CHECK CONFIGURATION")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import websockets
        print("✅ websockets package found")
    except ImportError:
        print("❌ websockets package not found!")
        print("   Install with: pip install websockets")
        exit(1)
    
    # Run tests
    asyncio.run(run_all_tests())
