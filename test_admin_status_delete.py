#!/usr/bin/env python
"""
Test the new Admin APIs:
1. PATCH /api/accounts/admin/users/{userId}/status - Update user status
2. DELETE /api/accounts/admin/users/{userId} - Delete user
"""

import requests
import json

def test_admin_status_and_delete_apis():
    """Test both status update and delete APIs"""
    print("🔍 Testing Admin Status and Delete APIs...")
    
    # Get admin token
    print("\n1️⃣ Getting admin token...")
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    
    if token_response.status_code != 200:
        print(f"❌ Failed to get token: {token_response.status_code}")
        return
    
    token = token_response.json().get('access_token')
    print(f"✅ Got token")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Update User Status API
    print("\n2️⃣ Testing User Status Update API...")
    
    # Test with different status values
    status_tests = ['inactive', 'banned', 'pending', 'active']
    
    for test_status in status_tests:
        try:
            status_data = {'status': test_status}
            
            response = requests.patch(
                'http://localhost:8002/api/accounts/admin/users/4/status/',
                headers=headers,
                json=status_data
            )
            
            print(f"  Status '{test_status}': {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Success: {result.get('message')}")
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error testing status '{test_status}': {e}")
    
    # Test invalid status
    print(f"\n3️⃣ Testing invalid status...")
    try:
        invalid_data = {'status': 'invalid_status'}
        response = requests.patch(
            'http://localhost:8002/api/accounts/admin/users/4/status/',
            headers=headers,
            json=invalid_data
        )
        
        print(f"Invalid status test: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected invalid status")
        else:
            print("❌ Should have rejected invalid status")
            
    except Exception as e:
        print(f"❌ Error testing invalid status: {e}")
    
    # Test 2: Delete User API  
    print(f"\n4️⃣ Testing User Delete API...")
    
    # First try to delete an admin user (should fail)
    try:
        response = requests.delete(
            'http://localhost:8002/api/accounts/admin/users/1/',  # Admin user
            headers=headers
        )
        
        print(f"Delete admin user: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly prevented admin deletion")
            result = response.json()
            print(f"  Message: {result.get('error')}")
        else:
            print("❌ Should have prevented admin deletion")
            
    except Exception as e:
        print(f"❌ Error testing admin deletion: {e}")
    
    # Try to delete a regular user (this will actually delete, so be careful!)
    print(f"\n⚠️  WARNING: The following test will actually delete user ID 4")
    print(f"   Do you want to proceed? This is just a test...")
    
    # For safety, let's just test the endpoint without actually deleting
    # You can uncomment this if you want to test actual deletion:
    
    # try:
    #     response = requests.delete(
    #         'http://localhost:8002/api/accounts/admin/users/4/',  # Regular user
    #         headers=headers
    #     )
    #     
    #     print(f"Delete regular user: {response.status_code}")
    #     if response.status_code == 200:
    #         result = response.json()
    #         print(f"✅ User deleted: {result.get('message')}")
    #         print(f"  Deleted user: {result.get('deleted_user')}")
    #     else:
    #         print(f"❌ Delete failed: {response.text}")
    #         
    # except Exception as e:
    #     print(f"❌ Error testing deletion: {e}")
    
    print("\n🎉 API testing complete!")
    print("\n📋 Summary of new endpoints:")
    print("   PATCH /api/accounts/admin/users/{userId}/status/")
    print("   DELETE /api/accounts/admin/users/{userId}/")

if __name__ == "__main__":
    test_admin_status_and_delete_apis()