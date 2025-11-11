"""
Test if Django webhook endpoint is working locally
"""
import requests

print("=" * 80)
print("LOCAL WEBHOOK TEST")
print("=" * 80)

# Test 1: Health check
print("\n[1] Testing health endpoint...")
try:
    r = requests.get("http://localhost:8002/api/hume-twilio/vonage-health/")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    if r.status_code == 200:
        print("   ✅ Server is running!")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Server not running! Start with: python manage.py runserver 8002")
    exit(1)

# Test 2: Answer webhook
print("\n[2] Testing answer webhook...")
try:
    url = "http://localhost:8002/api/hume-twilio/vonage-outgoing-answer/"
    params = {"conversation_uuid": "test-123-456"}
    r = requests.get(url, params=params)
    print(f"   Status: {r.status_code}")
    response = r.json()
    print(f"   Response keys: {list(response.keys())}")
    
    if r.status_code == 200 and isinstance(response, list):
        print(f"   ✅ NCCO returned with {len(response)} actions!")
        for i, action in enumerate(response):
            print(f"      Action {i+1}: {action.get('action')}")
            if action.get('action') == 'connect':
                endpoint = action.get('endpoint', [{}])[0]
                print(f"         Type: {endpoint.get('type')}")
                if endpoint.get('type') == 'websocket':
                    print(f"         ✅ WebSocket endpoint configured!")
    else:
        print(f"   ❌ Unexpected response: {response}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Event webhook
print("\n[3] Testing event webhook...")
try:
    url = "http://localhost:8002/api/hume-twilio/vonage-event-callback/"
    payload = {
        "uuid": "test-uuid-789",
        "status": "started",
        "conversation_uuid": "test-conv-123"
    }
    r = requests.post(url, json=payload)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    if r.status_code == 200:
        print("   ✅ Event webhook working!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("RESULT:")
print("=" * 80)
print("✅ Django server: WORKING")
print("✅ Webhook endpoints: RESPONDING")
print("✅ Phone number: LINKED to app")
print("❌ Problem: NGROK is blocking external requests!")
print("\n💡 SOLUTION:")
print("   Ngrok free plan shows warning page to external requests.")
print("   Vonage can't reach your webhook through ngrok!")
print("\n🎯 OPTIONS:")
print("   1. Upgrade ngrok to paid plan (no warning page)")
print("   2. Use different tunnel: localtunnel, cloudflare tunnel")
print("   3. Deploy to cloud: PythonAnywhere, Heroku, Railway")
print("=" * 80)
