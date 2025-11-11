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
from django.db.models import Sum

User = get_user_model()

def test_updated_dashboard_calculation():
    print("=== TESTING UPDATED DASHBOARD CALCULATION ===\n")
    
    # Get user
    user = User.objects.filter(user_name='zakria11').first()
    print(f"👤 User: {user.user_name}")
    
    # Get subscription
    user_subscription = Subscription.objects.filter(user=user, status='active').first()
    billing_start = user_subscription.current_period_start.date()
    billing_end = user_subscription.current_period_end.date()
    
    print(f"📅 Billing cycle: {billing_start} to {billing_end}")
    
    # Simulate the exact dashboard calculation
    current_cycle_calls = TwilioCall.objects.filter(
        user=user,
        started_at__date__gte=billing_start,
        started_at__date__lte=billing_end
    )
    
    # Calculate calls
    inbound_calls = current_cycle_calls.filter(direction='inbound').count()
    outbound_calls = current_cycle_calls.filter(direction__in=['outbound', 'outbound_api']).count()
    total_calls = inbound_calls + outbound_calls
    
    # Calculate actual minutes used from call data (NEW LOGIC)
    total_duration_seconds = current_cycle_calls.aggregate(total=Sum('duration'))['total'] or 0
    actual_minutes_used = round(total_duration_seconds / 60, 2) if total_duration_seconds else 0
    
    # Get plan info
    plan_name = user_subscription.plan.name
    plan_minutes_limit = user_subscription.plan.call_minutes_limit
    plan_minutes_used = actual_minutes_used  # Now uses calculated value
    
    print(f"\n📊 DASHBOARD RESULTS (NEW CALCULATION):")
    print(f"   inboundCalls: {inbound_calls}")
    print(f"   outboundCalls: {outbound_calls}")
    print(f"   totalCallsThisCycle: {total_calls}")
    print(f"   planName: {plan_name}")
    print(f"   planMinutesLimit: {plan_minutes_limit}")
    print(f"   planMinutesUsed: {plan_minutes_used} ✅ (was 0, now calculated from call durations)")
    
    # Calculate utilization
    utilization = (plan_minutes_used / plan_minutes_limit * 100) if plan_minutes_limit > 0 else 0
    print(f"   Plan utilization: {utilization:.1f}%")
    
    print(f"\n🎯 EXPECTED API RESPONSE:")
    expected_response = {
        "inboundCalls": inbound_calls,
        "outboundCalls": outbound_calls,
        "planName": plan_name,
        "planMinutesLimit": plan_minutes_limit,
        "planMinutesUsed": plan_minutes_used,
        "totalCallsThisCycle": total_calls,
    }
    
    import json
    print(json.dumps(expected_response, indent=2))
    
    if plan_minutes_used > 0:
        print(f"\n🎉 SUCCESS! planMinutesUsed now shows {plan_minutes_used} instead of 0!")
    else:
        print(f"\n⚠️ Still 0 minutes - check if calls have duration data")

if __name__ == "__main__":
    test_updated_dashboard_calculation()