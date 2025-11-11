"""
Test New Unified Active Calls Endpoint
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Your credentials
EMAIL = "umair11@gmail.com"

print("="*60)
print("NEW UNIFIED ACTIVE CALLS ENDPOINT")
print("="*60)

try:
    user = User.objects.get(email=EMAIL)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f"\n✅ Token generated for: {user.email}")
    print(f"\n{'='*60}")
    print("NEW ENDPOINT - All Active Calls (Inbound + Outbound)")
    print(f"{'='*60}")
    
    print("\n🆕 UNIFIED ENDPOINT (Recommended):")
    print(f'curl -X GET "http://localhost:8002/api/hume-twilio/dashboard/active-calls/" ^')
    print(f'  -H "Authorization: Bearer {access_token}"')
    
    print("\n📋 Response will include:")
    print("  • type: 'inbound' or 'outbound' for each call")
    print("  • summary.total_inbound: Count of inbound calls")
    print("  • summary.total_outbound: Count of outbound calls")
    print("  • All call details with live transcripts")
    
    print(f"\n{'='*60}")
    print("EXISTING ENDPOINTS (Also updated with 'type' field)")
    print(f"{'='*60}")
    
    print("\n📞 Inbound Only:")
    print(f'curl -X GET "http://localhost:8002/api/hume-twilio/dashboard/inbound/active/" ^')
    print(f'  -H "Authorization: Bearer {access_token}"')
    
    print("\n\n💡 RECOMMENDATION:")
    print("   Use /dashboard/active-calls/ for your frontend")
    print("   It shows BOTH inbound and outbound with 'type' field!")
    
    print(f"\n{'='*60}")
    print("⚠️  IMPORTANT: RESTART SERVER TO APPLY CHANGES")
    print(f"{'='*60}")
    print("\nIn your Daphne terminal, press Ctrl+C and restart:")
    print("  .\\venv\\Scripts\\Activate.ps1; daphne -b 0.0.0.0 -p 8002 core.asgi:application")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
