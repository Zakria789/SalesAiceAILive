#!/usr/bin/env python
"""
Test PATCH with form data instead of JSON
"""

import requests

def test_patch_form_data():
    """Test PATCH with form data"""
    print("🔍 Testing PATCH with form data...")
    
    # Get token
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    token = token_response.json().get('access_token')
    
    headers = {
        'Authorization': f'Bearer {token}',
        # Don't set Content-Type, let requests handle it for form data
    }
    
    # Test with comprehensive form data
    form_data = {
        'name': 'Updated Admin User',
        'email': 'updated.admin@example.com', 
        'phone': '+1-555-0123',
        'company': 'Updated Company LLC',
        'role': 'admin',
        'status': 'active',
        'bio': 'Updated bio information',
        'timezone': 'PST',
        'language': 'es'
    }
    
    try:
        response = requests.patch(
            'http://localhost:8002/api/accounts/admin/users/4/',
            headers=headers,
            data=form_data  # Using data= instead of json=
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_patch_form_data()