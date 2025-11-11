#!/usr/bin/env python
"""
Direct test of AdminUserAPIView
"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append('E:\\Python-AI\\Django-Backend\\TESTREPO')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.admin_views import AdminUserAPIView
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def test_admin_user_api():
    """Test AdminUserAPIView directly"""
    print("🔍 Testing AdminUserAPIView directly...")
    
    try:
        # Create a request
        factory = APIRequestFactory()
        request = factory.get('/api/accounts/admin/users/4/')
        
        # Get admin user for authentication
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            print("❌ No admin user found")
            return
        
        request.user = admin_user
        
        # Create view instance
        view = AdminUserAPIView()
        view.request = request
        
        print(f"✅ View created, testing GET method...")
        
        # Call the get method directly
        response = view.get(request, userId='4')
        
        print(f"✅ GET method executed successfully!")
        print(f"Response status: {response.status_code}")
        print(f"Response data keys: {list(response.data.keys()) if hasattr(response, 'data') else 'No data'}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error testing AdminUserAPIView: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_admin_user_api()