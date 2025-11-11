#!/usr/bin/env python
"""Debug script to test Vonage call initiation and see full response"""
import requests
import json
import time

endpoint = "http://localhost:8002/api/hume-twilio/initiate-call/"
payload = {
    "phone_number": "+923403471112",  # Test number
    # agent_id will auto-select default agent
}

print("📞 Making call...")
response = requests.post(endpoint, json=payload)

print(f"Status: {response.status_code}")
print(f"\n===== FULL RESPONSE =====")
print(json.dumps(response.json(), indent=2))

if response.status_code == 201:
    call_uuid = response.json().get('call_sid')
    print(f"\n✅ Call UUID: {call_uuid}")
    print(f"\n⏳ Waiting 20 seconds for Vonage to call answer webhook...")
    time.sleep(20)
    print(f"✅ Done waiting - check server logs for webhook calls")
else:
    print(f"❌ Error: {response.text}")
