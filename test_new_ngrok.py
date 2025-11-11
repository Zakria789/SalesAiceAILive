"""
🔍 TEST NEW NGROK URL
Verify the new ngrok tunnel is working
"""

import requests
import json

NGROK_URL = "https://roguishly-oncogenic-amiyah.ngrok-free.dev"

def test_ngrok():
    """Test ngrok URL"""
    print("\n" + "="*70)
    print("🧪 TESTING NEW NGROK URL")
    print("="*70)
    print(f"📍 URL: {NGROK_URL}")
    
    # Test endpoints
    endpoints = [
        "/api/hume-twilio/",
        "/api/hume-twilio/voice-webhook/",
        "/api/hume-twilio/status-callback/",
        "/api/accounts/",
    ]
    
    headers = {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "Mozilla/5.0"
    }
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{NGROK_URL}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            # Try POST for webhooks
            if 'webhook' in endpoint or 'callback' in endpoint:
                response = requests.post(url, headers=headers, timeout=10, data={'test': 'data'})
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            status = response.status_code
            
            if status == 200:
                print(f"✅ Status: {status} OK")
                results[endpoint] = True
            elif status == 405:
                print(f"✅ Status: {status} Method Not Allowed (endpoint exists!)")
                results[endpoint] = True
            elif status == 403:
                print(f"✅ Status: {status} Forbidden (endpoint exists, auth required)")
                results[endpoint] = True
            elif status == 400:
                print(f"⚠️  Status: {status} Bad Request (endpoint exists)")
                results[endpoint] = True
            else:
                print(f"⚠️  Status: {status}")
                results[endpoint] = False
                
            # Show response preview
            content = response.text[:200]
            if content:
                print(f"   Response: {content}...")
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout")
            results[endpoint] = False
        except Exception as e:
            print(f"❌ Error: {e}")
            results[endpoint] = False
    
    # WebSocket info
    print(f"\n{'='*70}")
    print("🔌 WEBSOCKET ENDPOINTS")
    print(f"{'='*70}")
    
    ws_url = NGROK_URL.replace('https://', 'wss://')
    
    print(f"📍 Main Route:")
    print(f"   {ws_url}/ws/hume-twilio/stream/<CALL_SID>/")
    print(f"\n📍 Alternative Route:")
    print(f"   {ws_url}/api/hume-twilio/stream/<CALL_SID>/")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST RESULTS")
    print(f"{'='*70}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for endpoint, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {endpoint}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} endpoints accessible")
    print(f"{'='*70}")
    
    if passed > 0:
        print("\n✅ NGROK IS WORKING!")
        print("\n🎯 Next Steps:")
        print(f"1. Update .env file:")
        print(f"   BASE_URL={NGROK_URL}")
        print(f"\n2. Update Twilio webhook URL:")
        print(f"   {NGROK_URL}/api/hume-twilio/voice-webhook/")
        print(f"\n3. Test live call:")
        print(f"   python test_live_call.py --phone +1234567890")
    else:
        print("\n❌ NGROK NOT ACCESSIBLE")
        print("Check:")
        print("1. Is ngrok running?")
        print("2. Is Django server on port 8002?")
        print("3. Is ngrok pointing to 8002?")
    
    return passed > 0

if __name__ == "__main__":
    try:
        test_ngrok()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
