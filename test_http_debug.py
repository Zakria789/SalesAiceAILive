#!/usr/bin/env python
"""
HTTP client test to debug the exact issue
"""

import requests
import json

def test_http_request():
    """Test the actual HTTP request to find the exact issue"""
    print("🔍 Testing HTTP request...")
    
    # First get a valid admin token
    print("\n1️⃣ Getting admin token...")
    token_response = requests.get('http://localhost:8002/api/auth/admin-token/')
    
    if token_response.status_code != 200:
        print(f"❌ Failed to get token: {token_response.status_code}")
        print(f"Response: {token_response.text}")
        return
    
    token_data = token_response.json()
    token = token_data.get('access_token')
    print(f"✅ Got token: {token[:20]}...")
    
    # Test the AdminUserAPIView endpoint
    print("\n2️⃣ Testing AdminUserAPIView endpoint...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'http://localhost:8002/api/accounts/admin/users/4/',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Check if it's HTML (error page) or JSON
        content_type = response.headers.get('content-type', '')
        
        if 'text/html' in content_type:
            print("❌ Got HTML error page instead of JSON")
            # Extract just the error message from HTML
            text = response.text
            if 'Exception Value:' in text:
                start = text.find('Exception Value:') + len('Exception Value:')
                end = text.find('</td>', start)
                error_msg = text[start:end].strip()
                print(f"Error: {error_msg}")
        elif 'application/json' in content_type:
            print("✅ Got JSON response")
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
        else:
            print(f"❓ Unknown content type: {content_type}")
            print(f"Response (first 500 chars): {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")

if __name__ == "__main__":
    test_http_request()