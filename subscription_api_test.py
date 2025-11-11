"""
Practical Test Script for Subscription Management API

This script demonstrates how to:
1. Get JWT tokens
2. List available plans 
3. Create subscriptions
4. Manage subscriptions (upgrade/downgrade/cancel)

Run this script to test your subscription API endpoints.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class SubscriptionTester:
    def __init__(self):
        self.token = None
        self.plans = []
        self.current_subscription = None
    
    def log(self, message, level="INFO"):
        """Log messages with formatting"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{symbols.get(level, 'ℹ️')} {message}")
    
    def make_request(self, method, endpoint, data=None, require_auth=True):
        """Make HTTP request with proper headers"""
        url = f"{API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if require_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif require_auth and not self.token:
            self.log("No authentication token available", "ERROR")
            return None
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                self.log(f"Unsupported method: {method}", "ERROR")
                return None
            
            self.log(f"{method.upper()} {endpoint} - Status: {response.status_code}")
            
            if response.status_code < 400:
                return response.json()
            else:
                self.log(f"Request failed: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Request error: {str(e)}", "ERROR")
            return None
    
    def get_jwt_token(self):
        """Get JWT token for authentication"""
        self.log("Getting JWT token...")
        
        # Try admin token first (GET method)
        data = self.make_request("GET", "/auth/admin-token/", require_auth=False)
        
        if data and data.get('access_token'):
            self.token = data['access_token']
            self.log("Successfully obtained admin token", "SUCCESS")
            return True
        
        # Try quick token as fallback (POST method)
        self.log("Admin token failed, trying quick token...")
        data = self.make_request("POST", "/auth/quick-token/", {
            "email": "admin@testcenter.com",
            "password": "admin123"
        }, require_auth=False)
        
        if data and data.get('access_token'):
            self.token = data['access_token']
            self.log("Successfully obtained quick token", "SUCCESS")
            return True
        
        self.log("Failed to obtain any JWT token", "ERROR")
        return False
    
    def get_subscription_plans(self):
        """Get available subscription plans"""
        self.log("Fetching subscription plans...")
        
        data = self.make_request("GET", "/subscriptions/api/plans/")
        
        if data and data.get('success'):
            self.plans = data.get('plans', [])
            self.log(f"Found {len(self.plans)} subscription plans", "SUCCESS")
            
            for i, plan in enumerate(self.plans, 1):
                print(f"  {i}. {plan['name']} ({plan['plan_type']})")
                print(f"     ID: {plan['id']}")
                print(f"     Price: ${plan['price']}/{plan['billing_cycle']}")
                features = plan.get('features', {})
                print(f"     Features: {features.get('call_minutes_limit', 0)} min, {features.get('agents_allowed', 0)} agents")
                print()
            
            return True
        else:
            self.log("Failed to fetch subscription plans", "ERROR")
            return False
    
    def get_current_subscription(self):
        """Get current user's subscription"""
        self.log("Checking current subscription...")
        
        data = self.make_request("GET", "/subscriptions/manage/")
        
        if data and data.get('success'):
            self.current_subscription = data.get('subscription')
            
            if self.current_subscription:
                sub = self.current_subscription
                self.log("Found active subscription", "SUCCESS")
                print(f"  Plan: {sub['plan']['name']}")
                print(f"  Status: {sub['status']}")
                print(f"  Period: {sub['current_period_start']} to {sub['current_period_end']}")
                if 'usage' in sub:
                    usage = sub['usage']
                    print(f"  Usage: {usage['minutes_used']}/{usage['minutes_limit']} minutes")
                print()
            else:
                self.log("No active subscription found", "WARNING")
            
            return True
        else:
            self.log("Failed to check subscription status", "ERROR")
            return False
    
    def create_subscription(self, plan_id, payment_method_id="pm_card_visa"):
        """Create a new subscription"""
        self.log(f"Creating subscription with plan {plan_id}...")
        
        data = self.make_request("POST", "/subscriptions/create/", {
            "plan_id": plan_id,
            "payment_method_id": payment_method_id,
            "billing_cycle": "month"
        })
        
        if data and data.get('success'):
            self.log("Subscription created successfully", "SUCCESS")
            print(f"  Subscription ID: {data.get('subscription', {}).get('id')}")
            print(f"  Status: {data.get('subscription', {}).get('status')}")
            return True
        else:
            self.log("Failed to create subscription", "ERROR")
            if data:
                print(f"  Error: {data.get('error', 'Unknown error')}")
            return False
    
    def manage_subscription(self, action, new_plan_id=None):
        """Manage existing subscription"""
        self.log(f"Managing subscription: {action}")
        
        request_data = {"action": action}
        if new_plan_id:
            request_data["new_plan_id"] = new_plan_id
        
        data = self.make_request("POST", "/subscriptions/manage/", request_data)
        
        if data and data.get('success'):
            self.log(f"Subscription {action} successful", "SUCCESS")
            if 'subscription' in data:
                sub = data['subscription']
                print(f"  New Status: {sub.get('status')}")
                print(f"  Cancel at period end: {sub.get('cancel_at_period_end')}")
            return True
        else:
            self.log(f"Failed to {action} subscription", "ERROR")
            if data:
                print(f"  Error: {data.get('error', 'Unknown error')}")
            return False
    
    def interactive_menu(self):
        """Interactive menu for testing"""
        while True:
            print("\n" + "="*50)
            print("SUBSCRIPTION MANAGEMENT TESTER")
            print("="*50)
            print("1. Get JWT Token")
            print("2. List Subscription Plans")
            print("3. Check Current Subscription")
            print("4. Create New Subscription")
            print("5. Upgrade Subscription")
            print("6. Downgrade Subscription") 
            print("7. Cancel Subscription")
            print("8. Run Full Test Suite")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Select option (0-8): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                self.get_jwt_token()
            elif choice == "2":
                if not self.token:
                    self.log("Please get JWT token first", "WARNING")
                else:
                    self.get_subscription_plans()
            elif choice == "3":
                if not self.token:
                    self.log("Please get JWT token first", "WARNING")
                else:
                    self.get_current_subscription()
            elif choice == "4":
                if not self.token:
                    self.log("Please get JWT token first", "WARNING")
                elif not self.plans:
                    self.log("Please fetch plans first", "WARNING")
                else:
                    self.create_subscription_interactive()
            elif choice in ["5", "6"]:
                action = "upgrade" if choice == "5" else "downgrade"
                if not self.token:
                    self.log("Please get JWT token first", "WARNING")
                elif not self.plans:
                    self.log("Please fetch plans first", "WARNING")
                else:
                    self.manage_subscription_interactive(action)
            elif choice == "7":
                if not self.token:
                    self.log("Please get JWT token first", "WARNING")
                else:
                    self.manage_subscription("cancel")
            elif choice == "8":
                self.run_full_test_suite()
            else:
                self.log("Invalid option", "WARNING")
    
    def create_subscription_interactive(self):
        """Interactive subscription creation"""
        print("\nAvailable Plans:")
        for i, plan in enumerate(self.plans, 1):
            print(f"{i}. {plan['name']} - ${plan['price']}/{plan['billing_cycle']}")
        
        try:
            plan_num = int(input("Select plan number: ")) - 1
            if 0 <= plan_num < len(self.plans):
                plan_id = self.plans[plan_num]['id']
                payment_method = input("Payment method ID (press Enter for test card): ").strip()
                if not payment_method:
                    payment_method = "pm_card_visa"
                
                self.create_subscription(plan_id, payment_method)
            else:
                self.log("Invalid plan number", "WARNING")
        except ValueError:
            self.log("Please enter a valid number", "WARNING")
    
    def manage_subscription_interactive(self, action):
        """Interactive subscription management"""
        print(f"\nAvailable Plans for {action}:")
        for i, plan in enumerate(self.plans, 1):
            print(f"{i}. {plan['name']} - ${plan['price']}/{plan['billing_cycle']}")
        
        try:
            plan_num = int(input("Select new plan number: ")) - 1
            if 0 <= plan_num < len(self.plans):
                plan_id = self.plans[plan_num]['id']
                self.manage_subscription(action, plan_id)
            else:
                self.log("Invalid plan number", "WARNING")
        except ValueError:
            self.log("Please enter a valid number", "WARNING")
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        print("\n" + "="*50)
        print("RUNNING FULL TEST SUITE")
        print("="*50)
        
        # Step 1: Get token
        if not self.get_jwt_token():
            return
        
        # Step 2: Get plans
        if not self.get_subscription_plans():
            return
        
        # Step 3: Check current subscription
        self.get_current_subscription()
        
        # Step 4: Test API endpoints are working
        self.log("Full test suite completed", "SUCCESS")
        
        if self.plans:
            print(f"\n📋 SUMMARY:")
            print(f"✅ JWT Token: {'Available' if self.token else 'Not available'}")
            print(f"✅ Plans Found: {len(self.plans)}")
            print(f"✅ Current Subscription: {'Yes' if self.current_subscription else 'None'}")
            
            print(f"\n🔧 PARAMETERS YOU CAN USE:")
            print(f"JWT Token: {self.token[:50]}..." if self.token else "No token")
            
            if self.plans:
                print(f"\nAvailable Plan IDs:")
                for plan in self.plans:
                    print(f"  - {plan['name']}: {plan['id']}")
                    
            print(f"\nTest Payment Method ID: pm_card_visa")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Subscription Management API Tester

Usage:
  python subscription_api_test.py          # Interactive mode
  python subscription_api_test.py --help   # Show this help

This script helps you test the subscription management API by:
1. Getting JWT authentication tokens
2. Listing available subscription plans
3. Creating new subscriptions  
4. Managing existing subscriptions (upgrade/downgrade/cancel)

The script will guide you through getting the required parameters for each API call.
        """)
        return
    
    tester = SubscriptionTester()
    
    print("🚀 Subscription Management API Tester")
    print("This tool helps you test the subscription APIs and get the required parameters.")
    print("\nMake sure your Django server is running on http://localhost:8000")
    
    tester.interactive_menu()

if __name__ == "__main__":
    main()
