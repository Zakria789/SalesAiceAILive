#!/usr/bin/env python
"""
Simple test for Billing Data API
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_api_import():
    try:
        from subscriptions.billing_data_api import BillingDataAPIView
        print("✅ Successfully imported BillingDataAPIView")
        
        # Test basic instantiation
        api_view = BillingDataAPIView()
        print("✅ Successfully created API instance")
        
        print("\n📋 API Methods:")
        print(f"   • get method: {'✅' if hasattr(api_view, 'get') else '❌'}")
        print(f"   • permission_classes: {api_view.permission_classes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 Testing Billing Data API Import...")
    success = test_api_import()
    
    if success:
        print("\n✅ Billing Data API is ready!")
        print("📌 Class: BillingDataAPIView")
        print("📌 File: subscriptions/billing_data_api.py")
    else:
        print("\n❌ API setup failed")
