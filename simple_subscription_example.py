"""
SIMPLE EXAMPLE: How to call /api/subscriptions/manage/

This script shows you exactly how to get the parameters and make the API call.
"""

import requests
import json

# Base configuration
API_BASE = "http://localhost:8000/api"

def main():
    print("🚀 SUBSCRIPTION MANAGEMENT API - COMPLETE EXAMPLE")
    print("=" * 60)
    
    # Step 1: Get JWT Token
    print("\n1️⃣ GETTING JWT TOKEN...")
    print("   Endpoint: GET /api/auth/admin-token/")
    
    try:
        response = requests.get(f"{API_BASE}/auth/admin-token/")
        if response.status_code == 200:
            token_data = response.json()
            jwt_token = token_data['access_token']
            print(f"   ✅ Success! Got JWT token: {jwt_token[:50]}...")
        else:
            print(f"   ❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Get Available Plans  
    print("\n2️⃣ GETTING AVAILABLE PLANS...")
    print("   Endpoint: GET /api/subscriptions/api/plans/")
    
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    try:
        response = requests.get(f"{API_BASE}/subscriptions/api/plans/", headers=headers)
        if response.status_code == 200:
            plans_data = response.json()
            plans = plans_data.get('plans', [])
            print(f"   ✅ Success! Found {len(plans)} plans:")
            
            for plan in plans:
                features = plan.get('features', {})
                print(f"      - {plan['name']}: {plan['id']}")
                print(f"        Price: ${plan['price']}/{plan['billing_cycle']}")
                print(f"        Features: {features.get('call_minutes_limit', 0)} min, {features.get('agents_allowed', 0)} agents")
                print()
        else:
            print(f"   ❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 3: Check Current Subscription
    print("3️⃣ CHECKING CURRENT SUBSCRIPTION...")
    print("   Endpoint: GET /api/subscriptions/manage/")
    
    try:
        response = requests.get(f"{API_BASE}/subscriptions/manage/", headers=headers)
        if response.status_code == 200:
            sub_data = response.json()
            current_sub = sub_data.get('subscription')
            
            if current_sub:
                print(f"   ✅ Found active subscription:")
                print(f"      Plan: {current_sub['plan']['name']}")
                print(f"      Status: {current_sub['status']}")
                print(f"      Period: {current_sub['current_period_start']} to {current_sub['current_period_end']}")
                has_subscription = True
            else:
                print("   📝 No active subscription found")
                has_subscription = False
        else:
            print(f"   ❌ Failed: {response.text}")
            has_subscription = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        has_subscription = False
    
    # Step 4: Show Examples
    print("\n4️⃣ EXAMPLE API CALLS FOR /api/subscriptions/manage/")
    print("=" * 60)
    
    print("\n🔧 REQUIRED HEADERS:")
    print(f'   Authorization: Bearer {jwt_token[:30]}...')
    print('   Content-Type: application/json')
    
    print("\n📝 EXAMPLE 1: CANCEL SUBSCRIPTION")
    print("   Method: POST")
    print("   URL: http://localhost:8000/api/subscriptions/manage/")
    cancel_body = {"action": "cancel"}
    print(f"   Body: {json.dumps(cancel_body, indent=6)}")
    
    print("\n📝 EXAMPLE 2: UPGRADE TO PRO PLAN")
    print("   Method: POST") 
    print("   URL: http://localhost:8000/api/subscriptions/manage/")
    
    # Find Pro plan ID
    pro_plan_id = None
    for plan in plans:
        if plan['plan_type'] == 'pro':
            pro_plan_id = plan['id']
            break
    
    if pro_plan_id:
        upgrade_body = {
            "action": "upgrade",
            "new_plan_id": pro_plan_id
        }
        print(f"   Body: {json.dumps(upgrade_body, indent=6)}")
    else:
        upgrade_body = {
            "action": "upgrade", 
            "new_plan_id": "PLAN_ID_FROM_STEP_2"
        }
        print(f"   Body: {json.dumps(upgrade_body, indent=6)}")
    
    print("\n📝 EXAMPLE 3: DOWNGRADE TO STARTER PLAN")
    print("   Method: POST")
    print("   URL: http://localhost:8000/api/subscriptions/manage/")
    
    # Find Starter plan ID
    starter_plan_id = None
    for plan in plans:
        if plan['plan_type'] == 'starter':
            starter_plan_id = plan['id']
            break
    
    if starter_plan_id:
        downgrade_body = {
            "action": "downgrade",
            "new_plan_id": starter_plan_id
        }
        print(f"   Body: {json.dumps(downgrade_body, indent=6)}")
    
    # Step 5: Show curl commands
    print("\n5️⃣ READY-TO-USE CURL COMMANDS")
    print("=" * 60)
    
    print(f"\n🔨 CANCEL SUBSCRIPTION:")
    print(f'''curl -X POST "http://localhost:8000/api/subscriptions/manage/" \\
  -H "Authorization: Bearer {jwt_token}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(cancel_body)}' ''')
    
    if pro_plan_id:
        print(f"\n🔨 UPGRADE TO PRO:")
        print(f'''curl -X POST "http://localhost:8000/api/subscriptions/manage/" \\
  -H "Authorization: Bearer {jwt_token}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(upgrade_body)}' ''')
    
    if starter_plan_id:
        print(f"\n🔨 DOWNGRADE TO STARTER:")
        print(f'''curl -X POST "http://localhost:8000/api/subscriptions/manage/" \\
  -H "Authorization: Bearer {jwt_token}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(downgrade_body)}' ''')
    
    # Bonus: Create subscription example
    print("\n6️⃣ BONUS: CREATE NEW SUBSCRIPTION")
    print("=" * 60)
    
    print("\n📝 EXAMPLE: CREATE SUBSCRIPTION")
    print("   Method: POST")
    print("   URL: http://localhost:8000/api/subscriptions/create/")
    
    if starter_plan_id:
        create_body = {
            "plan_id": starter_plan_id,
            "payment_method_id": "pm_card_visa",  # Test payment method
            "billing_cycle": "month"
        }
        print(f"   Body: {json.dumps(create_body, indent=6)}")
        
        print(f"\n🔨 CURL COMMAND:")
        print(f'''curl -X POST "http://localhost:8000/api/subscriptions/create/" \\
  -H "Authorization: Bearer {jwt_token}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(create_body)}' ''')
    
    # Summary
    print("\n📋 SUMMARY - WHAT YOU NEED")
    print("=" * 60)
    
    print(f"\n✅ JWT Token: {jwt_token[:50]}...")
    print(f"✅ Available Plan IDs:")
    for plan in plans:
        print(f"   - {plan['name']} ({plan['plan_type']}): {plan['id']}")
    
    print(f"\n🔧 For /api/subscriptions/manage/:")
    print(f"   - action: 'upgrade', 'downgrade', or 'cancel'")
    print(f"   - new_plan_id: Required for upgrade/downgrade (use IDs above)")
    
    print(f"\n🔧 For /api/subscriptions/create/:")
    print(f"   - plan_id: Use any plan ID from above")
    print(f"   - payment_method_id: Use 'pm_card_visa' for testing")
    
    print(f"\n🌐 Test in Browser:")
    print(f"   - Swagger UI: http://localhost:8000/swagger/")
    print(f"   - Admin Panel: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()
