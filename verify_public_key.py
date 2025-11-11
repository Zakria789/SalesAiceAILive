"""
Extract Public Key from Private Key and verify
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from decouple import config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

print("=" * 80)
print("PUBLIC KEY EXTRACTION & VERIFICATION")
print("=" * 80)

private_key_path = config('VONAGE_PRIVATE_KEY_PATH')

# Read private key
with open(private_key_path, 'rb') as f:
    private_key_data = f.read()

print(f"\n✅ Private key loaded: {len(private_key_data)} bytes")

try:
    # Load private key
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    
    private_key = load_pem_private_key(
        private_key_data,
        password=None,
        backend=default_backend()
    )
    
    print(f"✅ Private key parsed successfully")
    print(f"   Key type: {type(private_key).__name__}")
    
    # Extract public key
    public_key = private_key.public_key()
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    public_key_str = public_pem.decode('utf-8')
    
    print(f"\n📝 Extracted Public Key:")
    print(public_key_str)
    
    # Get from .env
    public_key_from_env = config('VONAGE_PUBLIC_KEY', default='')
    
    if public_key_from_env:
        # Clean both for comparison
        extracted_clean = public_key_str.replace('\n', '').replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '').strip()
        env_clean = public_key_from_env.replace('\\n', '').replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '').strip()
        
        if extracted_clean == env_clean:
            print(f"\n✅ PUBLIC KEY MATCHES .env file!")
        else:
            print(f"\n⚠️  PUBLIC KEY DIFFERENT from .env")
            print(f"\n   .env has: {env_clean[:50]}...")
            print(f"   Extracted: {extracted_clean[:50]}...")
    else:
        print(f"\n⚠️  No VONAGE_PUBLIC_KEY in .env file")
    
    print(f"\n" + "=" * 80)
    print(f"COMPARE WITH DASHBOARD:")
    print(f"=" * 80)
    print(f"Go to: https://dashboard.nexmo.com/applications/0d75cbea-4319-434d-a864-f6f9ef83874d")
    print(f"Click 'Edit' → Check if 'Public Key' section shows:")
    print(f"  {public_key_str.split()[2][:50]}...")
    print(f"=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Also check JWT generation one more time with detailed info
print(f"\n" + "=" * 80)
print(f"JWT GENERATION TEST")
print(f"=" * 80)

import jwt
import time

app_id = config('VONAGE_APPLICATION_ID')

with open(private_key_path, 'r') as f:
    private_key_text = f.read()

iat = int(time.time())
payload = {
    'application_id': app_id,
    'iat': iat,
    'exp': iat + 900,
    'jti': f'verify-{iat}'
}

try:
    token = jwt.encode(payload, private_key_text, algorithm='RS256')
    print(f"✅ JWT generated")
    
    # Decode without verification to see payload
    decoded = jwt.decode(token, options={"verify_signature": False})
    print(f"\n📋 JWT Payload:")
    print(f"   application_id: {decoded.get('application_id')}")
    print(f"   iat: {decoded.get('iat')}")
    print(f"   exp: {decoded.get('exp')}")
    print(f"   jti: {decoded.get('jti')}")
    
    # Try to verify with public key
    try:
        verified = jwt.decode(token, public_key_str, algorithms=['RS256'])
        print(f"\n✅ JWT VERIFICATION SUCCESSFUL with extracted public key!")
    except Exception as ve:
        print(f"\n⚠️  JWT verification failed: {ve}")
    
except Exception as e:
    print(f"❌ JWT generation failed: {e}")

print(f"\n" + "=" * 80)
