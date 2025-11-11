#!/usr/bin/env python
"""Test call and wait for webhooks"""
import requests
import time

endpoint = "https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/initiate-call/"
payload = {
    "phone_no": "+923403471112",
    "agent_id": 1
}

print("📞 Making call...")
response = requests.post(endpoint, json=payload)
print(f"Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    call_sid = data.get('call', {}).get('call_sid')
    print(f"✅ Call initiated: {call_sid}")
    print(f"   Agent: {data.get('agent', {}).get('name')}")
    print(f"   Phone: {data.get('customer', {}).get('phone')}")
    print()
    print("⏳ Waiting 15 seconds for call to complete...")
    for i in range(15, 0, -1):
        print(f"   {i}s remaining...", end='\r')
        time.sleep(1)
    print("✅ Done waiting                     ")
else:
    print(f"❌ Error: {response.text}")
