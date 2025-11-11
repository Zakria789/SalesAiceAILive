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

User = get_user_model()

def test_user_name_fields():
    print("=== TESTING USER NAME FIELDS ===\n")
    
    users = User.objects.all()
    
    for user in users:
        print(f"👤 User ID: {user.id}")
        print(f"   user_name: '{user.user_name}'")
        print(f"   first_name: '{user.first_name}'")  
        print(f"   last_name: '{user.last_name}'")
        print(f"   get_full_name(): '{user.get_full_name()}'")
        print(f"   email: '{user.email}'")
        
        # Show what the API will return
        api_name = user.get_full_name() or user.user_name
        print(f"   🎯 API will return name: '{api_name}'")
        print()

if __name__ == "__main__":
    test_user_name_fields()