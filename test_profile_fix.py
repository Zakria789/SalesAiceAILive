"""
Quick Test - Profile Update API Fix
===================================
Test the fixed profile update API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "umair11@gmail.com"
PASSWORD = "Test@123"

def test_profile_update_fix():
    """Test profile update API with fixed username field"""
    
    print("🔧 TESTING PROFILE UPDATE API FIX")
    print("=" * 50)
    
    # Step 1: Get JWT Token
    print("\n1️⃣  Getting JWT Token...")
    login_response = requests.post(f"{BASE_URL}/api/accounts/login/", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get('access')
    print(f"✅ Token obtained")
    
    # Step 2: Get current user info
    print(f"\n2️⃣  Getting current user info...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    user_response = requests.get(f"{BASE_URL}/api/accounts/me/", headers=headers)
    if user_response.status_code == 200:
        current_user = user_response.json()
        print(f"Current user: {json.dumps(current_user, indent=2)}")
    else:
        print(f"❌ Could not get user info: {user_response.status_code}")
    
    # Step 3: Test Profile Update
    print(f"\n3️⃣  Testing Profile Update...")
    
    profile_data = {
        "username": "umair_test_fixed",
        "email": EMAIL  # Keep same email
    }
    
    url = f"{BASE_URL}/api/accounts/user/profile/"
    print(f"URL: {url}")
    print(f"Data: {json.dumps(profile_data, indent=2)}")
    
    response = requests.put(url, json=profile_data, headers=headers)
    
    print(f"\n📊 RESPONSE:")
    print(f"Status Code: {response.status_code}")
    
    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200 and response_data.get('success'):
            print(f"\n✅ SUCCESS: Profile updated!")
            updated_user = response_data.get('user', {})
            print(f"Updated username: {updated_user.get('username')}")
            print(f"Updated email: {updated_user.get('email')}")
        else:
            print(f"\n❌ ERROR: {response_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"Raw Response: {response.text}")

if __name__ == '__main__':
    print("\n🚀 Starting Profile Update Fix Test...\n")
    test_profile_update_fix()
    print("\n✅ Test Complete!\n")