#!/usr/bin/env python
"""
Quick test to verify the isCurrentPlan fix
"""
import os
import sys
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from subscriptions.models import SubscriptionPlan, Subscription
from subscriptions.simple_plans_api import UserPlansComparisonAPIView
from django.http import HttpRequest

def create_mock_request(user=None):
    """Create a mock request object"""
    request = HttpRequest()
    request.method = 'GET'
    request.user = user
    return request

def test_iscurrent_fix():
    """Test that only current plan has isCurrentPlan: true"""
    print("🧪 TESTING isCurrentPlan FIX")
    print("=" * 50)
    
    try:
        # Get test user
        User = get_user_model()
        user, created = User.objects.get_or_create(
            user_name='testuser_fix',
            defaults={
                'email': 'testuser_fix@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Get plans
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
        if plans.count() < 2:
            print("❌ Need at least 2 plans for testing")
            return False
        
        # Test 1: User without subscription
        print("\n📋 Test 1: User without subscription")
        api_view = UserPlansComparisonAPIView()
        request = create_mock_request(user)
        
        response = api_view.get(request)
        data = response.data
        
        print(f"✅ Plans returned: {len(data['plans'])}")
        print(f"✅ Current plan: {data.get('current_plan')}")
        
        # Check that NO plan is marked as current
        current_plans = [p for p in data['plans'] if p.get('isCurrentPlan')]
        if len(current_plans) == 0:
            print("✅ CORRECT: No plan marked as current for user without subscription")
        else:
            print(f"❌ WRONG: {len(current_plans)} plans marked as current (should be 0)")
            return False
        
        # Check that all are upgrades
        for plan in data['plans']:
            if plan['type'] != 'upgrade':
                print(f"❌ WRONG: Plan {plan['name']} has type '{plan['type']}', should be 'upgrade'")
                return False
        print("✅ CORRECT: All plans are marked as 'upgrade' for user without subscription")
        
        # Test 2: User with subscription to middle plan
        print("\n📋 Test 2: User with subscription")
        middle_plan = plans[1] if plans.count() > 1 else plans[0]
        
        # Create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            plan=middle_plan,
            defaults={
                'status': 'active',
                'stripe_subscription_id': f'sub_test_{user.pk}',
                'current_period_end': timezone.now() + timedelta(days=30),
                'current_period_start': timezone.now()
            }
        )
        
        print(f"✅ Created/found subscription to: {middle_plan.name}")
        
        # Test API again
        response = api_view.get(request)
        data = response.data
        
        print(f"✅ Plans returned: {len(data['plans'])}")
        print(f"✅ Current plan: {data.get('current_plan')['name'] if data.get('current_plan') else 'None'}")
        
        # Check that exactly ONE plan is marked as current
        current_plans = [p for p in data['plans'] if p.get('isCurrentPlan')]
        if len(current_plans) == 1:
            print("✅ CORRECT: Exactly one plan marked as current")
            print(f"   Current plan: {current_plans[0]['name']}")
            
            # Verify it's the right plan
            if current_plans[0]['name'] == middle_plan.name:
                print("✅ CORRECT: The right plan is marked as current")
            else:
                print(f"❌ WRONG: Wrong plan marked as current")
                return False
        else:
            print(f"❌ WRONG: {len(current_plans)} plans marked as current (should be 1)")
            return False
        
        # Show all plan details
        print("\n📋 All Plans:")
        for plan in data['plans']:
            is_current = plan.get('isCurrentPlan', False)
            plan_type = plan.get('type', 'unknown')
            status_emoji = "🔥" if is_current else ("⬆️" if plan_type == 'upgrade' else "⬇️")
            print(f"   {status_emoji} {plan['name']}: ${plan['price']} ({plan_type}) - isCurrentPlan: {is_current}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ isCurrentPlan is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting isCurrentPlan Fix Test...")
    success = test_iscurrent_fix()
    
    if success:
        print("\n🎉 FIX VERIFIED!")
        print("✅ Only current plan has isCurrentPlan: true")
        print("✅ Other plans have isCurrentPlan: false")
    else:
        print("\n❌ Fix verification failed")
