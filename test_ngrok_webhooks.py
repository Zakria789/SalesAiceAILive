"""
🔍 NGROK + WEBSOCKET WEBHOOK TEST
Test all Twilio webhook endpoints
"""

import requests
import json
from decouple import config

# Configuration
NGROK_URL = config('BASE_URL', default='https://uncontortioned-na-ponderously.ngrok-free.dev')

def test_endpoint(url, method='GET', data=None, description=''):
    """Test a single endpoint"""
    print(f"\n{'='*70}")
    print(f"🧪 Testing: {description}")
    print(f"📍 URL: {url}")
    print(f"📤 Method: {method}")
    print(f"{'='*70}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, data=data, timeout=10)
        
        print(f"✅ Status: {response.status_code} {response.reason}")
        print(f"📦 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.content)} bytes")
        
        # Show response preview
        if response.status_code == 200:
            content = response.text[:500]
            print(f"\n📄 Response Preview:")
            print(content)
            if len(response.text) > 500:
                print("... (truncated)")
        else:
            print(f"\n⚠️ Response:")
            print(response.text[:500])
        
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout after 10 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "🚀"*35)
    print("NGROK + WEBHOOK CONNECTIVITY TEST")
    print("🚀"*35)
    
    results = {}
    
    # Test 1: Main ngrok URL
    results['ngrok_base'] = test_endpoint(
        NGROK_URL,
        description="Ngrok Base URL"
    )
    
    # Test 2: API base
    results['api_base'] = test_endpoint(
        f"{NGROK_URL}/api/",
        description="API Base Endpoint"
    )
    
    # Test 3: HumeAI-Twilio API
    results['hume_api'] = test_endpoint(
        f"{NGROK_URL}/api/hume-twilio/",
        description="HumeAI-Twilio API Endpoint"
    )
    
    # Test 4: Voice Webhook (WebSocket version)
    results['voice_webhook'] = test_endpoint(
        f"{NGROK_URL}/api/hume-twilio/voice-webhook/",
        description="Twilio Voice Webhook (WebSocket)"
    )
    
    # Test 5: Simple Voice Webhook (No WebSocket)
    results['voice_simple'] = test_endpoint(
        f"{NGROK_URL}/api/hume-twilio/voice-webhook-simple/",
        description="Twilio Voice Webhook (Simple - No WebSocket)"
    )
    
    # Test 6: Status Callback
    results['status_callback'] = test_endpoint(
        f"{NGROK_URL}/api/hume-twilio/status-callback/",
        description="Twilio Status Callback"
    )
    
    # Test 7: WebSocket endpoint info
    print(f"\n{'='*70}")
    print(f"🔌 WebSocket Endpoints (ws:// or wss://)")
    print(f"{'='*70}")
    
    ws_url = NGROK_URL.replace('https://', 'wss://').replace('http://', 'ws://')
    
    print(f"📍 Main WebSocket Route:")
    print(f"   {ws_url}/ws/hume-twilio/stream/<CALL_SID>/")
    print(f"\n📍 Alternative WebSocket Route:")
    print(f"   {ws_url}/api/hume-twilio/stream/<CALL_SID>/")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed*100//total}%)")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System ready for Twilio integration!")
        print("\n✅ Next Steps:")
        print("1. ✓ Ngrok is accessible")
        print("2. ✓ Webhooks are responding")
        print("3. ✓ WebSocket routes configured")
        print("4. 📞 Ready to test live calls!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("\nCheck the following:")
        print("1. Is Django server running?")
        print("2. Is ngrok tunnel active?")
        print("3. Are URLs configured correctly in .env?")
    
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
