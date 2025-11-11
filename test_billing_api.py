#!/usr/bin/env python
"""
Test the new Billing Data API
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.billing_data_api import BillingDataAPIView
from django.http import HttpRequest

def test_billing_data_api():
    """Test the new Billing Data API"""
    print("🧪 TESTING BILLING DATA API")
    print("=" * 60)
    
    try:
        # Get test user with subscription
        User = get_user_model()
        user = User.objects.filter(user_name='testuser_fix').first()
        if not user:
            print("❌ Test user not found")
            return False
        
        # Test API
        api_view = BillingDataAPIView()
        request = HttpRequest()
        request.method = 'GET'
        request.user = user
        
        response = api_view.get(request)
        
        if response.status_code == 200:
            data = response.data
            print(f"✅ API Response Status: {response.status_code}")
            print(f"✅ Success: {data.get('success', False)}")
            
            billing_data = data.get('billing_data', {})
            
            print(f"\n📋 BILLING DATA STRUCTURE:")
            print(f"   • subscription: {'✅' if 'subscription' in billing_data else '❌'}")
            print(f"   • upcoming_invoice: {'✅' if 'upcoming_invoice' in billing_data else '❌'}")
            print(f"   • payment_methods: {'✅' if 'payment_methods' in billing_data else '❌'}")
            print(f"   • invoices: {'✅' if 'invoices' in billing_data else '❌'}")
            print(f"   • billing_address: {'✅' if 'billing_address' in billing_data else '❌'}")
            
            # Show subscription details
            subscription = billing_data.get('subscription', {})
            if subscription:
                print(f"\n📊 SUBSCRIPTION DETAILS:")
                print(f"   • Plan: {subscription.get('plan_name')}")
                print(f"   • Status: {subscription.get('status')}")
                print(f"   • Price: ${subscription.get('price_monthly')}")
                print(f"   • Features: {len(subscription.get('features', []))} items")
            
            print(f"\n✅ API TEST SUCCESSFUL!")
            return True
            
        else:
            print(f"❌ API Response Status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"❌ Response: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting Billing Data API Test...")
    success = test_billing_data_api()
    
    if success:
        print(f"\n🎉 BILLING DATA API IS READY!")
        print(f"📌 Endpoint: /api/subscriptions/user/billing-data/")
    else:
        print(f"\n❌ API test failed")
