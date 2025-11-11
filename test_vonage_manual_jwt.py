"""
Test Vonage Voice API with manual JWT and raw requests
"""
import requests
import jwt
import time
from decouple import config

print("=" * 80)
print("🔍 TESTING VONAGE VOICE API WITH MANUAL JWT")
print("=" * 80)

# Load config
VONAGE_APPLICATION_ID = config('VONAGE_APPLICATION_ID', default='')
VONAGE_PRIVATE_KEY_PATH = config('VONAGE_PRIVATE_KEY_PATH', default='./private_key.pem')

print(f"\n[1] Loading private key...")
with open(VONAGE_PRIVATE_KEY_PATH, 'r') as f:
    private_key = f.read()
print(f"   ✅ Loaded: {len(private_key)} bytes")

print(f"\n[2] Creating JWT token...")
now = int(time.time())
payload = {
    'application_id': VONAGE_APPLICATION_ID,
    'iat': now,
    'exp': now + 900,
    'jti': f'test-{now}'
}

token = jwt.encode(payload, private_key, algorithm='RS256')
print(f"   ✅ JWT: {token[:60]}...")

print(f"\n[3] Making Voice API call with JWT...")
url = "https://api.nexmo.com/v1/calls"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "to": [{"type": "phone", "number": "923403471112"}],
    "from": {"type": "phone", "number": "12199644562"},
    "answer_url": ["https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-outgoing-answer/"]
}

try:
    response = requests.post(url, json=data, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    if response.status_code == 201:
        print(f"\n   ✅ CALL INITIATED SUCCESSFULLY!")
        result = response.json()
        print(f"   UUID: {result.get('uuid')}")
    else:
        print(f"\n   ❌ Failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
