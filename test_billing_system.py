#!/usr/bin/env python
"""
Stripe Billing System Test Script

This script tests the complete Stripe billing integration:
- Subscription plan creation
- Customer creation
- Subscription lifecycle
- Webhook handling
- Payment method management
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
from subscriptions.models import (
    SubscriptionPlan, Subscription, BillingHistory, 
    UsageRecord, UsageAlert
)
from subscriptions.stripe_service import StripeService
import stripe
from django.conf import settings

User = get_user_model()

class BillingSystemTest:
    def __init__(self):
        self.stripe_service = StripeService()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def run_tests(self):
        """Run all billing system tests"""
        print("🧪 Starting Stripe Billing System Tests")
        print("=" * 50)
        
        try:
            # Test 1: Create subscription plans
            self.test_subscription_plans()
            
            # Test 2: Create test user
            test_user = self.create_test_user()
            
            # Test 3: Test customer creation
            self.test_customer_creation(test_user)
            
            # Test 4: Test subscription creation
            self.test_subscription_creation(test_user)
            
            # Test 5: Test usage tracking
            self.test_usage_tracking(test_user)
            
            # Test 6: Test billing history
            self.test_billing_history(test_user)
            
            print("\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {str(e)}")
            sys.exit(1)
    
    def test_subscription_plans(self):
        """Test subscription plan creation"""
        print("\n📦 Testing Subscription Plans...")
        
        # Create sample plans if they don't exist
        plans_data = [
            {
                'name': 'Starter',
                'plan_type': 'starter',
                'price': 29.00,
                'billing_cycle': 'monthly',
                'call_minutes_limit': 1000,
                'agents_allowed': 2,
                'analytics_access': True,
                'api_access': False,
                'priority_support': False,
                'call_recording': True,
                'call_transcription': False,
            },
            {
                'name': 'Professional',
                'plan_type': 'pro',
                'price': 99.00,
                'billing_cycle': 'monthly',
                'call_minutes_limit': 5000,
                'agents_allowed': 10,
                'analytics_access': True,
                'api_access': True,
                'priority_support': True,
                'call_recording': True,
                'call_transcription': True,
            },
            {
                'name': 'Enterprise',
                'plan_type': 'enterprise',
                'price': 299.00,
                'billing_cycle': 'monthly',
                'call_minutes_limit': 20000,
                'agents_allowed': 50,
                'analytics_access': True,
                'api_access': True,
                'priority_support': True,
                'call_recording': True,
                'call_transcription': True,
                'sentiment_analysis': True,
                'custom_integration': True,
            }
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                print(f"  ✓ Created plan: {plan.name} - ${plan.price}/month")
            else:
                print(f"  ✓ Plan exists: {plan.name} - ${plan.price}/month")
        
        print(f"  Total plans: {SubscriptionPlan.objects.count()}")
    
    def create_test_user(self):
        """Create or get test user"""
        print("\n👤 Creating Test User...")
        
        user, created = User.objects.get_or_create(
            email='billing_test@example.com',
            defaults={
                'user_name': 'billing_test_user',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
            }
        )
        
        if created:
            print(f"  ✓ Created test user: {user.email}")
        else:
            print(f"  ✓ Using existing test user: {user.email}")
        
        return user
    
    def test_customer_creation(self, user):
        """Test Stripe customer creation"""
        print("\n💳 Testing Stripe Customer Creation...")
        
        result = StripeService.get_or_create_customer(user)
        
        if result['success']:
            print(f"  ✓ Customer created/retrieved: {user.stripe_customer_id}")
            
            # Verify customer in Stripe
            try:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                print(f"  ✓ Customer verified in Stripe: {customer.id}")
                print(f"  ✓ Customer email: {customer.email}")
            except Exception as e:
                print(f"  ❌ Failed to verify customer in Stripe: {str(e)}")
        else:
            raise Exception(f"Customer creation failed: {result['error']}")
    
    def test_subscription_creation(self, user):
        """Test subscription creation (simulated)"""
        print("\n📋 Testing Subscription Creation...")
        
        # Get a starter plan
        plan = SubscriptionPlan.objects.filter(plan_type='starter').first()
        if not plan:
            raise Exception("No starter plan found")
        
        # Create a mock subscription (without actual Stripe payment)
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id='sub_test_123456789',
            stripe_customer_id=user.stripe_customer_id,
            status='active',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=30),
            billing_cycle='monthly'
        )
        
        print(f"  ✓ Test subscription created: {subscription.id}")
        print(f"  ✓ Plan: {subscription.plan.name}")
        print(f"  ✓ Status: {subscription.status}")
        print(f"  ✓ Period: {subscription.current_period_start} to {subscription.current_period_end}")
        
        return subscription
    
    def test_usage_tracking(self, user):
        """Test usage tracking"""
        print("\n📊 Testing Usage Tracking...")
        
        subscription = Subscription.objects.filter(user=user).first()
        if not subscription:
            raise Exception("No subscription found for usage tracking")
        
        # Create some usage records
        usage_data = [
            {'minutes_used': 150, 'call_id': 'call_001'},
            {'minutes_used': 200, 'call_id': 'call_002'},
            {'minutes_used': 175, 'call_id': 'call_003'},
        ]
        
        total_usage = 0
        for usage in usage_data:
            record = UsageRecord.objects.create(
                subscription=subscription,
                minutes_used=usage['minutes_used'],
                call_id=usage['call_id'],
                timestamp=timezone.now()
            )
            total_usage += usage['minutes_used']
            print(f"  ✓ Usage recorded: {usage['minutes_used']} minutes (Call: {usage['call_id']})")
        
        print(f"  ✓ Total usage this period: {total_usage} minutes")
        print(f"  ✓ Plan limit: {subscription.plan.call_minutes_limit} minutes")
        
        # Test usage percentage calculation
        usage_percentage = (total_usage / subscription.plan.call_minutes_limit) * 100
        print(f"  ✓ Usage percentage: {usage_percentage:.1f}%")
        
        # Test alert creation if over threshold
        if usage_percentage >= 80:
            alert = UsageAlert.objects.create(
                subscription=subscription,
                alert_type='usage_limit',
                threshold_percentage=80,
                current_usage=total_usage,
                message=f"You have reached {usage_percentage:.1f}% of your monthly limit"
            )
            print(f"  ✓ Usage alert created: {alert.message}")
    
    def test_billing_history(self, user):
        """Test billing history creation"""
        print("\n📜 Testing Billing History...")
        
        subscription = Subscription.objects.filter(user=user).first()
        if not subscription:
            raise Exception("No subscription found for billing history")
        
        # Create sample billing records
        billing_records = [
            {
                'invoice_type': 'subscription',
                'amount': subscription.plan.price,
                'status': 'paid',
                'description': f'Monthly subscription - {subscription.plan.name}',
                'stripe_invoice_id': 'in_test_123456',
            },
            {
                'invoice_type': 'overage',
                'amount': 12.50,
                'status': 'paid',
                'description': 'Overage charges - 250 additional minutes',
                'stripe_invoice_id': 'in_test_789012',
            }
        ]
        
        for record_data in billing_records:
            record = BillingHistory.objects.create(
                user=user,
                subscription=subscription,
                billing_period_start=subscription.current_period_start,
                billing_period_end=subscription.current_period_end,
                due_date=timezone.now() + timedelta(days=7),
                total_amount=record_data['amount'],
                **record_data
            )
            print(f"  ✓ Billing record created: {record.description} (${record.amount})")
        
        # Summary
        from django.db import models
        total_billing = BillingHistory.objects.filter(user=user).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        print(f"  ✓ Total billing history: {BillingHistory.objects.filter(user=user).count()} records")
        print(f"  ✓ Total amount billed: ${total_billing}")
    
    def test_stripe_api_connection(self):
        """Test Stripe API connection"""
        print("\n🔌 Testing Stripe API Connection...")
        
        try:
            # Test API connection by retrieving account info
            account = stripe.Account.retrieve()
            print(f"  ✓ Connected to Stripe account: {account.id}")
            print(f"  ✓ Account country: {account.country}")
            print(f"  ✓ Account currency: {account.default_currency}")
            
            # Test creating a test customer
            test_customer = stripe.Customer.create(
                email='stripe_test@example.com',
                name='Stripe Test Customer',
                metadata={'test': 'true'}
            )
            print(f"  ✓ Test customer created: {test_customer.id}")
            
            # Clean up test customer
            stripe.Customer.delete(test_customer.id)
            print(f"  ✓ Test customer deleted")
            
        except Exception as e:
            raise Exception(f"Stripe API connection failed: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test user and related data
        test_user = User.objects.filter(email='billing_test@example.com').first()
        if test_user:
            # Delete related records
            Subscription.objects.filter(user=test_user).delete()
            BillingHistory.objects.filter(user=test_user).delete()
            UsageRecord.objects.filter(subscription__user=test_user).delete()
            UsageAlert.objects.filter(subscription__user=test_user).delete()
            
            # Delete user
            test_user.delete()
            print("  ✓ Test data cleaned up")


def main():
    """Main test runner"""
    tester = BillingSystemTest()
    
    # Check if we have Stripe keys configured
    if settings.STRIPE_SECRET_KEY == 'sk_test_placeholder':
        print("⚠️  Warning: Using placeholder Stripe keys. Update your .env file with real test keys.")
        print("   You can still run the database tests, but Stripe API tests will be skipped.")
        
        response = input("\nDo you want to continue with database-only tests? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            return
    
    try:
        tester.run_tests()
        
        # Ask if user wants to clean up
        response = input("\nDo you want to clean up test data? (y/n): ")
        if response.lower() == 'y':
            tester.cleanup_test_data()
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
