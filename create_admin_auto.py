"""
🔐 Auto-create admin user on Railway startup
This script runs automatically when Django starts and creates admin if not exists
"""

import os
import django

def create_admin_if_not_exists():
    """Auto-create admin user on Railway startup"""
    try:
        # Import after Django setup
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get admin credentials from environment
        admin_email = os.getenv('ADMIN_EMAIL', 'SalesAice.ai@gmail.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Aiceinthehole')
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        
        # Check if admin already exists
        if User.objects.filter(username=admin_username).exists():
            print(f"✅ Admin user '{admin_username}' already exists")
            return
            
        if User.objects.filter(email=admin_email).exists():
            print(f"✅ User with email '{admin_email}' already exists")
            return
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        
        print(f"🎉 Admin user created successfully!")
        print(f"📧 Email: {admin_email}")
        print(f"👤 Username: {admin_username}")
        print(f"🌐 Login at: https://salesaiceailive-production.up.railway.app/admin/")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")

if __name__ == "__main__":
    # This can be called directly
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    create_admin_if_not_exists()