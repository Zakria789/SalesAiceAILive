"""
Comprehensive Guide: How to Obtain Parameters for Subscription Management API

This script demonstrates how to get the required parameters for:
1. /api/subscriptions/manage/ - Subscription management endpoint
2. /api/subscriptions/create/ - Subscription creation endpoint

Run this script to understand what parameters you need and how to get them.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")
    print("-" * 50)

def get_jwt_token(email="admin@testcenter.com", password="admin123"):
    """Get JWT token for API authentication"""
    try:
        # Try admin token (GET method)
        response = requests.get(f"{API_BASE}/auth/admin-token/")
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        
        # Try quick token (POST method) 
        response = requests.post(f"{API_BASE}/auth/quick-token/", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def get_subscription_plans(token):
    """Get available subscription plans with their IDs"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/subscriptions/api/plans/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get plans: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting plans: {e}")
        return None

def get_current_subscription(token):
    """Get current user's subscription details"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/subscriptions/manage/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get subscription: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting subscription: {e}")
        return None

def main():
    print_section("SUBSCRIPTION MANAGEMENT API PARAMETER GUIDE")
    
    print("""
This guide shows you how to obtain the required parameters for:
- /api/subscriptions/manage/ (Subscription management)
- /api/subscriptions/create/ (Create new subscription)
    """)
    
    # Step 1: Get JWT Token
    print_step(1, "GET JWT TOKEN FOR AUTHENTICATION")
    print("Before using any subscription API, you need a JWT token.")
    print("\nMethod 1 - Admin Token:")
    print("GET /api/auth/admin-token/")
    print("No body required - uses existing admin user")
    
    print("\nMethod 2 - Quick Token (for any user):")
    print("POST /api/auth/quick-token/")
    print('Body: {"email": "user@example.com", "password": "userpassword"}')
    
    token = get_jwt_token()
    if not token:
        print("\n❌ Could not get JWT token. Make sure the server is running and admin user exists.")
        return
    
    print(f"\n✅ Got JWT Token: {token[:50]}...")
    
    # Step 2: Get Available Plans
    print_step(2, "GET AVAILABLE SUBSCRIPTION PLANS")
    print("To create or change subscriptions, you need plan IDs.")
    print("\nEndpoint: GET /api/subscriptions/api/plans/")
    print("Headers: Authorization: Bearer <your_jwt_token>")
    
    plans_data = get_subscription_plans(token)
    if plans_data and plans_data.get('success'):
        plans = plans_data.get('plans', [])
        print(f"\n✅ Found {len(plans)} available plans:")
        
        for plan in plans:
            print(f"\n📦 Plan: {plan['name']}")
            print(f"   ID: {plan['id']}")
            print(f"   Type: {plan['plan_type']}")
            print(f"   Price: ${plan['price']}/{plan['billing_cycle']}")
            features = plan.get('features', {})
            print(f"   Features: {features.get('call_minutes_limit', 0)} minutes, {features.get('agents_allowed', 0)} agents")
    else:
        print("\n❌ Could not get subscription plans")
        return
    
    # Step 3: Check Current Subscription
    print_step(3, "CHECK CURRENT SUBSCRIPTION STATUS")
    print("Check if user already has an active subscription.")
    print("\nEndpoint: GET /api/subscriptions/manage/")
    print("Headers: Authorization: Bearer <your_jwt_token>")
    
    current_sub = get_current_subscription(token)
    if current_sub and current_sub.get('success'):
        subscription = current_sub.get('subscription')
        if subscription:
            print(f"\n✅ Found active subscription:")
            print(f"   Plan: {subscription['plan']['name']}")
            print(f"   Status: {subscription['status']}")
            print(f"   Period: {subscription['current_period_start']} to {subscription['current_period_end']}")
            print(f"   Usage: {subscription['usage']}")
        else:
            print("\n📝 No active subscription found")
    
    # Step 4: Subscription Management Parameters
    print_step(4, "SUBSCRIPTION MANAGEMENT API PARAMETERS")
    print("\nEndpoint: POST /api/subscriptions/manage/")
    print("Headers: Authorization: Bearer <your_jwt_token>")
    print("Content-Type: application/json")
    
    print("\n🔧 REQUIRED PARAMETERS:")
    print("action: One of ['upgrade', 'downgrade', 'cancel']")
    
    print("\n🔧 CONDITIONAL PARAMETERS:")
    print("new_plan_id: Required when action is 'upgrade' or 'downgrade'")
    print("             Use the plan ID from step 2 above")
    
    print("\n📝 EXAMPLE REQUESTS:")
    
    # Cancel subscription example
    print("\n1️⃣ Cancel Subscription:")
    cancel_example = {
        "action": "cancel"
    }
    print(f"Body: {json.dumps(cancel_example, indent=2)}")
    
    # Upgrade/Downgrade example
    if plans_data and plans_data.get('success') and plans_data.get('plans'):
        plan_id = plans_data['plans'][0]['id']
        print(f"\n2️⃣ Upgrade/Downgrade Subscription:")
        upgrade_example = {
            "action": "upgrade",
            "new_plan_id": plan_id
        }
        print(f"Body: {json.dumps(upgrade_example, indent=2)}")
    
    # Step 5: Create Subscription Parameters
    print_step(5, "CREATE SUBSCRIPTION API PARAMETERS")
    print("\nEndpoint: POST /api/subscriptions/create/")
    print("Headers: Authorization: Bearer <your_jwt_token>")
    print("Content-Type: application/json")
    
    print("\n🔧 REQUIRED PARAMETERS:")
    print("plan_id: The subscription plan ID (from step 2)")
    print("payment_method_id: Stripe payment method ID")
    
    print("\n🔧 OPTIONAL PARAMETERS:")
    print("billing_cycle: 'month' or 'year' (defaults to plan's billing cycle)")
    
    print("\n💳 HOW TO GET PAYMENT METHOD ID:")
    print("Option 1: Use Stripe Elements in your frontend to collect payment")
    print("Option 2: Use Stripe Dashboard to create test payment methods")
    print("Option 3: Use Stripe CLI for testing: stripe payment_methods create --type=card")
    print("Option 4: For testing, use: 'pm_card_visa' (Stripe test payment method)")
    
    if plans_data and plans_data.get('success') and plans_data.get('plans'):
        plan_id = plans_data['plans'][0]['id']
        print(f"\n📝 EXAMPLE CREATE SUBSCRIPTION REQUEST:")
        create_example = {
            "plan_id": plan_id,
            "payment_method_id": "pm_card_visa",  # Test payment method
            "billing_cycle": "month"
        }
        print(f"Body: {json.dumps(create_example, indent=2)}")
    
    # Step 6: Complete Usage Example
    print_step(6, "COMPLETE USAGE EXAMPLE WITH CURL")
    
    print("\n🚀 Complete workflow example:")
    print("\n# 1. Get JWT Token")
    print(f'curl -X GET "{API_BASE}/auth/admin-token/"')
    
    print("\n# 2. Get Available Plans")
    print(f'curl -X GET "{API_BASE}/subscriptions/api/plans/" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN"')
    
    print("\n# 3. Check Current Subscription")
    print(f'curl -X GET "{API_BASE}/subscriptions/manage/" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN"')
    
    print("\n# 4. Create New Subscription")
    print(f'curl -X POST "{API_BASE}/subscriptions/create/" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"plan_id": "PLAN_ID_FROM_STEP_2", "payment_method_id": "pm_card_visa"}\'')
    
    print("\n# 5. Manage Subscription (Upgrade)")
    print(f'curl -X POST "{API_BASE}/subscriptions/manage/" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"action": "upgrade", "new_plan_id": "NEW_PLAN_ID"}\'')
    
    print("\n# 6. Cancel Subscription")
    print(f'curl -X POST "{API_BASE}/subscriptions/manage/" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"action": "cancel"}\'')
    
    print_section("SUMMARY")
    print("""
✅ WHAT YOU NEED:

For /api/subscriptions/manage/:
- JWT Token (from /api/auth/admin-token/ or /api/auth/quick-token/)
- action: 'upgrade', 'downgrade', or 'cancel'
- new_plan_id: Only required for upgrade/downgrade (get from /api/subscriptions/api/plans/)

For /api/subscriptions/create/:
- JWT Token
- plan_id: Get from /api/subscriptions/api/plans/
- payment_method_id: Use 'pm_card_visa' for testing or create via Stripe

🔗 HELPFUL ENDPOINTS:
- GET /api/auth/quick-token/ - Quick test token
- GET /api/subscriptions/api/plans/ - List all plans with IDs
- GET /api/subscriptions/manage/ - Check current subscription
- Swagger UI: http://localhost:8000/swagger/ - Interactive API docs
    """)

if __name__ == "__main__":
    main()
