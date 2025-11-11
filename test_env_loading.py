"""
Quick check to see if environment variables are loading correctly
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("\n[+] .env file loaded")
    
    api_key = os.getenv('HUME_API_KEY')
    secret_key = os.getenv('HUME_SECRET_KEY')
    
    print(f"\nHUME_API_KEY: {api_key[:20] if api_key else 'NOT SET'}...")
    print(f"HUME_SECRET_KEY: {secret_key[:20] if secret_key else 'NOT SET'}...")
    
    if api_key and secret_key:
        print("\n[+] Both keys are properly loaded!")
    else:
        print("\n[!] Keys are missing!")
else:
    print("\n[!] .env file not found!")

# Now test with Django settings
print("\n" + "=" * 80)
print("CHECKING DJANGO SETTINGS")
print("=" * 80)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print(f"\nHUME_AI_API_KEY from settings: {settings.HUME_AI_API_KEY[:20] if hasattr(settings, 'HUME_AI_API_KEY') else 'NOT SET'}...")
print(f"HUME_AI_SECRET_KEY from settings: {settings.HUME_AI_SECRET_KEY[:20] if hasattr(settings, 'HUME_AI_SECRET_KEY') else 'NOT SET'}...")

if hasattr(settings, 'HUME_AI_API_KEY') and settings.HUME_AI_API_KEY:
    print("\n[+] Django settings loaded API keys correctly!")
else:
    print("\n[!] Django settings failed to load API keys!")
