"""
Check Vonage Application Details via API
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
import requests
import jwt
import time

print("=" * 80)
print("VONAGE APPLICATION VERIFICATION")
print("=" * 80)

# Load credentials
api_key = config('VONAGE_API_KEY')
api_secret = config('VONAGE_API_SECRET')
app_id = config('VONAGE_APPLICATION_ID')
private_key_path = config('VONAGE_PRIVATE_KEY_PATH')

print(f"\n📋 Configuration:")
print(f"   API Key: {api_key}")
print(f"   Application ID: {app_id}")

# Load private key
with open(private_key_path, 'r') as f:
    private_key = f.read()

# Generate JWT
iat = int(time.time())
payload = {
    'application_id': app_id,
    'iat': iat,
    'exp': iat + 900,
    'jti': f"jwt-{iat}"
}

token = jwt.encode(payload, private_key, algorithm='RS256')
print(f"\n✅ JWT Generated")

# Check application details via API
print(f"\n🔍 Checking Application Details...")

try:
    # Get application info
    url = f"https://api.nexmo.com/v2/applications/{app_id}"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        app_data = response.json()
        print(f"\n✅ APPLICATION FOUND!")
        print(f"\n📱 Application Details:")
        print(f"   ID: {app_data.get('id')}")
        print(f"   Name: {app_data.get('name')}")
        
        # Check capabilities
        capabilities = app_data.get('capabilities', {})
        print(f"\n🔧 Capabilities:")
        for cap_name, cap_data in capabilities.items():
            print(f"   {cap_name.upper()}: {cap_data if cap_data else 'DISABLED'}")
        
        # Check voice webhooks
        voice = capabilities.get('voice', {})
        if voice:
            print(f"\n📞 Voice Configuration:")
            print(f"   Answer URL: {voice.get('webhooks', {}).get('answer_url', {}).get('address')}")
            print(f"   Event URL: {voice.get('webhooks', {}).get('event_url', {}).get('address')}")
        
    elif response.status_code == 401:
        print(f"\n❌ AUTHENTICATION FAILED!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print(f"\n⚠️ POSSIBLE ISSUES:")
        print(f"   1. Application ID is incorrect")
        print(f"   2. Private key doesn't match this application")
        print(f"   3. Application was deleted/recreated")
        print(f"\n💡 SOLUTION:")
        print(f"   Go to Vonage Dashboard → Applications")
        print(f"   Create NEW application or get correct APP_ID")
        print(f"   Download the private_key.pem again")
        
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test with basic auth (non-JWT) for account balance
print(f"\n" + "=" * 80)
print("ACCOUNT BALANCE CHECK (Basic Auth)")
print("=" * 80)

try:
    url = "https://rest.nexmo.com/account/get-balance"
    response = requests.get(url, params={'api_key': api_key, 'api_secret': api_secret})
    
    if response.status_code == 200:
        balance_data = response.json()
        print(f"\n✅ Account Active!")
        print(f"   Balance: €{balance_data.get('value')}")
        print(f"   Auto-reload: {balance_data.get('autoReload')}")
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("""
If you see 401 error above, you need to:

1. Go to: https://dashboard.nexmo.com/applications
2. Find your application OR create a new one
3. Enable "Voice" capability
4. Set Answer URL: https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-voice-webhook/
5. Set Event URL: https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/vonage-event-callback/
6. Download the private_key.pem file
7. Copy Application ID and update .env file
8. Replace ./private_key.pem with downloaded file
""")
print("=" * 80)
