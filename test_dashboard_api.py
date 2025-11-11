#!/usr/bin/env python
import requests
import json

# Test the comprehensive dashboard API
def test_dashboard_api():
    print("=== TESTING COMPREHENSIVE DASHBOARD API ===\n")
    
    # API endpoint
    url = "http://localhost:8000/api/dashboard/comprehensive/"
    
    # You'll need to get a valid JWT token for the user 'agenTest'
    # For now, let's test without authentication to see if the server is running
    
    try:
        # Test without authentication first to check if server is running
        response = requests.get(url, timeout=10)
        
        if response.status_code == 401:
            print("✅ Server is running (got 401 Unauthorized as expected)")
            print("📋 Response:", response.json() if response.content else "No content")
            
            print("\n🔑 Authentication needed. To test with authentication:")
            print("1. Get JWT token for user 'agenTest'")
            print("2. Add header: {'Authorization': 'Bearer <token>'}")
            print("\nOr test via Django admin/browser while logged in")
            
        elif response.status_code == 200:
            print("🎉 SUCCESS! API returned data:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Verify the fix
            print(f"\n✅ VERIFICATION:")
            print(f"   Total calls: {data.get('totalCallsThisCycle', 'N/A')}")
            print(f"   Inbound calls: {data.get('inboundCalls', 'N/A')}")
            print(f"   Outbound calls: {data.get('outboundCalls', 'N/A')}")
            print(f"   Plan: {data.get('planName', 'N/A')}")
            
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("🔧 Please ensure Django server is running:")
        print("   python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

if __name__ == "__main__":
    test_dashboard_api()