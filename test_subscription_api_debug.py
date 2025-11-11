#!/usr/bin/env python
"""
Test the subscription API to see debug output
"""
import requests
import json

# Test data
api_url = "http://127.0.0.1:8000/api/subscriptions/user/subscribe/"
test_data = {
    "user_id": 1,  # Assuming user ID 1 exists
    "package_id": "53d7eb44-3da6-4f7f-bfc2-3808de96a0b4"  # Use the same package ID from your result
}

print("🧪 Testing subscription API with debug logging...")
print(f"📍 URL: {api_url}")
print(f"📦 Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        api_url,
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📝 Response Headers: {dict(response.headers)}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        response_data = response.json()
        print(f"📄 Response JSON:")
        print(json.dumps(response_data, indent=2))
    else:
        print(f"📄 Response Text:")
        print(response.text)
        
except requests.RequestException as e:
    print(f"❌ Request failed: {str(e)}")
except json.JSONDecodeError as e:
    print(f"❌ JSON decode error: {str(e)}")
    print(f"Raw response: {response.text}")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
