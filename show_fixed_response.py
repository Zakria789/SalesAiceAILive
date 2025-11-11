#!/usr/bin/env python
"""
Test the API response format to show the fixed response
"""
import os
import sys
import django
from datetime import timedelta
import json

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

def show_fixed_response():
    """Show the corrected API response"""
    print("🎯 CORRECTED API RESPONSE")
    print("=" * 50)
    
    try:
        # Get test user with subscription
        User = get_user_model()
        user = User.objects.filter(user_name='testuser_fix').first()
        if not user:
            print("❌ Test user not found")
            return False
        
        # Get API response
        api_view = UserPlansComparisonAPIView()
        request = create_mock_request(user)
        response = api_view.get(request)
        data = response.data
        
        print("📋 FIXED RESPONSE (JSON formatted):")
        print(json.dumps(data, indent=2, default=str))
        
        print("\n🔍 VERIFICATION:")
        current_count = sum(1 for plan in data['plans'] if plan.get('isCurrentPlan'))
        print(f"✅ Plans with isCurrentPlan=true: {current_count} (should be 1)")
        
        if data.get('current_plan'):
            current_plan_name = data['current_plan']['name']
            print(f"✅ Current plan highlighted: {current_plan_name}")
        
        print("\n📋 PLAN BREAKDOWN:")
        for plan in data['plans']:
            is_current = plan.get('isCurrentPlan', False)
            plan_type = plan.get('type', 'unknown')
            status = "CURRENT" if is_current else plan_type.upper()
            print(f"   • {plan['name']}: ${plan['price']} - {status} (isCurrentPlan: {is_current})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    show_fixed_response()
