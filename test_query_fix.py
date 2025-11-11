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
from django.db.models import Q

User = get_user_model()

def test_query_fix():
    print("=== TESTING QUERY FIX ===\n")
    
    # Get the user with active subscription
    test_user = User.objects.filter(subscription__status='active').first()
    
    if not test_user:
        print("❌ No user with active subscription found")
        return
    
    print(f"🧪 Testing for user: {test_user.user_name}")
    
    # Get user's subscription billing cycle
    user_subscription = Subscription.objects.filter(user=test_user, status='active').first()
    billing_start = user_subscription.current_period_start.date()
    billing_end = user_subscription.current_period_end.date()
    
    print(f"📅 Billing cycle: {billing_start} to {billing_end}")
    
    # Get user's calls for current billing cycle
    current_cycle_calls = TwilioCall.objects.filter(
        user=test_user,
        started_at__date__gte=billing_start,
        started_at__date__lte=billing_end
    )
    
    print(f"\n📊 QUERY COMPARISON:")
    
    # Test old incorrect query (what you had before)
    print("1. Old incorrect query:")
    # This would evaluate as just direction='outbound' (the 'or' doesn't work as expected)
    old_wrong = current_cycle_calls.filter(direction='outbound').count()
    print(f"   direction='outbound': {old_wrong}")
    
    # Test new correct query with Q objects
    print("\n2. New correct query with Q objects:")
    inbound_calls = current_cycle_calls.filter(direction='inbound').count()
    outbound_calls = current_cycle_calls.filter(Q(direction='outbound') | Q(direction='outbound_api')).count()
    print(f"   Inbound calls: {inbound_calls}")
    print(f"   Outbound calls (outbound + outbound_api): {outbound_calls}")
    print(f"   Total calls: {inbound_calls + outbound_calls}")
    
    # Alternative method using __in lookup
    print("\n3. Alternative with __in lookup:")
    outbound_calls_alt = current_cycle_calls.filter(direction__in=['outbound', 'outbound_api']).count()
    print(f"   Outbound calls (__in method): {outbound_calls_alt}")
    
    # Check what direction values actually exist
    print(f"\n🔍 ACTUAL DATA CHECK:")
    direction_counts = current_cycle_calls.values_list('direction', flat=True).distinct()
    print(f"   Direction values in billing cycle: {list(direction_counts)}")
    
    for direction in direction_counts:
        count = current_cycle_calls.filter(direction=direction).count()
        print(f"     '{direction}': {count} calls")
    
    # Test the complete dashboard calculation
    print(f"\n📈 DASHBOARD CALCULATION:")
    total_calls = inbound_calls + outbound_calls
    print(f"   Final result - Total calls this cycle: {total_calls}")
    
    if total_calls > 0:
        print(f"   🎉 SUCCESS! Dashboard should now show {total_calls} calls")
    else:
        print(f"   ⚠️ Still showing 0 calls - need to investigate further")

if __name__ == "__main__":
    test_query_fix()