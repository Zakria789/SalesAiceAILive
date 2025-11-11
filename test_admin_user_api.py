#!/usr/bin/env python3
"""
Test script for Admin User APIs
Tests both GET and PATCH endpoints for /api/accounts/admin/users/{userId}/
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
USER_ID = "4"  # Test with user ID 4

def get_admin_token():
    """Get admin JWT token"""
    try:
        response = requests.get(f"{BASE_URL}/api/auth/admin-token/")
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Failed to get admin token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting admin token: {e}")
        return None

def test_get_user(token):
    """Test GET /api/accounts/admin/users/{userId}/"""
    print(f"\n🔍 Testing GET /api/accounts/admin/users/{USER_ID}/")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/accounts/admin/users/{USER_ID}/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GET User API Success!")
            print(f"📋 User Data:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Name: {data.get('name')}")
            print(f"   - Email: {data.get('email')}")
            print(f"   - Role: {data.get('role')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Phone: {data.get('phone')}")
            print(f"   - Company: {data.get('company')}")
            print(f"   - Total Calls: {data.get('totalCalls')}")
            print(f"   - Minutes Used: {data.get('minutesUsed')}")
            print(f"   - Current Plan: {data.get('currentPlan')}")
            print(f"   - Billing Status: {data.get('billingStatus')}")
            print(f"   - Avatar: {data.get('avatar')}")
            print(f"   - Profile: {data.get('profile')}")
            return data
        else:
            print(f"❌ GET User API Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing GET user: {e}")
        return None

def test_update_user(token):
    """Test PATCH /api/accounts/admin/users/{userId}/"""
    print(f"\n📝 Testing PATCH /api/accounts/admin/users/{USER_ID}/")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test data for update
    update_data = {
        "name": "John Doe Updated",
        "phone": "+1234567890",
        "company": "Tech Corp Updated",
        "bio": "Updated bio for testing",
        "timezone": "America/New_York",
        "language": "en",
        "notifications": {
            "email": True,
            "sms": True,
            "push": False
        }
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/api/accounts/admin/users/{USER_ID}/", 
            headers=headers,
            json=update_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PATCH User API Success!")
            print(f"📋 Update Response:")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Updated User: {data.get('user')}")
            return data
        else:
            print(f"❌ PATCH User API Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing PATCH user: {e}")
        return None

def main():
    print("🚀 Testing Admin User APIs")
    print("=" * 50)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    print(f"✅ Got admin token: {token[:20]}...")
    
    # Test GET user
    user_data = test_get_user(token)
    
    # Test PATCH user
    if user_data:
        update_result = test_update_user(token)
        
        # Get user again to verify update
        if update_result:
            print(f"\n🔄 Verifying update by getting user again...")
            test_get_user(token)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()