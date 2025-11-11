"""
Quick test to verify Django server is running and APIs are accessible
"""

import requests
import json

def test_server():
    print("\n" + "="*60)
    print("🧪 TESTING DJANGO SERVER")
    print("="*60 + "\n")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Admin endpoint
    try:
        response = requests.get(f"{base_url}/admin/", timeout=2)
        if response.status_code in [200, 302]:
            print("✅ Admin endpoint: WORKING")
        else:
            print(f"⚠️  Admin endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin endpoint: {str(e)}")
    
    # Test 2: API base endpoint
    try:
        response = requests.get(f"{base_url}/api/", timeout=2)
        if response.status_code in [200, 404]:  # 404 is fine, means server is responding
            print("✅ API endpoint: WORKING")
        else:
            print(f"⚠️  API endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ API endpoint: {str(e)}")
    
    # Test 3: Call API agents endpoint
    try:
        response = requests.get(f"{base_url}/api/call/agents/", timeout=2)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Call API agents: WORKING ({len(agents)} agents found)")
        else:
            print(f"⚠️  Call API agents: {response.status_code}")
    except Exception as e:
        print(f"❌ Call API agents: {str(e)}")
    
    # Test 4: HumeAI-Twilio API
    try:
        response = requests.get(f"{base_url}/api/hume-twilio/agents/", timeout=2)
        if response.status_code in [200, 401]:  # 401 means auth required, but server is working
            print("✅ HumeAI-Twilio API: WORKING")
        else:
            print(f"⚠️  HumeAI-Twilio API: {response.status_code}")
    except Exception as e:
        print(f"❌ HumeAI-Twilio API: {str(e)}")
    
    print("\n" + "="*60)
    print("🎉 TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_server()
