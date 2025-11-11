"""
Update Vonage Application Public Key via API
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
import requests
import json

print("=" * 80)
print("VONAGE APPLICATION PUBLIC KEY UPDATE")
print("=" * 80)

# Load config
api_key = config('VONAGE_API_KEY')
api_secret = config('VONAGE_API_SECRET')
app_id = config('VONAGE_APPLICATION_ID')
private_key_path = config('VONAGE_PRIVATE_KEY_PATH')

# Extract public key from private key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

with open(private_key_path, 'rb') as f:
    private_key_data = f.read()

private_key = load_pem_private_key(private_key_data, password=None, backend=default_backend())
public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

public_key_str = public_pem.decode('utf-8')

print(f"\n📝 New Public Key extracted:")
print(public_key_str)

# Get current application details
print(f"\n🔍 Getting current application details...")
url = f"https://api.nexmo.com/v2/applications/{app_id}"

try:
    response = requests.get(url, auth=(api_key, api_secret))
    
    if response.status_code == 200:
        app_data = response.json()
        print(f"✅ Application found: {app_data.get('name')}")
        
        # Update with new public key
        print(f"\n🔧 Updating public key...")
        
        # Prepare update payload - keep all existing settings
        update_payload = {
            "name": app_data.get('name'),
            "capabilities": app_data.get('capabilities', {}),
            "keys": {
                "public_key": public_key_str
            }
        }
        
        # Update application
        update_response = requests.put(
            url,
            auth=(api_key, api_secret),
            headers={'Content-Type': 'application/json'},
            json=update_payload
        )
        
        if update_response.status_code == 200:
            print(f"✅ PUBLIC KEY UPDATED SUCCESSFULLY!")
            print(f"\n🎉 Vonage application is now synced with local private key!")
        else:
            print(f"❌ Update failed: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
            
    else:
        print(f"❌ Failed to get application: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 80)
