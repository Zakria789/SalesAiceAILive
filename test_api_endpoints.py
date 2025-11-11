#!/usr/bin/env python
"""
API Testing Script for Stripe Billing System
Tests all billing endpoints with proper authentication
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class BillingAPITester:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
    
    def authenticate(self, email, password):
        """Get JWT token for authentication"""
        try:
            # Try to get user
            user = User.objects.get(email=email)
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            self.token = access_token
            self.headers['Authorization'] = f'Bearer {access_token}'
            
            print(f"✅ Authenticated as: {user.email}")
            print(f"🔑 Token: {access_token[:50]}...")
            return True
            
        except User.DoesNotExist:
            print(f"❌ User {email} not found")
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def test_public_endpoints(self):
        """Test public endpoints (no auth required)"""
        print("\n📝 Testing Public Endpoints...")
        
        # Test subscription plans
        try:
            url = f"{self.base_url}/api/subscriptions/api/plans/"
            response = requests.get(url)
            
            print(f"GET {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    plans = data.get('plans', [])
                    print(f"✅ Found {len(plans)} subscription plans")
                    for plan in plans:
                        print(f"   📦 {plan['name']} - ${plan['price']}/month")
                else:
                    print(f"❌ API returned error: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication"""
        if not self.token:
            print("❌ No authentication token. Login first.")
            return
        
        print("\n🔐 Testing Authenticated Endpoints...")
        
        # Test current subscription
        try:
            url = f"{self.base_url}/api/subscriptions/api/manage/"
            response = requests.get(url, headers=self.headers)
            
            print(f"GET {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    subscription = data.get('subscription')
                    if subscription:
                        print(f"✅ Active subscription found: {subscription}")
                    else:
                        print("✅ No active subscription (normal for new user)")
                else:
                    print(f"❌ API returned error: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test billing history
        try:
            url = f"{self.base_url}/api/subscriptions/api/billing-history/"
            response = requests.get(url, headers=self.headers)
            
            print(f"\nGET {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    history = data.get('billing_history', [])
                    print(f"✅ Found {len(history)} billing records")
                else:
                    print(f"❌ API returned error: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test payment methods
        try:
            url = f"{self.base_url}/api/subscriptions/api/payment-methods/"
            response = requests.get(url, headers=self.headers)
            
            print(f"\nGET {url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    methods = data.get('payment_methods', [])
                    print(f"✅ Found {len(methods)} payment methods")
                else:
                    print(f"❌ API returned error: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Stripe Billing API Testing")
        print("=" * 50)
        
        # Test public endpoints first
        self.test_public_endpoints()
        
        # Test with admin user
        if self.authenticate('admin@testcenter.com', 'admin123'):
            self.test_authenticated_endpoints()
        
        print("\n✅ API Testing Complete!")

def main():
    """Main test runner"""
    print("🚀 Starting API Tests...")
    
    # Check if server is running
    try:
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        print("✅ Django server is running")
    except requests.exceptions.RequestException:
        print("❌ Django server is not running!")
        print("💡 Start server with: python manage.py runserver")
        return
    
    # Run tests
    tester = BillingAPITester()
    tester.run_all_tests()
    
    # Show admin info
    print("\n" + "="*50)
    print("🔑 ADMIN ACCESS INFORMATION:")
    print("Email: admin@testcenter.com")
    print("Password: admin123")
    print("Admin Panel: http://127.0.0.1:8000/admin/")
    print("API Base URL: http://127.0.0.1:8000/api/subscriptions/")

if __name__ == '__main__':
    main()
