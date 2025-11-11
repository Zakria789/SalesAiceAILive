#!/usr/bin/env python
"""
Test both GET and PATCH methods of AdminUserAPIView
"""

import requests
import json

def test_admin_user_api():
    """Test both GET and PATCH endpoints"""
    print("🔍 Testing AdminUserAPIView...")
    
    # Get admin token
    print("\n1️⃣ Getting admin token...")
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    
    if token_response.status_code != 200:
        print(f"❌ Failed to get token: {token_response.status_code}")
        return
    
    token_data = token_response.json()
    token = token_data.get('access_token')
    print(f"✅ Got token: {token[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test GET method
    print("\n2️⃣ Testing GET method...")
    try:
        get_response = requests.get(
            'http://localhost:8002/api/accounts/admin/users/4/',
            headers=headers
        )
        
        print(f"GET Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            get_data = get_response.json()
            print(f"✅ GET Success! Keys: {list(get_data.keys())}")
            print(f"User: {get_data.get('name')} ({get_data.get('email')})")
            print(f"Plan: {get_data.get('currentPlan')}")
            print(f"Calls: {get_data.get('totalCalls')}")
            print(f"Minutes: {get_data.get('minutesUsed')}")
        else:
            print(f"❌ GET failed: {get_response.text}")
            
    except Exception as e:
        print(f"❌ GET error: {e}")
    
    # Test PATCH method
    print("\n3️⃣ Testing PATCH method...")
    try:
        patch_data = {
            'name': 'Updated User Name',
            'company': 'Test Company Updated',
            'bio': 'This is an updated bio',
            'timezone': 'EST',
            'language': 'es',
            'notifications': {
                'email': False,
                'sms': True,
                'push': False
            }
        }
        
        patch_response = requests.patch(
            'http://localhost:8002/api/accounts/admin/users/4/',
            headers=headers,
            json=patch_data
        )
        
        print(f"PATCH Status: {patch_response.status_code}")
        
        if patch_response.status_code == 200:
            patch_result = patch_response.json()
            print(f"✅ PATCH Success! {patch_result}")
            
            # Verify changes with another GET
            print("\n4️⃣ Verifying changes...")
            verify_response = requests.get(
                'http://localhost:8002/api/accounts/admin/users/4/',
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"✅ Verification Success!")
                print(f"Updated Name: {verify_data.get('name')}")
                print(f"Updated Company: {verify_data.get('company')}")
                
        else:
            print(f"❌ PATCH failed: {patch_response.text}")
            
    except Exception as e:
        print(f"❌ PATCH error: {e}")
    
    print("\n🎉 AdminUserAPIView testing complete!")

if __name__ == "__main__":
    test_admin_user_api()