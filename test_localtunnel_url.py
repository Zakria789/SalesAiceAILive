"""
Test Localtunnel Connection
"""
import os
import sys

print("\n" + "="*70)
print("🔍 LOCALTUNNEL URL TESTER")
print("="*70 + "\n")

print("📋 Instructions:")
print("1. Check the NEW PowerShell window")
print("2. Copy the URL (looks like: https://random-word.loca.lt)")
print("3. Paste it here")
print()

tunnel_url = input("Enter your localtunnel URL: ").strip()

if not tunnel_url:
    print("\n❌ No URL provided!")
    sys.exit(1)

if not tunnel_url.startswith('http'):
    tunnel_url = 'https://' + tunnel_url

print(f"\n✅ Testing URL: {tunnel_url}\n")

import requests

try:
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get(
        f"{tunnel_url}/api/hume-twilio/health/",
        timeout=10,
        allow_redirects=True
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✅ Localtunnel is WORKING!")
        
        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('BASE_URL='):
                        f.write(f'BASE_URL={tunnel_url}\n')
                    else:
                        f.write(line)
            
            print(f"✅ Updated .env with: BASE_URL={tunnel_url}")
        
        print("\n" + "="*70)
        print("📋 TWILIO WEBHOOK URLS:")
        print("="*70)
        print(f"\nVoice Webhook:")
        print(f"{tunnel_url}/api/hume-twilio/voice-webhook-fixed/")
        print(f"\nStatus Callback:")
        print(f"{tunnel_url}/api/hume-twilio/status-callback-fixed/")
        print("\n" + "="*70)
        
    else:
        print(f"\n❌ Got status {response.status_code}")
        print("Check if Django is running on port 8002")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPossible issues:")
    print("- Django not running on port 8002")
    print("- Localtunnel not started properly")
    print("- Wrong URL entered")

print()
