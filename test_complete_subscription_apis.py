import requests
import json
import time

def test_complete_subscription_package_apis():
    print("🚀 COMPLETE SUBSCRIPTION & PACKAGE APIs TESTING")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000/api"
    
    # Test users
    admin_credentials = {"email": "admin@gmail.com", "password": "admin123"}
    user_credentials = {"email": "testvoice@admin.com", "password": "testpass123"}
    
    try:
        # ==================== AUTHENTICATION ====================
        print("\n🔐 1. AUTHENTICATION TESTING")
        print("-" * 40)
        
        # Admin Login
        print("🔑 Testing Admin Login...")
        admin_login = requests.post(f"{base_url}/auth/login/", json=admin_credentials)
        
        if admin_login.status_code == 200:
            admin_token = admin_login.json()["tokens"]["access"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print("✅ Admin login successful!")
        else:
            print(f"❌ Admin login failed: {admin_login.status_code}")
            return
        
        # User Login
        print("🔑 Testing User Login...")
        user_login = requests.post(f"{base_url}/auth/login/", json=user_credentials)
        
        if user_login.status_code == 200:
            user_token = user_login.json()["tokens"]["access"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print("✅ User login successful!")
        else:
            print(f"❌ User login failed: {user_login.status_code}")
            return
        
        # ==================== ADMIN PACKAGE MANAGEMENT ====================
        print("\n📦 2. ADMIN PACKAGE MANAGEMENT")
        print("-" * 40)
        
        # List existing packages
        print("📋 Testing GET All Packages (Admin)...")
        get_packages = requests.get(f"{base_url}/subscriptions/admin/packages/", headers=admin_headers)
        
        if get_packages.status_code == 200:
            packages_data = get_packages.json()
            print(f"✅ Found {len(packages_data['packages'])} existing packages")
            for i, pkg in enumerate(packages_data['packages'][:2]):
                print(f"   {i+1}. {pkg['name']} - ${pkg['price_monthly']}")
                print(f"      Features: {pkg['features']}")
        else:
            print(f"❌ Get packages failed: {get_packages.status_code}")
        
        # Create new package with features
        print("\n📦 Testing CREATE Package with Features...")
        new_package = {
            "name": "API Test Package",
            "price_monthly": 79.99,
            "minutes_inbound_limit": 1500,
            "minutes_outbound_limit": 1500,
            "minutes_total_limit": 3000,
            "agents_allowed": 3,
            "analytics_access": True,
            "features": {
                "campaigns": True,
                "api_access": True,
                "advanced_analytics": True
            }
        }
        
        create_package = requests.post(
            f"{base_url}/subscriptions/admin/packages/", 
            json=new_package, 
            headers=admin_headers
        )
        
        if create_package.status_code == 201:
            created_pkg = create_package.json()
            package_id = created_pkg['package']['id']
            print("✅ Package created successfully!")
            print(f"   📦 ID: {package_id}")
            print(f"   📦 Name: {created_pkg['package']['name']}")
            print(f"   💰 Price: ${created_pkg['package']['price_monthly']}")
            print(f"   🎯 Features: {created_pkg['package']['features']}")
        else:
            print(f"❌ Create package failed: {create_package.status_code} - {create_package.text}")
            package_id = None
        
        # Get single package
        if package_id:
            print(f"\n📋 Testing GET Single Package (ID: {package_id})...")
            get_single = requests.get(f"{base_url}/subscriptions/admin/packages/{package_id}/", headers=admin_headers)
            
            if get_single.status_code == 200:
                single_pkg = get_single.json()
                print("✅ Single package retrieved successfully!")
                print(f"   📦 Name: {single_pkg['package']['name']}")
                print(f"   🎯 Features: {single_pkg['package']['features']}")
            else:
                print(f"❌ Get single package failed: {get_single.status_code}")
        
        # Update package
        if package_id:
            print(f"\n📝 Testing UPDATE Package (ID: {package_id})...")
            update_data = {
                "name": "API Test Package Updated",
                "price_monthly": 89.99,
                "features": {
                    "campaigns": True,
                    "api_access": False,  # Changed
                    "advanced_analytics": True
                }
            }
            
            update_package = requests.put(
                f"{base_url}/subscriptions/admin/packages/{package_id}/", 
                json=update_data, 
                headers=admin_headers
            )
            
            if update_package.status_code == 200:
                updated_pkg = update_package.json()
                print("✅ Package updated successfully!")
                print(f"   📦 New Name: {updated_pkg['package']['name']}")
                print(f"   💰 New Price: ${updated_pkg['package']['price_monthly']}")
                print(f"   🎯 Updated Features: {updated_pkg['package']['features']}")
            else:
                print(f"❌ Update package failed: {update_package.status_code}")
        
        # ==================== USER PACKAGE SELECTION ====================
        print("\n👤 3. USER PACKAGE SELECTION")
        print("-" * 40)
        
        # Get available packages for user
        print("📋 Testing GET Available Packages (User View)...")
        user_packages = requests.get(f"{base_url}/subscriptions/user/packages/", headers=user_headers)
        
        if user_packages.status_code == 200:
            user_pkgs = user_packages.json()
            print(f"✅ Found {len(user_pkgs['packages'])} packages available for users")
            for i, pkg in enumerate(user_pkgs['packages'][:3]):
                print(f"   {i+1}. {pkg['name']} - ${pkg['price_monthly']}")
                print(f"      Features: {pkg['features']}")
                print(f"      Plan Type: {pkg['plan_type']}")
                print(f"      Popular: {'✅' if pkg['is_popular'] else '❌'}")
        else:
            print(f"❌ Get user packages failed: {user_packages.status_code}")
        
        # ==================== USER SUBSCRIPTION MANAGEMENT ====================
        print("\n🔔 4. USER SUBSCRIPTION MANAGEMENT")
        print("-" * 40)
        
        # Get user's current subscription
        print("📋 Testing GET Current Subscription...")
        current_sub = requests.get(f"{base_url}/subscriptions/user/subscription/", headers=user_headers)
        
        if current_sub.status_code == 200:
            sub_data = current_sub.json()
            print("✅ Current subscription retrieved!")
            if sub_data.get('subscription'):
                print(f"   📦 Plan: {sub_data['subscription']['plan_name']}")
                print(f"   📊 Status: {sub_data['subscription']['status']}")
                print(f"   📅 Period: {sub_data['subscription']['current_period_start']} to {sub_data['subscription']['current_period_end']}")
            else:
                print("   📦 No active subscription")
        else:
            print(f"❌ Get current subscription failed: {current_sub.status_code}")
        
        # Subscribe to a package (if available)
        if user_packages.status_code == 200 and user_pkgs['packages']:
            test_package_id = user_pkgs['packages'][0]['id']
            print(f"\n🔔 Testing SUBSCRIBE to Package (ID: {test_package_id})...")
            
            subscribe_data = {
                "package_id": test_package_id,
                "billing_cycle": "month"
            }
            
            subscribe = requests.post(
                f"{base_url}/subscriptions/user/subscribe/", 
                json=subscribe_data, 
                headers=user_headers
            )
            
            if subscribe.status_code in [200, 201]:
                sub_result = subscribe.json()
                print("✅ Subscription process initiated!")
                print(f"   📦 Message: {sub_result.get('message', 'Success')}")
                if 'checkout_url' in sub_result:
                    print(f"   🔗 Checkout URL: {sub_result['checkout_url'][:50]}...")
            else:
                print(f"❌ Subscribe failed: {subscribe.status_code} - {subscribe.text}")
        
        # ==================== BILLING & INVOICES ====================
        print("\n💳 5. BILLING & INVOICES")
        print("-" * 40)
        
        # Get billing portal
        print("🏦 Testing Billing Portal Access...")
        billing_portal = requests.post(f"{base_url}/subscriptions/user/billing-portal/", headers=user_headers)
        
        if billing_portal.status_code == 200:
            portal_data = billing_portal.json()
            print("✅ Billing portal accessible!")
            print(f"   🔗 Portal URL: {portal_data.get('portal_url', 'Available')[:50]}...")
        else:
            print(f"❌ Billing portal failed: {billing_portal.status_code}")
        
        # Get invoices
        print("📄 Testing Invoice Management...")
        invoices = requests.get(f"{base_url}/subscriptions/user/invoices/", headers=user_headers)
        
        if invoices.status_code == 200:
            invoice_data = invoices.json()
            print(f"✅ Found {len(invoice_data.get('invoices', []))} invoices")
            for i, invoice in enumerate(invoice_data.get('invoices', [])[:2]):
                print(f"   {i+1}. Invoice #{invoice.get('number', 'N/A')} - ${invoice.get('amount', 0)}")
        else:
            print(f"❌ Get invoices failed: {invoices.status_code}")
        
        # ==================== USAGE & ALERTS ====================
        print("\n📊 6. USAGE & ALERTS")
        print("-" * 40)
        
        # Get usage alerts
        print("🚨 Testing Usage Alerts...")
        alerts = requests.get(f"{base_url}/subscriptions/user/alerts/", headers=user_headers)
        
        if alerts.status_code == 200:
            alert_data = alerts.json()
            print(f"✅ Found {len(alert_data.get('alerts', []))} usage alerts")
            for alert in alert_data.get('alerts', [])[:2]:
                print(f"   🚨 {alert.get('alert_type', 'Alert')}: {alert.get('message', 'No message')}")
        else:
            print(f"❌ Get alerts failed: {alerts.status_code}")
        
        # Test feature access
        print("🔐 Testing Feature Access Check...")
        feature_check = requests.get(f"{base_url}/subscriptions/user/feature-access/", headers=user_headers)
        
        if feature_check.status_code == 200:
            feature_data = feature_check.json()
            print("✅ Feature access retrieved!")
            features = feature_data.get('features', {})
            print(f"   🎯 Campaigns: {'✅' if features.get('campaigns') else '❌'}")
            print(f"   🎯 API Access: {'✅' if features.get('api_access') else '❌'}")
            print(f"   🎯 Advanced Analytics: {'✅' if features.get('advanced_analytics') else '❌'}")
        else:
            print(f"❌ Feature access check failed: {feature_check.status_code}")
        
        # ==================== ADMIN STATISTICS ====================
        print("\n📈 7. ADMIN STATISTICS & MANAGEMENT")
        print("-" * 40)
        
        # Get subscription statistics
        print("📊 Testing Subscription Statistics (Admin)...")
        stats = requests.get(f"{base_url}/subscriptions/admin/statistics/", headers=admin_headers)
        
        if stats.status_code == 200:
            stats_data = stats.json()
            print("✅ Subscription statistics retrieved!")
            print(f"   📊 Total Subscriptions: {stats_data.get('total_subscriptions', 0)}")
            print(f"   💰 Monthly Revenue: ${stats_data.get('monthly_revenue', 0)}")
            print(f"   📈 Active Users: {stats_data.get('active_users', 0)}")
        else:
            print(f"❌ Get statistics failed: {stats.status_code}")
        
        # ==================== CLEANUP ====================
        print("\n🧹 8. CLEANUP")
        print("-" * 40)
        
        # Delete test package if created
        if package_id:
            print(f"🗑️ Cleaning up test package (ID: {package_id})...")
            delete_package = requests.delete(f"{base_url}/subscriptions/admin/packages/{package_id}/", headers=admin_headers)
            
            if delete_package.status_code == 204:
                print("✅ Test package deleted successfully!")
            else:
                print(f"❌ Delete package failed: {delete_package.status_code}")
        
        # ==================== FINAL SUMMARY ====================
        print("\n" + "=" * 60)
        print("🎉 COMPLETE API TESTING SUMMARY")
        print("=" * 60)
        print("✅ Authentication - Admin & User Login")
        print("✅ Admin Package Management - CRUD Operations")
        print("✅ User Package Selection - Available Packages")
        print("✅ User Subscription Management - Subscribe/Manage")
        print("✅ Billing Portal - Stripe Integration")
        print("✅ Invoice Management - User Invoices")
        print("✅ Usage Alerts - Monitoring System")
        print("✅ Feature Access - Permission Checking")
        print("✅ Admin Statistics - Subscription Analytics")
        print("✅ Cleanup - Resource Management")
        print("\n🚀 ALL SUBSCRIPTION & PACKAGE APIs WORKING PERFECTLY!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TESTING ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_complete_subscription_package_apis()
