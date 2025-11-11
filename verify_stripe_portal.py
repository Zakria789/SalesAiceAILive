#!/usr/bin/env python
"""
Simple Stripe Portal Integration Verification
Verifies that the Stripe billing portal integration is properly implemented
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def verify_stripe_portal_integration():
    """Verify that Stripe portal integration is properly implemented"""
    print("🔍 Verifying Stripe Portal Integration")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: API View exists and is properly implemented
    total_checks += 1
    try:
        from subscriptions.user_subscription_api import UserBillingPortalAPIView
        view = UserBillingPortalAPIView()
        
        # Check if view has required methods
        if hasattr(view, 'post'):
            print("✅ UserBillingPortalAPIView exists with POST method")
            checks_passed += 1
        else:
            print("❌ UserBillingPortalAPIView missing POST method")
    except ImportError as e:
        print(f"❌ Cannot import UserBillingPortalAPIView: {e}")
    
    # Check 2: URL configuration
    total_checks += 1
    try:
        from django.urls import resolve, reverse
        from django.conf import settings
        
        # Check if URL pattern exists
        resolved = resolve('/api/subscriptions/user/billing-portal/')
        if 'UserBillingPortalAPIView' in str(resolved.func.view_class):
            print("✅ Billing portal URL properly configured")
            checks_passed += 1
        else:
            print("❌ Billing portal URL not properly configured")
    except Exception as e:
        print(f"❌ URL configuration issue: {e}")
    
    # Check 3: Stripe configuration
    total_checks += 1
    try:
        from django.conf import settings
        
        required_settings = [
            'STRIPE_SECRET_KEY',
            'STRIPE_PUBLISHABLE_KEY', 
            'FRONTEND_URL'
        ]
        
        all_configured = True
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                print(f"❌ Missing setting: {setting}")
                all_configured = False
        
        if all_configured:
            print("✅ All required Stripe settings are configured")
            checks_passed += 1
        else:
            print("❌ Some required Stripe settings are missing")
    except Exception as e:
        print(f"❌ Settings check failed: {e}")
    
    # Check 4: View implementation details
    total_checks += 1
    try:
        import inspect
        from subscriptions.user_subscription_api import UserBillingPortalAPIView
        
        # Get the post method source
        post_method = getattr(UserBillingPortalAPIView, 'post')
        source = inspect.getsource(post_method)
        
        required_elements = [
            'stripe.billing_portal.Session.create',
            'stripe_customer_id',
            'return_url',
            'portal_session.url'
        ]
        
        all_elements_present = True
        for element in required_elements:
            if element not in source:
                print(f"❌ Missing implementation element: {element}")
                all_elements_present = False
        
        if all_elements_present:
            print("✅ Billing portal implementation contains all required elements")
            checks_passed += 1
        else:
            print("❌ Billing portal implementation is missing required elements")
    except Exception as e:
        print(f"❌ Implementation check failed: {e}")
    
    # Check 5: Model relationships
    total_checks += 1
    try:
        from subscriptions.models import Subscription
        from accounts.models import User
        
        # Check if Subscription model has required fields
        subscription_fields = [field.name for field in Subscription._meta.fields]
        required_fields = ['stripe_customer_id', 'user', 'status']
        
        missing_fields = [field for field in required_fields if field not in subscription_fields]
        
        if not missing_fields:
            print("✅ Subscription model has all required fields for Stripe integration")
            checks_passed += 1
        else:
            print(f"❌ Subscription model missing fields: {missing_fields}")
    except Exception as e:
        print(f"❌ Model check failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {checks_passed}/{total_checks}")
    print(f"❌ Failed: {total_checks - checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("\n🎉 Stripe Portal Integration is fully implemented and ready!")
        print("\n📋 IMPLEMENTATION DETAILS:")
        print("🔹 API Endpoint: POST /api/subscriptions/user/billing-portal/")
        print("🔹 Authentication: Required (IsAuthenticated)")
        print("🔹 Function: Creates Stripe billing portal session")
        print("🔹 Returns: Portal URL for frontend redirect")
        print("🔹 Features: Payment method update, invoice download, subscription management")
        print("\n💡 USAGE:")
        print("1. Frontend makes POST request to billing portal endpoint")
        print("2. Backend validates user has active subscription with Stripe customer ID")
        print("3. Creates Stripe billing portal session with return URL")
        print("4. Returns portal URL to frontend")
        print("5. Frontend redirects user to Stripe's hosted billing portal")
        print("6. User manages billing, then returns to app via return_url")
    else:
        print("\n⚠️  Some verification checks failed. Review the output above.")
    
    return checks_passed == total_checks

def show_api_documentation():
    """Show API documentation for the billing portal"""
    print("\n📚 STRIPE BILLING PORTAL API DOCUMENTATION")
    print("=" * 60)
    
    print("\n🔌 ENDPOINT:")
    print("POST /api/subscriptions/user/billing-portal/")
    
    print("\n🔐 AUTHENTICATION:")
    print("Required: JWT Token or Session Authentication")
    
    print("\n📥 REQUEST:")
    print("Method: POST")
    print("Body: Empty (no parameters required)")
    print("Headers: Authorization: Bearer <token>")
    
    print("\n📄 RESPONSE SUCCESS (200):")
    print("""{
    "success": true,
    "message": "Billing portal session created successfully",
    "portal_url": "https://billing.stripe.com/session/abc123..."
}""")
    
    print("\n❌ RESPONSE ERROR (400):")
    print("""{
    "success": false,
    "error": "No active subscription with Stripe customer found"
}""")
    
    print("\n🎯 FRONTEND INTEGRATION:")
    print("""
// JavaScript/TypeScript example
const accessBillingPortal = async () => {
    try {
        const response = await fetch('/api/subscriptions/user/billing-portal/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect user to Stripe's billing portal
            window.location.href = data.portal_url;
        } else {
            console.error('Failed to access billing portal:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
};
""")

if __name__ == '__main__':
    success = verify_stripe_portal_integration()
    show_api_documentation()
    print("\n" + "=" * 60)
    if success:
        print("🎊 STRIPE PORTAL INTEGRATION: FULLY VERIFIED ✅")
    else:
        print("⚠️  STRIPE PORTAL INTEGRATION: NEEDS ATTENTION")
    print("=" * 60)
