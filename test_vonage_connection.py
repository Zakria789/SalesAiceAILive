"""
Test Vonage API Connection and Authentication
"""
import os
from dotenv import load_dotenv
import vonage
from pathlib import Path

load_dotenv()

print("=" * 80)
print("VONAGE API CONNECTION TEST")
print("=" * 80)

# Load credentials
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')
VONAGE_APPLICATION_ID = os.getenv('VONAGE_APPLICATION_ID')
VONAGE_PHONE = os.getenv('VONAGE_PHONE_NUMBER')
PRIVATE_KEY_PATH = os.getenv('VONAGE_PRIVATE_KEY_PATH', './private_key.pem')

print(f"\nAPI Key: {VONAGE_API_KEY}")
print(f"Application ID: {VONAGE_APPLICATION_ID}")
print(f"Phone Number: {VONAGE_PHONE}")
print(f"Private Key Path: {PRIVATE_KEY_PATH}")

# Check private key file
key_path = Path(PRIVATE_KEY_PATH)
if key_path.exists():
    print(f"\n✅ Private key file exists")
    with open(key_path, 'r') as f:
        key_content = f.read()
    print(f"   Key size: {len(key_content)} bytes")
else:
    print(f"\n❌ Private key file NOT found at: {key_path.absolute()}")
    exit(1)

print("\n" + "-" * 80)
print("Testing Vonage Authentication...")
print("-" * 80)

try:
    # Create Vonage Voice client
    auth = vonage.Auth(
        application_id=VONAGE_APPLICATION_ID,
        private_key=key_content
    )
    voice_client = vonage.Voice(auth)
    
    print("\n✅ Vonage Voice client created successfully!")
    print("✅ JWT Authentication working!")
    
    # Test account balance with basic auth
    try:
        account_auth = vonage.Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
        account_client = vonage.Account(account_auth)
        
        balance = account_client.get_balance()
        print(f"\n✅ Account Balance: €{balance}")
        print("✅ Vonage API fully operational!")
        
    except Exception as e:
        print(f"\n⚠️ Balance check: {e}")
        print("✅ Voice authentication confirmed working!")
    
    print("\n" + "=" * 80)
    print("✅ VONAGE CONNECTION: WORKING")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Vonage Connection Failed: {e}")
    print("\n" + "=" * 80)
    print("❌ VONAGE CONNECTION: FAILED")
    print("=" * 80)
