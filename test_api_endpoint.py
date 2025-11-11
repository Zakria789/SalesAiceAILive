#!/usr/bin/env python
import requests
import json

def test_user_details_api_endpoint():
    print("=== TESTING USER DETAILS API ENDPOINT ===\n")
    
    # API endpoint
    base_url = "http://localhost:8000"
    user_id = "4"  # zakria11@gmail.com user ID
    url = f"{base_url}/api/admin/users/{user_id}/details/"
    
    print(f"🌐 Testing endpoint: {url}")
    
    # Note: This would require admin authentication
    # For actual use, you'd need:
    # headers = {'Authorization': 'Bearer <admin_jwt_token>'}
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 401:
            print("✅ Server is running (got 401 Unauthorized as expected)")
            print("🔑 Authentication needed for admin endpoint")
            print("\n📋 ENDPOINT SUMMARY:")
            print(f"   URL: {url}")
            print(f"   Method: GET")
            print(f"   Auth Required: Yes (Admin JWT token)")
            print(f"   Response Type: JSON")
            
        elif response.status_code == 200:
            print("🎉 SUCCESS! Admin API returned data:")
            data = response.json()
            
            # Show key data points
            user_data = data.get('user', {})
            print(f"\n👤 USER INFO:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Total Calls: {user_data.get('totalCalls')}")
            print(f"   Minutes Used: {user_data.get('minutesUsed')}")
            print(f"   Current Plan: {user_data.get('currentPlan')}")
            
            print(f"\n📞 CALL DATA:")
            print(f"   Call History Records: {len(data.get('callHistory', []))}")
            print(f"   Billing History Records: {len(data.get('billingHistory', []))}")
            print(f"   Activity Log Records: {len(data.get('activityLogs', []))}")
            
            analytics = data.get('analytics', {})
            print(f"\n📊 ANALYTICS:")
            print(f"   Success Rate: {analytics.get('successRate')}%")
            print(f"   Avg Call Duration: {analytics.get('avgCallDuration')} min")
            print(f"   Most Active Day: {analytics.get('mostActiveDay')}")
            
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("🔧 Please ensure Django server is running:")
        print("   python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
    
    print(f"\n📚 API DOCUMENTATION:")
    print(f"   Endpoint: GET /api/admin/users/<userId>/details/")
    print(f"   Authentication: Admin JWT token required")
    print(f"   Parameters: userId (string) - User ID to get details for")
    print(f"   Response: UserDetailData interface (see TypeScript definitions)")
    
    print(f"\n🎯 USAGE EXAMPLE:")
    print(f"   fetch('/api/admin/users/4/details/', {{")
    print(f"     headers: {{ 'Authorization': 'Bearer <admin_token>' }}")
    print(f"   }})")
    print(f"   .then(res => res.json())")
    print(f"   .then(data => console.log(data))")

if __name__ == "__main__":
    test_user_details_api_endpoint()