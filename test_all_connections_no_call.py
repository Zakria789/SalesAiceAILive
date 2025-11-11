"""
Test All Connections WITHOUT Making a Real Call
Tests: HumeAI WebSocket, Vonage API, NCCO Structure
"""
import asyncio
import websockets
import json
import requests
import jwt
import time
from datetime import datetime, timedelta

# Configuration
HUME_API_KEY = "mb5K22hbrOAvddJfkP4ZlScpMVHItgw0jfyxj0F1byGJ7j1w"
HUME_CONFIG_ID = "13624648-658a-49b1-81cb-a0f2e2b05de5"

VONAGE_API_KEY = "bab7bfbe"
VONAGE_API_SECRET = "m*Qbr^6I1wURy"
VONAGE_APP_ID = "0d75cbea-4319-434d-a864-f6f9ef83874d"
VONAGE_PRIVATE_KEY_PATH = "./private_key.pem"

print("=" * 80)
print("🧪 COMPREHENSIVE CONNECTION TEST (NO REAL CALL)")
print("=" * 80)

# ============================================================================
# TEST 1: HumeAI WebSocket with API Key in URL (NCCO Format)
# ============================================================================
async def test_hume_websocket_with_url_auth():
    """Test HumeAI WebSocket connection with API key in URL (Vonage NCCO format)"""
    print("\n" + "=" * 80)
    print("TEST 1: HumeAI WebSocket Connection (API Key in URL)")
    print("=" * 80)
    
    # Build WebSocket URL with API key as query parameter (NCCO format)
    ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}&api_key={HUME_API_KEY}"
    
    print(f"🔗 Connecting to: wss://api.hume.ai/v0/assistant/chat")
    print(f"   Config ID: {HUME_CONFIG_ID}")
    print(f"   API Key: {HUME_API_KEY[:20]}... (in URL)")
    print(f"   Full URL length: {len(ws_url)} characters")
    
    try:
        # Connect with 10 second timeout
        async with websockets.connect(
            ws_url,
            ping_interval=30,
            ping_timeout=10,
            close_timeout=10
        ) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Wait for initial message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received response: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'chat_metadata':
                    print("✅ HumeAI session established!")
                    print(f"   Chat ID: {data.get('chat_id', 'N/A')}")
                    print(f"   Chat Group ID: {data.get('chat_group_id', 'N/A')}")
                    return True
                else:
                    print(f"⚠️  Unexpected response type: {data.get('type')}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⚠️  No response received within 5 seconds")
                return False
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed: {e}")
        print(f"   Status code: {e.status_code}")
        if e.status_code == 401:
            print("   ERROR: Authentication failed - API key invalid or not accepted in URL")
        elif e.status_code == 400:
            print("   ERROR: Bad request - Check config_id or API key format")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# ============================================================================
# TEST 2: Vonage API Authentication
# ============================================================================
def test_vonage_authentication():
    """Test Vonage API authentication with JWT"""
    print("\n" + "=" * 80)
    print("TEST 2: Vonage API Authentication")
    print("=" * 80)
    
    try:
        # Load private key
        with open(VONAGE_PRIVATE_KEY_PATH, 'r') as f:
            private_key = f.read()
        
        print(f"✅ Private key loaded: {len(private_key)} bytes")
        
        # Generate JWT
        now = int(time.time())
        payload = {
            'application_id': VONAGE_APP_ID,
            'iat': now,
            'exp': now + 900,  # 15 minutes
            'jti': f"test-{now}"
        }
        
        token = jwt.encode(payload, private_key, algorithm='RS256')
        print(f"✅ JWT token generated: {token[:50]}...")
        
        # Test API call
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get application details
        url = f"https://api.nexmo.com/v2/applications/{VONAGE_APP_ID}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            app_data = response.json()
            print(f"✅ Vonage API authentication successful!")
            print(f"   Application: {app_data.get('name', 'N/A')}")
            print(f"   ID: {app_data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# ============================================================================
# TEST 3: NCCO Structure Validation (Fixed - No Headers)
# ============================================================================
def test_ncco_structure():
    """Validate NCCO structure matches Vonage specification"""
    print("\n" + "=" * 80)
    print("TEST 3: NCCO Structure Validation (Fixed Format)")
    print("=" * 80)
    
    # Build NCCO exactly as vonage_voice_bridge.py does (FIXED VERSION)
    BASE_URL = "https://uncontortioned-na-ponderously.ngrok-free.dev"
    hume_ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}&api_key={HUME_API_KEY}"
    
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
                    "uri": hume_ws_url,
                    "content-type": "audio/l16;rate=16000"
                }
            ]
        },
        {
            "action": "talk",
            "text": "Connecting you to our AI assistant. Please wait.",
            "bargeIn": True
        }
    ]
    
    print("📋 NCCO Structure:")
    print(json.dumps(ncco, indent=2))
    
    # Validate structure
    checks = {
        "Has connect action": ncco[0].get("action") == "connect",
        "Has talk action": ncco[1].get("action") == "talk",
        "Connect has endpoint": "endpoint" in ncco[0],
        "Endpoint is websocket": ncco[0]["endpoint"][0].get("type") == "websocket",
        "Has WebSocket URI": "uri" in ncco[0]["endpoint"][0],
        "Has content-type": "content-type" in ncco[0]["endpoint"][0],
        "NO headers field": "headers" not in ncco[0]["endpoint"][0],  # FIXED!
        "API key in URL": "api_key=" in ncco[0]["endpoint"][0]["uri"],
        "Config ID in URL": "config_id=" in ncco[0]["endpoint"][0]["uri"],
        "Has eventUrl": "eventUrl" in ncco[0],
        "Talk has text": "text" in ncco[1],
        "Talk has bargeIn": "bargeIn" in ncco[1]
    }
    
    print("\n✅ Validation Results:")
    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ NCCO structure is VALID!")
        print("   ✅ No 'headers' field (Vonage NCCO compliant)")
        print("   ✅ API key included in URL (Vonage requirement)")
    else:
        print("\n❌ NCCO structure has issues!")
    
    return all_passed

# ============================================================================
# TEST 4: Local Django Server Health Check
# ============================================================================
def test_django_health():
    """Test local Django server is running"""
    print("\n" + "=" * 80)
    print("TEST 4: Django Server Health Check")
    print("=" * 80)
    
    try:
        response = requests.get(
            "http://localhost:8002/api/hume-twilio/vonage-health/",
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Django server is running!")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ Server returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Django server: {str(e)}")
        return False

# ============================================================================
# RUN ALL TESTS
# ============================================================================
async def run_all_tests():
    results = {}
    
    # Test 1: HumeAI WebSocket (with API key in URL)
    results['hume_websocket'] = await test_hume_websocket_with_url_auth()
    
    # Test 2: Vonage Authentication
    results['vonage_auth'] = test_vonage_authentication()
    
    # Test 3: NCCO Structure
    results['ncco_structure'] = test_ncco_structure()
    
    # Test 4: Django Health
    results['django_health'] = test_django_health()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("✅ HumeAI WebSocket: Working (API key in URL)")
        print("✅ Vonage API: Authenticated")
        print("✅ NCCO Structure: Valid (No headers field)")
        print("✅ Django Server: Running")
        print("\n🚀 READY FOR REAL CALL TEST!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("=" * 80)
        print("Please review the failed tests above before making a call.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
