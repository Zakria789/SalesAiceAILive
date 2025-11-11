#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.admin_views import UserDetailAPIView

User = get_user_model()

def test_name_variations():
    print("=== TESTING NAME VARIATIONS IN API ===\n")
    
    # Test with different users to show name handling
    test_users = [
        {'id': 4, 'expected_name': 'zakria11@gmail.com'},  # user_name only
        {'id': 5, 'expected_name': 'Test User'},           # first_name + last_name
        {'id': 8, 'expected_name': 'Sales Admin'},         # first_name + last_name
    ]
    
    # Mock admin request
    class MockRequest:
        def __init__(self, admin_user):
            self.user = admin_user
    
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_user(
            user_name='temp_admin', 
            email='temp@admin.com',
            password='test123',
            is_staff=True
        )
    
    api_view = UserDetailAPIView()
    mock_request = MockRequest(admin_user)
    
    for test_case in test_users:
        user_id = test_case['id']
        expected_name = test_case['expected_name']
        
        try:
            user = User.objects.get(id=user_id)
            print(f"👤 User ID {user_id}: {user.user_name}")
            print(f"   first_name: '{user.first_name}'")
            print(f"   last_name: '{user.last_name}'")
            print(f"   Expected API name: '{expected_name}'")
            
            response = api_view.get(mock_request, str(user_id))
            
            if response.status_code == 200:
                actual_name = response.data['user']['name']
                print(f"   ✅ API returned name: '{actual_name}'")
                
                if actual_name == expected_name:
                    print(f"   🎯 MATCH! Name correctly returned")
                else:
                    print(f"   ❌ MISMATCH! Expected '{expected_name}' but got '{actual_name}'")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
            print()
            
        except User.DoesNotExist:
            print(f"   ❌ User {user_id} not found")
            print()
    
    print(f"📋 NAME LOGIC SUMMARY:")
    print(f"   API returns: user.get_full_name() OR user.user_name")
    print(f"   - If first_name + last_name exist → returns 'First Last'")
    print(f"   - If no first/last name → returns user_name")
    print(f"   - This provides the most meaningful name for each user")

if __name__ == "__main__":
    test_name_variations()