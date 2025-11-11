#!/usr/bin/env python
"""
🔐 HUME AI - API KEY VALIDATION & TOKEN GENERATION
Check if we need to generate an access token or if API key format is wrong
"""
import requests
import json
from decouple import config

print("=" * 80)
print("🔐 HUME AI API KEY VALIDATION")
print("=" * 80)

api_key = config('HUME_API_KEY', default='')
config_id = config('HUME_CONFIG_ID', default='')

print(f"\n📋 Current Setup:")
print(f"   API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
print(f"   Config ID: {config_id}")

# Test 1: Direct API call to verify key
print("\n[TEST 1] Verify API Key Format")
print("-" * 80)

print("🔍 Checking API key validity...")

# Try to call HumeAI REST API (not WebSocket)
try:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try a simple REST endpoint to verify token
    response = requests.get(
        "https://api.hume.ai/v0/configs",
        headers=headers,
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ API Key is VALID!")
        configs = response.json()
        print(f"   Available configs: {len(configs)}")
        
        # Check if our config exists
        config_found = False
        for cfg in configs:
            if cfg.get('id') == config_id:
                print(f"   ✅ Your config ID found: {cfg.get('name', 'Unknown')}")
                config_found = True
                break
        
        if not config_found:
            print(f"   ⚠️  Config ID {config_id[:20]}... not found")
    
    elif response.status_code == 401:
        print(f"   ❌ API Key INVALID (401 Unauthorized)")
        print(f"   Response: {response.text[:200]}")
    
    else:
        print(f"   ⚠️  Unexpected status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check if key needs format change
print("\n[TEST 2] API Key Format Analysis")
print("-" * 80)

print(f"   Key length: {len(api_key)} characters")
print(f"   Key format: {'Token-like' if api_key.startswith('hm_') or len(api_key) > 20 else 'Unknown'}")
print(f"   Is alphanumeric: {'Yes' if api_key.isalnum() else 'Contains special chars'}")

if api_key.startswith('hm_'):
    print(f"   ✅ Appears to be HumeAI format (hm_ prefix)")
else:
    print(f"   ℹ️  Different format than expected (hm_ prefix)")

# Test 3: Alternative endpoints
print("\n[TEST 3] Test Alternative HumeAI Endpoints")
print("-" * 80)

endpoints = [
    ("Status Check", "https://api.hume.ai/v0/status"),
    ("User Info", "https://api.hume.ai/v0/user"),
    ("List Configs", "https://api.hume.ai/v0/configs"),
]

for name, url in endpoints:
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers, timeout=5)
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {name}: {response.status_code}")
        
    except Exception as e:
        print(f"   ⚠️  {name}: Error - {str(e)[:50]}")

print("\n" + "=" * 80)
print("💡 DIAGNOSIS")
print("=" * 80)

print("""
HumeAI uses different authentication methods:

1. API Key (Direct Bearer Token) - For REST API
   Usage: Authorization: Bearer {API_KEY}
   
2. OAuth / Access Token - For WebSocket
   Usage: ws connection + Bearer token
   
The 401 error suggests:
   - API key is expired or revoked
   - API key format is incorrect
   - Config ID doesn't match the key's permissions

SOLUTIONS:
1. Generate new API key from HumeAI Dashboard
   → Log in to: https://beta.hume.ai/console
   → Settings → API Keys
   → Create new key or verify existing

2. Check if key has "Production" access
   → Some keys might be limited to dev/staging

3. Verify Config ID
   → Go to: Configs → Select your config
   → Copy exact Config ID from dashboard

4. Check key expiration
   → Some keys auto-expire after 30/60/90 days
""")

print("=" * 80)
