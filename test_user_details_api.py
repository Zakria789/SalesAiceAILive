#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import TwilioCall
from subscriptions.models import Subscription, BillingHistory
from django.utils import timezone
from django.db.models import Count
import json

User = get_user_model()

def test_user_details_api():
    print("=== TESTING USER DETAILS API ===\n")
    
    # Get user with calls (zakria11@gmail.com)
    user = User.objects.filter(user_name='zakria11@gmail.com').first()
    if not user:
        print("❌ User zakria11@gmail.com not found")
        # Try to find user with most calls
        from HumeAiTwilio.models import TwilioCall
        user_with_calls = User.objects.annotate(
            call_count=Count('twilio_calls')
        ).order_by('-call_count').first()
        if user_with_calls and user_with_calls.twilio_calls.exists():
            user = user_with_calls
            print(f"✅ Using user with most calls: {user.user_name}")
        else:
            print("❌ No user with calls found")
            return
    
    print(f"👤 Testing API for user: {user.user_name} (ID: {user.id})")
    
    # Import the API view
    from accounts.admin_views import UserDetailAPIView
    
    # Create a mock request
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    # Create admin user for the request
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        # Create a temporary admin user
        admin_user = User.objects.create_user(
            user_name='temp_admin',
            email='admin@test.com',
            password='testpass',
            is_staff=True,
            is_superuser=True
        )
        print(f"Created temporary admin user: {admin_user.user_name}")
    
    # Test the API view
    view = UserDetailAPIView()
    request = MockRequest(admin_user)
    
    try:
        response = view.get(request, str(user.id))
        
        if response.status_code == 200:
            data = response.data
            
            print(f"✅ API Response successful!")
            print(f"\n📊 USER DATA:")
            user_data = data['user']
            print(f"   Name: {user_data['name']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print(f"   Status: {user_data['status']}")
            print(f"   Total Calls: {user_data['totalCalls']}")
            print(f"   Minutes Used: {user_data['minutesUsed']}")
            print(f"   Current Plan: {user_data['currentPlan']}")
            print(f"   Billing Status: {user_data['billingStatus']}")
            
            print(f"\n📞 CALL HISTORY:")
            call_history = data['callHistory']
            print(f"   Total records: {len(call_history)}")
            for i, call in enumerate(call_history[:3]):
                print(f"   {i+1}. {call['type']} call on {call['date'][:10]} - {call['duration']}s - ${call['cost']}")
            
            print(f"\n💳 BILLING HISTORY:")
            billing_history = data['billingHistory']
            print(f"   Total records: {len(billing_history)}")
            for i, bill in enumerate(billing_history[:3]):
                print(f"   {i+1}. ${bill['amount']} - {bill['type']} - {bill['status']}")
            
            print(f"\n📈 ANALYTICS:")
            analytics = data['analytics']
            print(f"   Total Spent: ${analytics['totalSpent']}")
            print(f"   Avg Call Duration: {analytics['avgCallDuration']} min")
            print(f"   Success Rate: {analytics['successRate']}%")
            print(f"   Most Active Day: {analytics['mostActiveDay']}")
            print(f"   Monthly calls: {len(analytics['callsByMonth'])} months of data")
            
            # Show expected API URL
            print(f"\n🌐 API ENDPOINT:")
            print(f"   URL: /api/admin/users/{user.id}/details/")
            print(f"   Method: GET")
            print(f"   Auth: Bearer <admin_jwt_token>")
            
            # Show sample response structure
            print(f"\n📋 SAMPLE RESPONSE STRUCTURE:")
            sample_structure = {
                "user": {
                    "id": user_data['id'],
                    "name": user_data['name'],
                    "email": user_data['email'],
                    "totalCalls": user_data['totalCalls'],
                    "minutesUsed": user_data['minutesUsed'],
                    "currentPlan": user_data['currentPlan'],
                    "profile": user_data['profile']
                },
                "callHistory": f"[{len(call_history)} records]",
                "billingHistory": f"[{len(billing_history)} records]", 
                "activityLogs": f"[{len(data['activityLogs'])} records]",
                "analytics": analytics
            }
            print(json.dumps(sample_structure, indent=2))
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.data}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_details_api()