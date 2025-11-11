#!/usr/bin/env python
"""
Test script to verify client_secret extraction fix
"""
import os
import django
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import stripe
from subscriptions.models import SubscriptionPlan

def test_client_secret_fix():
    """Test the client_secret extraction with your specific data"""
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if not stripe.api_key:
        print("❌ STRIPE_SECRET_KEY not found in environment")
        return
    
    print(f"🔑 Using Stripe API Key: {stripe.api_key[:12]}...")
    
    # Your specific test data
    package_id = "a020bb71-024d-43d0-a5d3-8ca06cc23df5"
    payment_method_id = "pm_1SFI33AMrH3m7b2GANTcUWFW"
    
    try:
        # Get the package
        package = SubscriptionPlan.objects.get(id=package_id)
        print(f"📦 Package found: {package.name}")
        print(f"💰 Price: ${package.price}")
        print(f"🏷️ Stripe Price ID: {package.stripe_price_id}")
        
        # Create test customer
        test_customer = stripe.Customer.create(
            email="test@example.com",
            name="Test User"
        )
        print(f"👤 Test customer: {test_customer.id}")
        
        # Attach payment method to customer
        if payment_method_id:
            try:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=test_customer.id
                )
                print(f"💳 Payment method attached: {payment_method_id}")
            except Exception as pm_error:
                print(f"⚠️ Payment method attach failed: {str(pm_error)}")
        
        # Test 1: Create subscription with payment_behavior='default_incomplete'
        print("\n🧪 Test 1: Creating subscription with default_incomplete...")
        subscription_params = {
            'customer': test_customer.id,
            'items': [{'price': package.stripe_price_id}],
            'payment_behavior': 'default_incomplete',
            'payment_settings': {'save_default_payment_method': 'on_subscription'},
            'expand': ['latest_invoice.payment_intent'],
        }
        
        if payment_method_id:
            subscription_params['default_payment_method'] = payment_method_id
        
        stripe_subscription = stripe.Subscription.create(**subscription_params)
        print(f"✅ Subscription created: {stripe_subscription.id}")
        print(f"📊 Status: {stripe_subscription.status}")
        
        # Extract client_secret
        client_secret = None
        if hasattr(stripe_subscription, 'latest_invoice') and stripe_subscription.latest_invoice:
            latest_invoice = stripe_subscription.latest_invoice
            if hasattr(latest_invoice, 'payment_intent') and latest_invoice.payment_intent:
                payment_intent = latest_invoice.payment_intent
                client_secret = getattr(payment_intent, 'client_secret', None)
                print(f"✅ Client secret from subscription: {client_secret[:20]}..." if client_secret else "❌ No client_secret")
        
        # Test 2: Manual PaymentIntent creation if needed
        if not client_secret:
            print("\n🧪 Test 2: Creating manual PaymentIntent...")
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(float(package.price) * 100),
                    currency='usd',
                    customer=test_customer.id,
                    payment_method=payment_method_id if payment_method_id else None,
                    confirmation_method='automatic',  # Changed to automatic
                    confirm=False,
                    setup_future_usage='off_session'
                )
                client_secret = payment_intent.client_secret
                print(f"✅ Manual PaymentIntent: {payment_intent.id}")
                print(f"✅ Client secret: {client_secret[:20]}...")
            except Exception as pi_error:
                print(f"❌ Manual PaymentIntent failed: {str(pi_error)}")
        
        # Test 3: SetupIntent fallback
        if not client_secret:
            print("\n🧪 Test 3: Creating SetupIntent fallback...")
            try:
                setup_intent = stripe.SetupIntent.create(
                    customer=test_customer.id,
                    payment_method=payment_method_id if payment_method_id else None,
                    payment_method_types=['card'],
                    usage='off_session',
                    confirm=False
                )
                client_secret = setup_intent.client_secret
                print(f"✅ SetupIntent: {setup_intent.id}")
                print(f"✅ Client secret: {client_secret[:20]}...")
            except Exception as si_error:
                print(f"❌ SetupIntent failed: {str(si_error)}")
        
        # Final result
        print(f"\n🎯 Final client_secret: {'✅ SUCCESS' if client_secret else '❌ FAILED'}")
        if client_secret:
            print(f"🔑 Client secret: {client_secret[:30]}...")
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        stripe.Customer.delete(test_customer.id)
        print("✅ Cleanup complete")
        
    except SubscriptionPlan.DoesNotExist:
        print(f"❌ Package not found: {package_id}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_client_secret_fix()
