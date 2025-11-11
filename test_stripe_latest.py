#!/usr/bin/env python
"""
Test script for Stripe current_period_start error in latest versions
"""
import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

import stripe
from django.conf import settings
from subscriptions.models import SubscriptionPlan
from django.contrib.auth import get_user_model
from datetime import datetime, timezone as dt_timezone

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

def test_stripe_subscription_creation():
    """Test subscription creation with latest Stripe version"""
    print("🧪 Testing Stripe Subscription Creation with Latest Version...")
    try:
        print(f"📦 Stripe Version: {stripe.version.VERSION}")
    except:
        print("📦 Stripe Version: Latest")
    
    try:
        # Get test data
        user = User.objects.filter(email__icontains='test').first()
        if not user:
            print("❌ No test user found")
            return False
            
        package = SubscriptionPlan.objects.filter(plan_type='pro').first()
        if not package:
            print("❌ No Pro package found")
            return False
            
        print(f"✅ Test User: {user.email}")
        print(f"✅ Test Package: {package.name} - ${package.price}")
        
        # Create Stripe customer
        stripe_customer = stripe.Customer.create(
            email=f"test_{user.id}@example.com",
            name=f"Test User {user.id}",
        )
        print(f"✅ Stripe Customer Created: {stripe_customer.id}")
        
        # Create subscription 
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer.id,
            items=[{'price': package.stripe_price_id}],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )
        
        print(f"✅ Stripe Subscription Created: {stripe_subscription.id}")
        print(f"📊 Status: {stripe_subscription.status}")
        
        # Test timestamp access (this is where the error happens)
        print("\n🔍 Testing Timestamp Access...")
        
        # Safe timestamp checking
        print(f"current_period_start exists: {hasattr(stripe_subscription, 'current_period_start')}")
        print(f"current_period_end exists: {hasattr(stripe_subscription, 'current_period_end')}")
        
        if hasattr(stripe_subscription, 'current_period_start'):
            print(f"current_period_start value: {stripe_subscription.current_period_start}")
            print(f"current_period_start type: {type(stripe_subscription.current_period_start)}")
            
        if hasattr(stripe_subscription, 'current_period_end'):
            print(f"current_period_end value: {stripe_subscription.current_period_end}")
            print(f"current_period_end type: {type(stripe_subscription.current_period_end)}")
        
        # Test datetime conversion
        try:
            if stripe_subscription.current_period_start:
                period_start = datetime.fromtimestamp(stripe_subscription.current_period_start, tz=dt_timezone.utc)
                print(f"✅ Period Start Conversion: {period_start}")
            else:
                print("⚠️ current_period_start is None/empty")
                
            if stripe_subscription.current_period_end:
                period_end = datetime.fromtimestamp(stripe_subscription.current_period_end, tz=dt_timezone.utc)
                print(f"✅ Period End Conversion: {period_end}")
            else:
                print("⚠️ current_period_end is None/empty")
                
        except Exception as ts_error:
            print(f"❌ Timestamp Conversion Error: {str(ts_error)}")
            return False
        
        # Test client_secret access
        print("\n🔍 Testing Client Secret Access...")
        try:
            if hasattr(stripe_subscription, 'latest_invoice'):
                print(f"latest_invoice exists: {stripe_subscription.latest_invoice is not None}")
                
                if stripe_subscription.latest_invoice:
                    invoice = stripe_subscription.latest_invoice
                    print(f"latest_invoice type: {type(invoice)}")
                    
                    if hasattr(invoice, 'payment_intent'):
                        print(f"payment_intent exists: {invoice.payment_intent is not None}")
                        
                        if invoice.payment_intent:
                            pi = invoice.payment_intent
                            print(f"payment_intent type: {type(pi)}")
                            
                            if hasattr(pi, 'client_secret'):
                                print(f"✅ Client Secret: {pi.client_secret[:20]}...")
                            else:
                                print("⚠️ client_secret not found")
                        else:
                            print("⚠️ payment_intent is None")
                    else:
                        print("⚠️ payment_intent attribute missing")
                else:
                    print("⚠️ latest_invoice is None")
            else:
                print("⚠️ latest_invoice attribute missing")
                
        except Exception as cs_error:
            print(f"❌ Client Secret Access Error: {str(cs_error)}")
        
        # Cleanup
        try:
            stripe.Subscription.delete(stripe_subscription.id)
            stripe.Customer.delete(stripe_customer.id)
            print("🧹 Cleanup completed")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        return False

def main():
    """Run the test"""
    print("🚀 Stripe Latest Version Compatibility Test")
    print("=" * 50)
    
    success = test_stripe_subscription_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test Passed! Stripe integration working with latest version.")
    else:
        print("❌ Test Failed! Issues found with latest Stripe version.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
