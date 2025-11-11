"""
Test Scheduled/Bulk Calls API
==============================
Ye script dikhayega ke scheduled calls API kya data return kar raha hai
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "umair11@gmail.com"
PASSWORD = "Test@123"

def get_jwt_token():
    """Get JWT token for authentication"""
    url = f"{BASE_URL}/api/accounts/login/"
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_scheduled_calls_api(token):
    """Test scheduled/bulk calls API"""
    
    print("=" * 80)
    print("📊 TESTING SCHEDULED/BULK CALLS API")
    print("=" * 80)
    print()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get all scheduled calls
    print("1️⃣  GET ALL SCHEDULED CALLS")
    print("-" * 80)
    url = f"{BASE_URL}/api/hume-twilio/dashboard/outbound/scheduled/"
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print()
        
        # Summary
        print("📊 SUMMARY:")
        summary = data.get('summary', {})
        print(f"   • Pending: {summary.get('total_pending', 0)}")
        print(f"   • Active: {summary.get('total_active', 0)}")
        print(f"   • Completed: {summary.get('total_completed', 0)}")
        print(f"   • Failed: {summary.get('total_failed', 0)}")
        print()
        
        # Show data structure
        calls = data.get('calls', {})
        
        # Pending calls
        if calls.get('pending'):
            print("⏳ PENDING CALLS:")
            for call in calls['pending'][:3]:  # Show first 3
                print(f"   • To: {call['to_number']}")
                print(f"     Customer: {call['customer_name']}")
                print(f"     Agent: {call['agent']['name']}")
                print(f"     Created: {call['created_at']}")
                print()
        
        # Active calls
        if calls.get('active'):
            print("📞 ACTIVE CALLS:")
            for call in calls['active'][:3]:
                print(f"   • To: {call['to_number']}")
                print(f"     Customer: {call['customer_name']}")
                print(f"     Agent: {call['agent']['name']}")
                print(f"     Started: {call['started_at']}")
                print()
        
        # Completed calls
        if calls.get('completed'):
            print("✅ COMPLETED CALLS:")
            for call in calls['completed'][:3]:
                print(f"   • To: {call['to_number']}")
                print(f"     Customer: {call['customer_name']}")
                print(f"     Duration: {call['duration']} seconds")
                print()
        
        # Failed calls
        if calls.get('failed'):
            print("❌ FAILED CALLS:")
            for call in calls['failed'][:3]:
                print(f"   • To: {call['to_number']}")
                print(f"     Customer: {call['customer_name']}")
                print(f"     Status: {call['status']}")
                print()
        
        # Full JSON response
        print("\n📄 FULL JSON RESPONSE:")
        print(json.dumps(data, indent=2))
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    print()
    
    # Test 2: Filter by status = pending
    print("\n2️⃣  FILTER BY STATUS = PENDING")
    print("-" * 80)
    url = f"{BASE_URL}/api/hume-twilio/dashboard/outbound/scheduled/?status=pending"
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', {})
        print(f"✅ Pending calls: {summary.get('total_pending', 0)}")
    
    print()
    
    # Test 3: Filter by status = completed
    print("3️⃣  FILTER BY STATUS = COMPLETED")
    print("-" * 80)
    url = f"{BASE_URL}/api/hume-twilio/dashboard/outbound/scheduled/?status=completed"
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', {})
        print(f"✅ Completed calls: {summary.get('total_completed', 0)}")
    
    print()
    print("=" * 80)


def check_local_database():
    """Check local database for outbound calls"""
    import os
    import sys
    import django
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    from HumeAiTwilio.models import TwilioCall
    
    print("\n" + "=" * 80)
    print("💾 LOCAL DATABASE CHECK")
    print("=" * 80)
    print()
    
    outbound_calls = TwilioCall.objects.filter(direction='outbound')
    
    print(f"📊 Total Outbound Calls: {outbound_calls.count()}")
    print()
    
    # Group by status
    statuses = {
        'initiated': outbound_calls.filter(status='initiated').count(),
        'ringing': outbound_calls.filter(status='ringing').count(),
        'in_progress': outbound_calls.filter(status='in_progress').count(),
        'completed': outbound_calls.filter(status='completed').count(),
        'failed': outbound_calls.filter(status='failed').count(),
        'no_answer': outbound_calls.filter(status='no_answer').count(),
        'busy': outbound_calls.filter(status='busy').count(),
    }
    
    print("📊 BREAKDOWN BY STATUS:")
    for status, count in statuses.items():
        if count > 0:
            print(f"   • {status}: {count}")
    
    print()
    
    # Show recent calls
    print("📞 RECENT OUTBOUND CALLS:")
    recent = outbound_calls.order_by('-created_at')[:5]
    
    for call in recent:
        print(f"\n   Call SID: {call.call_sid}")
        print(f"   To: {call.to_number}")
        print(f"   Customer: {call.customer_name or 'N/A'}")
        print(f"   Status: {call.status}")
        print(f"   Duration: {call.duration}s")
        print(f"   Created: {call.created_at}")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    print("\n🚀 Starting Scheduled Calls API Test...\n")
    
    # First check local database
    try:
        check_local_database()
    except Exception as e:
        print(f"⚠️  Could not check local database: {e}")
    
    # Get JWT token
    print("\n🔐 Getting JWT Token...")
    token = get_jwt_token()
    
    if token:
        print("✅ Token obtained successfully!")
        print()
        
        # Test API
        test_scheduled_calls_api(token)
        
        print("\n✅ Test Complete!\n")
    else:
        print("❌ Failed to get token. Cannot test API.\n")
