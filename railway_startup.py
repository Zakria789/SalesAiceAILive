#!/usr/bin/env python
"""
Railway startup script with better error handling
"""
import os
import sys
import time
import subprocess

def wait_for_database(max_attempts=30, delay=2):
    """Wait for database to be available"""
    print("🔍 Checking database connectivity...")
    
    for attempt in range(max_attempts):
        try:
            # Test database connection
            result = subprocess.run([
                'python', 'manage.py', 'check', '--database', 'default'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Database is ready!")
                return True
                
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Database not ready yet...")
            
        except subprocess.TimeoutExpired:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Database check timed out...")
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts}: {str(e)}")
            
        time.sleep(delay)
    
    print("❌ Database not available after maximum attempts")
    return False

def run_migrations():
    """Run Django migrations"""
    print("🔄 Running migrations...")
    try:
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], check=True, text=True)
        print("✅ Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False

def start_server():
    """Start the Django server"""
    print("🚀 Starting Django server...")
    port = os.environ.get('PORT', '8000')
    
    try:
        subprocess.run([
            'daphne', '-b', '0.0.0.0', '-p', port, 'core.asgi:application'
        ], check=True)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

def main():
    print("🚂 Railway Django Startup Script")
    print("=" * 40)
    
    # Check environment
    db_url = os.environ.get('DATABASE_URL')
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    
    print(f"Railway Environment: {railway_env}")
    print(f"Database URL exists: {bool(db_url)}")
    
    if not db_url:
        print("❌ DATABASE_URL not found! Check Railway environment variables.")
        sys.exit(1)
    
    # Wait for database
    if not wait_for_database():
        print("❌ Cannot connect to database. Exiting...")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migrations failed. Exiting...")
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()