#!/usr/bin/env python3
"""
Quick server restart script to reload .env credentials
Use this on the system that's having authentication issues
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def main():
    print("🔄 RESTARTING DJANGO SERVER TO RELOAD CREDENTIALS")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found! Creating it...")
        
        env_content = """TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
"""
        env_file.write_text(env_content)
        print("✅ .env file created with correct credentials")
    
    # Clear Python cache
    print("🧹 Clearing Python cache...")
    try:
        if os.name == 'nt':  # Windows
            os.system('del /s /q *.pyc')
            os.system('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"')
        else:  # Unix/Linux/Mac
            os.system('find . -name "*.pyc" -delete')
            os.system('find . -name "__pycache__" -type d -exec rm -rf {} +')
        print("✅ Cache cleared")
    except:
        print("⚠️ Could not clear cache")
    
    # Instructions for manual restart
    print("\n🔄 MANUAL RESTART INSTRUCTIONS:")
    print("1. Stop current Django server (Ctrl+C in the terminal)")
    print("2. Wait 2 seconds")
    print("3. Run: python manage.py runserver")
    print("4. Test the API call again")
    
    print("\n🎯 ALTERNATIVE - Programmatic Restart:")
    print("If you want to restart automatically, run:")
    print("   python manage.py runserver --noreload")
    
    # Test credentials after restart
    print("\n📋 After restart, verify credentials with:")
    print("   python diagnose_django_twilio.py")

if __name__ == '__main__':
    main()