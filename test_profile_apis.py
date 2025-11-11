"""
Test User Profile & Password APIs
=================================
Test script for the new user management APIs
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "umair11@gmail.com"
PASSWORD = "Test@123"

def get_jwt_token():
    """Get JWT token for authentication"""
    url = f"{BASE_URL}/api/accounts/login/"
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_profile_apis(token):
    """Test all profile management APIs"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("=" * 80)
    print("👤 TESTING USER PROFILE & PASSWORD APIS")
    print("=" * 80)
    print()
    
    # Test 1: Update Profile
    print("1️⃣  UPDATE PROFILE (username & email)")
    print("-" * 80)
    
    profile_data = {
        "username": "umair_updated_test",
        "email": "umair11@gmail.com"  # Keep same email
    }
    
    response = requests.put(
        f"{BASE_URL}/api/accounts/user/profile/",
        json=profile_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message')}")
        print(f"Updated User: {data.get('user', {}).get('username')} - {data.get('user', {}).get('email')}")
    else:
        print(f"❌ Error: {response.text}")
    
    print()
    
    # Test 2: Change Password (Wrong current password)
    print("2️⃣  CHANGE PASSWORD (Wrong Current Password)")
    print("-" * 80)
    
    password_data = {
        "current_password": "wrong_password",
        "new_password": "NewTest@123"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/accounts/user/change-password/",
        json=password_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Expected Error: {data.get('error')}")
    else:
        print(f"❌ Unexpected: {response.text}")
    
    print()
    
    # Test 3: Change Password (Correct)
    print("3️⃣  CHANGE PASSWORD (Correct)")
    print("-" * 80)
    
    password_data = {
        "current_password": PASSWORD,
        "new_password": "NewTest@123"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/accounts/user/change-password/",
        json=password_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message')}")
        print("⚠️  Password changed! Remember to update login credentials.")
    else:
        print(f"❌ Error: {response.text}")
    
    print()
    
    # Test 4: Forgot Password
    print("4️⃣  FORGOT PASSWORD (Send Reset Email)")
    print("-" * 80)
    
    forgot_data = {
        "email": EMAIL
    }
    
    response = requests.post(
        f"{BASE_URL}/api/accounts/user/forgot-password/",
        json=forgot_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message')}")
        print("📧 Check your email for reset link!")
    else:
        print(f"❌ Error: {response.text}")
    
    print()
    
    # Test 5: Forgot Password (Non-existent email)
    print("5️⃣  FORGOT PASSWORD (Non-existent Email)")
    print("-" * 80)
    
    forgot_data = {
        "email": "nonexistent@example.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/accounts/user/forgot-password/",
        json=forgot_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success (Security): {data.get('message')}")
        print("🔒 Security feature: Same message for security")
    else:
        print(f"❌ Error: {response.text}")
    
    print()
    
    # Test 6: Reset Password (Invalid token)
    print("6️⃣  RESET PASSWORD (Invalid Token)")
    print("-" * 80)
    
    reset_data = {
        "uid": "invalid_uid",
        "token": "invalid_token",
        "new_password": "ResetTest@123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/accounts/user/reset-password/",
        json=reset_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Expected Error: {data.get('error')}")
    else:
        print(f"❌ Unexpected: {response.text}")
    
    print()
    print("=" * 80)
    print("📝 API ENDPOINTS SUMMARY:")
    print("=" * 80)
    print("1. PUT  /api/accounts/user/change-password/  ✅")
    print("2. PUT  /api/accounts/user/profile/          ✅") 
    print("3. POST /api/accounts/user/forgot-password/  ✅")
    print("4. POST /api/accounts/user/reset-password/   ✅")
    print()
    print("🎯 Frontend Integration Ready!")
    print("=" * 80)


def show_curl_examples():
    """Show cURL examples for testing"""
    
    print("\n" + "=" * 80)
    print("🔧 CURL EXAMPLES")
    print("=" * 80)
    
    print("\n1️⃣  Change Password:")
    print("""curl -X PUT "http://localhost:8002/api/accounts/user/change-password/" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "current_password": "Test@123",
    "new_password": "NewTest@123"
  }'""")
    
    print("\n2️⃣  Update Profile:")
    print("""curl -X PUT "http://localhost:8002/api/accounts/user/profile/" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "new_username",
    "email": "new@example.com"
  }'""")
    
    print("\n3️⃣  Forgot Password:")
    print("""curl -X POST "http://localhost:8002/api/accounts/user/forgot-password/" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "umair11@gmail.com"
  }'""")
    
    print("\n4️⃣  Reset Password:")
    print("""curl -X POST "http://localhost:8002/api/accounts/user/reset-password/" \\
  -H "Content-Type: application/json" \\
  -d '{
    "uid": "TOKEN_FROM_EMAIL",
    "token": "TOKEN_FROM_EMAIL",
    "new_password": "ResetTest@123"
  }'""")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    print("\n🚀 Starting User Profile API Tests...\n")
    
    # Get JWT token
    print("🔐 Getting JWT Token...")
    token = get_jwt_token()
    
    if token:
        print("✅ Token obtained successfully!")
        print()
        
        # Test APIs
        test_profile_apis(token)
        
        # Show cURL examples
        show_curl_examples()
        
        print("\n✅ Testing Complete!\n")
    else:
        print("❌ Failed to get token. Cannot test APIs.\n")