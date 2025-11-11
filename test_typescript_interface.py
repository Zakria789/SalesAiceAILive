#!/usr/bin/env python
"""
TypeScript AdminPackage Interface Compatibility Test
Verifies that the API response matches the exact TypeScript interface
"""

import os
import sys
import django
import json

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from subscriptions.models import SubscriptionPlan
from subscriptions.admin_package_management import AdminPackageManagementAPIView
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from accounts.models import User

User = get_user_model()


def test_admin_package_interface():
    """Test that AdminPackageManagementAPIView returns data matching TypeScript AdminPackage interface"""
    
    print("🔍 Testing AdminPackage Interface Compatibility")
    print("=" * 60)
    
    # Create a test admin user
    admin_user = User.objects.filter(role='admin').first()
    if not admin_user:
        admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
    
    # Create a test package if none exists
    if not SubscriptionPlan.objects.exists():
        test_package = SubscriptionPlan.objects.create(
            name='Test Pro Plan',
            plan_type='pro',
            price=99.99,
            call_minutes_limit=3000,
            minutes_inbound_limit=1500,
            minutes_outbound_limit=1500,
            agents_allowed=5,
            analytics_access=True,
            advanced_analytics=False,
            api_access=False,
            call_recording=True,
            is_active=True
        )
        print(f"✅ Created test package: {test_package.name}")
    
    # Create API request
    factory = APIRequestFactory()
    request = factory.get('/api/subscriptions/admin/packages/')
    request.user = admin_user
    
    # Get API response
    view = AdminPackageManagementAPIView()
    response = view.get(request)
    
    print(f"📄 API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.data
        packages = data.get('packages', [])
        
        if packages:
            package = packages[0]  # Test first package
            
            print(f"📦 Testing Package: {package.get('name')}")
            print("\n🔍 TypeScript Interface Compatibility Check:")
            print("-" * 50)
            
            # Expected TypeScript interface fields
            expected_fields = {
                'id': ['number', 'string'],  # number | string
                'name': ['string'],
                'price_monthly': ['number', 'string'],  # number | string
                'minutes_inbound_limit': ['number'],
                'minutes_outbound_limit': ['number'],
                'minutes_total_limit': ['number'],
                'agents_allowed': ['number'],
                'analytics_access': ['boolean'],
                'features': ['object'],  # Record<string, any>
                'is_active': ['boolean'],
                'created_at': ['string'],
                'subscribers': ['number', 'undefined']  # Optional field
            }
            
            all_tests_passed = True
            
            for field, expected_types in expected_fields.items():
                if field in package:
                    value = package[field]
                    actual_type = type(value).__name__
                    
                    # Map Python types to TypeScript types
                    type_mapping = {
                        'str': 'string',
                        'int': 'number',
                        'float': 'number',
                        'bool': 'boolean',
                        'dict': 'object',
                        'NoneType': 'undefined'
                    }
                    
                    ts_type = type_mapping.get(actual_type, actual_type)
                    
                    if ts_type in expected_types:
                        print(f"✅ {field}: {ts_type} (value: {value})")
                    else:
                        print(f"❌ {field}: Expected {expected_types}, got {ts_type}")
                        all_tests_passed = False
                elif field == 'subscribers':  # Optional field
                    print(f"✅ {field}: optional (not present)")
                else:
                    print(f"❌ {field}: Missing required field")
                    all_tests_passed = False
            
            print("\n📋 Sample API Response:")
            print("-" * 30)
            print(json.dumps(package, indent=2))
            
            print("\n💻 TypeScript Interface Validation:")
            print("-" * 40)
            
            if all_tests_passed:
                print("🎉 ALL TESTS PASSED!")
                print("✅ API response perfectly matches TypeScript AdminPackage interface")
                
                print("\n📝 TypeScript Usage Example:")
                print("""
const fetchAdminPackages = async (): Promise<AdminPackage[]> => {
  const response = await fetch('/api/subscriptions/admin/packages/', {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
  
  const data = await response.json();
  return data.packages; // Fully type-safe!
};

// Usage
const packages: AdminPackage[] = await fetchAdminPackages();
packages.forEach(pkg => {
  console.log(`${pkg.name}: $${pkg.price_monthly}/month`);
  console.log(`Inbound: ${pkg.minutes_inbound_limit} minutes`);
  console.log(`Outbound: ${pkg.minutes_outbound_limit} minutes`);
  console.log(`Total: ${pkg.minutes_total_limit} minutes`);
  console.log(`Agents: ${pkg.agents_allowed}`);
});
                """)
                
            else:
                print("❌ Some tests failed. API response needs adjustment.")
                
            return all_tests_passed
            
        else:
            print("❌ No packages found in response")
            return False
    else:
        print(f"❌ API request failed with status {response.status_code}")
        return False


def show_typescript_interface():
    """Show the complete TypeScript interface"""
    print("\n📋 Complete TypeScript AdminPackage Interface:")
    print("=" * 50)
    
    interface = '''
type AdminPackage = {
  id: number | string;
  name: string;
  price_monthly: number | string;
  minutes_inbound_limit: number;
  minutes_outbound_limit: number;
  minutes_total_limit: number;
  agents_allowed: number;
  analytics_access: boolean;
  features: Record<string, any>;
  is_active: boolean;
  created_at: string;
  subscribers?: number;
};

// Example API Response Type
type AdminPackagesResponse = {
  success: boolean;
  message: string;
  packages: AdminPackage[];
};
    '''
    
    print(interface)


def main():
    """Main test runner"""
    success = test_admin_package_interface()
    show_typescript_interface()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 TYPESCRIPT INTERFACE COMPATIBILITY: PERFECT MATCH! ✅")
        print("Your API response exactly matches the TypeScript AdminPackage interface!")
    else:
        print("⚠️  TYPESCRIPT INTERFACE COMPATIBILITY: NEEDS ADJUSTMENT")
        print("Please review the failed checks above.")
    print("=" * 60)
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
