#!/usr/bin/env python
"""
Test status API without trailing slash
"""

import requests

def test_no_slash():
    # Get token
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    token = token_response.json().get('access_token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test status endpoint WITHOUT trailing slash
    try:
        response = requests.patch(
            'http://localhost:8002/api/accounts/admin/users/4/status',  # No trailing slash
            headers=headers,
            json={'status': 'inactive'}
        )
        
        print(f"Status (no slash): {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message')}")
        else:
            print(f"❌ Failed: {response.text[:200]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_no_slash()