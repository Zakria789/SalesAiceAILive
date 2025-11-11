#!/usr/bin/env python3
"""
Test script for Admin User Details API
"""
import requests
import json
import sys

# API endpoint
url = "http://localhost:8002/api/accounts/admin/users/4/details/"

# JWT token for admin access
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNDA3MTI3LCJpYXQiOjE3NjE0MDM1MjcsImp0aSI6ImYyOGVhZjFmOGU2MDQyYmJiYTY3MTQ1N2JkZDVhY2MzIiwidXNlcl9pZCI6IjIifQ.DrfJUbUy7xkamqgXIEqhJVa58N10U5pT5mn2mS_gx4Y"

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    print("🚀 Testing Admin User Details API...")
    print(f"📡 URL: {url}")
    print()
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! API Response:")
        print("=" * 50)
        
        # Print user details
        user = data.get('user', {})
        print(f"👤 User Info:")
        print(f"   ID: {user.get('id')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Status: {user.get('status')}")
        print(f"   Total Calls: {user.get('totalCalls')}")
        print(f"   Minutes Used: {user.get('minutesUsed')}")
        print(f"   Current Plan: {user.get('currentPlan')}")
        print(f"   Avatar: {user.get('avatar')}")
        print()
        
        # Print call history count
        call_history = data.get('callHistory', [])
        print(f"📞 Call History: {len(call_history)} records")
        if call_history:
            print(f"   Latest call: {call_history[0].get('date')}")
        print()
        
        # Print billing history count
        billing_history = data.get('billingHistory', [])
        print(f"💳 Billing History: {len(billing_history)} records")
        if billing_history:
            print(f"   Latest transaction: ${billing_history[0].get('amount')}")
        print()
        
        # Print activity logs count
        activity_logs = data.get('activityLogs', [])
        print(f"📋 Activity Logs: {len(activity_logs)} records")
        print()
        
        # Print analytics
        analytics = data.get('analytics', {})
        print(f"📈 Analytics:")
        print(f"   Total Spent: ${analytics.get('totalSpent')}")
        print(f"   Avg Call Duration: {analytics.get('avgCallDuration')} min")
        print(f"   Success Rate: {analytics.get('successRate')}%")
        print(f"   Most Active Day: {analytics.get('mostActiveDay')}")
        print()
        
    else:
        print(f"❌ FAILED! Status: {response.status_code}")
        try:
            error_data = response.json()
            print("Error details:")
            print(json.dumps(error_data, indent=2))
        except:
            print("Raw response:")
            print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ Connection Error - Make sure Django server is running on localhost:8002")
except Exception as e:
    print(f"❌ Error: {e}")