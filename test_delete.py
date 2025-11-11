#!/usr/bin/env python
"""
Test DELETE API
"""

import requests

def test_delete():
    # Get token
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    token = token_response.json().get('access_token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test DELETE endpoint (try to delete admin - should fail)
    try:
        response = requests.delete(
            'http://localhost:8002/api/accounts/admin/users/1/',  # Admin user
            headers=headers
        )
        
        print(f"Delete admin user - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_delete()