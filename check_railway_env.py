#!/usr/bin/env python
"""
Quick fix for Railway environment variables
Run this to check and set missing variables
"""
import os

def check_railway_environment():
    print("🔍 Railway Environment Check")
    print("=" * 40)
    
    # Required environment variables
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string from Railway',
        'RAILWAY_ENVIRONMENT': 'Should be "production"',
        'SECRET_KEY': 'Django secret key',
        'PORT': 'Server port (Railway sets this automatically)'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            if var == 'SECRET_KEY':
                print(f"✅ {var}: {value[:10]}...")
            elif var == 'DATABASE_URL':
                print(f"✅ {var}: {value[:30]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET ({description})")
            missing_vars.append(var)
    
    print("\n" + "=" * 40)
    
    if missing_vars:
        print("❌ Missing environment variables!")
        print("\n📋 Add these to Railway dashboard → Variables:")
        print("\n```")
        if 'RAILWAY_ENVIRONMENT' in missing_vars:
            print("RAILWAY_ENVIRONMENT=production")
        if 'SECRET_KEY' in missing_vars:
            print("SECRET_KEY=your-super-secret-django-key-here")
        if 'DATABASE_URL' in missing_vars:
            print("DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway")
        print("```")
        print("\n🔧 Steps to fix:")
        print("1. Go to Railway dashboard")
        print("2. Select your project")
        print("3. Go to Variables tab")
        print("4. Add the missing variables")
        print("5. Redeploy your app")
    else:
        print("✅ All required environment variables are set!")
        
        # Test Django settings
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
            import django
            django.setup()
            
            from django.conf import settings
            db_engine = settings.DATABASES['default']['ENGINE']
            
            if 'postgresql' in db_engine:
                print("✅ Django is configured to use PostgreSQL")
            else:
                print(f"⚠️  Django is using: {db_engine}")
                print("   Should be PostgreSQL in production")
                
        except Exception as e:
            print(f"⚠️  Django setup error: {str(e)}")

if __name__ == '__main__':
    check_railway_environment()