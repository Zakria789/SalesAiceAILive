"""
Test Change Password API
========================
Direct test for the change password endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "umair11@gmail.com"
CURRENT_PASSWORD = "Test@123"
NEW_PASSWORD = "Test@1234"

def test_change_password():
    """Test change password API directly"""
    
    print("🔐 TESTING CHANGE PASSWORD API")
    print("=" * 50)
    
    # Step 1: Get JWT Token
    print("\n1️⃣  Getting JWT Token...")
    login_response = requests.post(f"{BASE_URL}/api/accounts/login/", json={
        "email": EMAIL,
        "password": CURRENT_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get('access')
    print(f"✅ Token obtained: {token[:20]}...")
    
    # Step 2: Test Change Password
    print(f"\n2️⃣  Testing Change Password...")
    print(f"Current Password: {CURRENT_PASSWORD}")
    print(f"New Password: {NEW_PASSWORD}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "current_password": CURRENT_PASSWORD,
        "new_password": NEW_PASSWORD
    }
    
    # Correct URL with /api/accounts/ prefix
    url = f"{BASE_URL}/api/accounts/user/change-password/"
    print(f"URL: {url}")
    
    response = requests.put(url, json=payload, headers=headers)
    
    print(f"\n📊 RESPONSE:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✅ SUCCESS: {data.get('message')}")
            print("\n⚠️  IMPORTANT: Password has been changed!")
            print(f"   Old Password: {CURRENT_PASSWORD}")
            print(f"   New Password: {NEW_PASSWORD}")
            
            # Test login with new password
            print(f"\n3️⃣  Testing login with new password...")
            new_login = requests.post(f"{BASE_URL}/api/accounts/login/", json={
                "email": EMAIL,
                "password": NEW_PASSWORD
            })
            
            if new_login.status_code == 200:
                print("✅ Login with new password successful!")
            else:
                print(f"❌ Login with new password failed: {new_login.status_code}")
                
        else:
            print(f"❌ API Error: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Details: {error_data}")
        except:
            print(f"Raw Response: {response.text}")

if __name__ == '__main__':
    print("\n🚀 Starting Change Password Test...\n")
    test_change_password()
    print("\n✅ Test Complete!\n")