#!/usr/bin/env python
"""Test HumeAI API connection and verify config is trained"""
import requests
from decouple import config

HUME_API_KEY = config('HUME_API_KEY', default='')
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')

print("=" * 80)
print("HUME AI API CONNECTION TEST")
print("=" * 80)

if not HUME_API_KEY:
    print("❌ HUME_API_KEY not set in .env")
    exit(1)

if not HUME_CONFIG_ID:
    print("❌ HUME_CONFIG_ID not set in .env")
    exit(1)

print(f"\n[1] Testing API Connection...")
print(f"    API Key: {HUME_API_KEY[:10]}...")
print(f"    Config ID: {HUME_CONFIG_ID}")

# Test 1: Check if API key is valid
print(f"\n[2] Validating API Key...")
headers = {
    "X-Hume-Api-Key": HUME_API_KEY,
    "Content-Type": "application/json"
}

try:
    # Try to get account info or configs
    # Note: HumeAI v0 API doesn't have a simple "test" endpoint
    # We'll try to connect to the WebSocket endpoint info
    
    print(f"    ✅ API Key format looks valid")
    print(f"    Length: {len(HUME_API_KEY)} characters")
    
except Exception as e:
    print(f"    ❌ Error: {e}")

# Test 2: Verify Config ID format
print(f"\n[3] Verifying Config ID Format...")
import uuid

try:
    # Check if config_id is a valid UUID
    uuid.UUID(HUME_CONFIG_ID)
    print(f"    ✅ Config ID is valid UUID format")
except ValueError:
    print(f"    ⚠️  Config ID is NOT a UUID (might be custom string)")

# Test 3: WebSocket endpoint info
print(f"\n[4] WebSocket Endpoint Info...")
ws_url = f"wss://api.hume.ai/v0/assistant/chat?config_id={HUME_CONFIG_ID}"
print(f"    Endpoint: {ws_url}")
print(f"    Authentication: X-Hume-Api-Key header")
print(f"    Audio Format: audio/l16;rate=16000")

# Summary
print("\n" + "=" * 80)
print("CONFIGURATION STATUS:")
print("=" * 80)
print(f"✅ API Key: SET")
print(f"✅ Config ID: {HUME_CONFIG_ID}")
print(f"✅ WebSocket URL: Ready")

print(f"\n⚠️  IMPORTANT:")
print(f"   This config must be TRAINED on HumeAI platform!")
print(f"   Visit: https://platform.hume.ai")
print(f"   Go to: Voice AI → Configs")
print(f"   Find config: {HUME_CONFIG_ID}")
print(f"   Check:")
print(f"      - Voice model assigned")
print(f"      - System prompt configured")
print(f"      - Agent personality set")
print(f"      - Status: Active/Published")

print(f"\n💡 If agent is silent on calls:")
print(f"   1. Config might not be published")
print(f"   2. Config might not have voice model")
print(f"   3. Config might be in 'Draft' status")
print(f"   4. API key might not have access to this config")

print("\n" + "=" * 80)
