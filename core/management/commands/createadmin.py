"""
🔐 Create Admin User Command for Railway Production
Usage: python manage.py createadmin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create admin user for production deployment'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username', default='admin')
        parser.add_argument('--email', type=str, help='Admin email', default='SalesAice.ai@gmail.com')
        parser.add_argument('--password', type=str, help='Admin password', default='Aiceinthehole')

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = options['username']
        email = options['email']
        password = options['password']
        
        # If no password provided, use environment variable or default
        if not password or password == 'Aiceinthehole':
            password = os.getenv('ADMIN_PASSWORD', 'Aiceinthehole')
        
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists!')
            )
            # Get existing user and show info
            user = User.objects.get(username=username)
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'🌐 Login at: https://salesaiceailive-production.up.railway.app/admin/')
            return
            
        # Create admin user
        try:
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!')
            )
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write(f'🌐 Login at: https://salesaiceailive-production.up.railway.app/admin/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {str(e)}')
            )