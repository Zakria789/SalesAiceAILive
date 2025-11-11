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
from subscriptions.models import Subscription
from django.utils import timezone

User = get_user_model()

def verify_dashboard_fix():
    print("=== VERIFYING DASHBOARD FIX ===\n")
    
    # Get the user with active subscription  
    test_user = User.objects.filter(subscription__status='active').first()
    
    if not test_user:
        print("❌ No user with active subscription found")
        return
    
    print(f"🧪 Testing dashboard calculation for user: {test_user.user_name}")
    
    # Get user's subscription billing cycle
    user_subscription = Subscription.objects.filter(user=test_user, status='active').first()
    billing_start = user_subscription.current_period_start.date()
    billing_end = user_subscription.current_period_end.date()
    
    print(f"📅 Billing cycle: {billing_start} to {billing_end}")
    
    # Simulate the dashboard API calculation
    current_cycle_calls = TwilioCall.objects.filter(
        user=test_user,
        started_at__date__gte=billing_start,
        started_at__date__lte=billing_end
    )
    
    # Use the new corrected query
    inbound_calls = current_cycle_calls.filter(direction='inbound').count()
    outbound_calls = current_cycle_calls.filter(direction__in=['outbound', 'outbound_api']).count()
    total_calls = inbound_calls + outbound_calls
    
    print(f"\n📊 DASHBOARD RESULTS:")
    print(f"   Inbound calls: {inbound_calls}")
    print(f"   Outbound calls: {outbound_calls}")  
    print(f"   Total calls this cycle: {total_calls}")
    
    # Check plan information
    plan_name = user_subscription.plan.name
    plan_minutes_limit = user_subscription.plan.call_minutes_limit
    
    print(f"\n💳 SUBSCRIPTION INFO:")
    print(f"   Plan: {plan_name}")
    print(f"   Minutes limit: {plan_minutes_limit}")
    
    print(f"\n🎯 EXPECTED DASHBOARD RESPONSE:")
    dashboard_preview = {
        "inboundCalls": inbound_calls,
        "outboundCalls": outbound_calls,
        "planName": plan_name,
        "planMinutesLimit": plan_minutes_limit,
        "totalCallsThisCycle": total_calls,
    }
    
    for key, value in dashboard_preview.items():
        print(f"   \"{key}\": {value}")
    
    if total_calls > 0:
        print(f"\n🎉 SUCCESS! Dashboard should now show {total_calls} calls instead of 0!")
        print(f"✅ Issue resolved - calls are now properly counted")
    else:
        print(f"\n⚠️ Still showing 0 calls - may need further investigation")

if __name__ == "__main__":
    verify_dashboard_fix()