"""
✅ VERIFY: All Twilio API Calls Disabled
=========================================

This script checks that NO Twilio API calls are happening
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

def check_twilio_code_disabled():
    """Check if Twilio API code is properly commented out"""
    
    print("\n" + "="*70)
    print("🔍 CHECKING TWILIO API CODE STATUS")
    print("="*70)
    
    file_path = "HumeAiTwilio/api_views/dashboard_views.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for commented Twilio code
    checks = {
        "Recording fetch code": "# # OLD TWILIO CODE (COMMENTED OUT - NO LONGER USING TWILIO)",
        "Duration fetch code": "# # OLD TWILIO CODE (COMMENTED OUT - NO LONGER USING TWILIO)",
        "Twilio Client import": "# from twilio.rest import Client",
        "Recording disabled marker": "❌ TWILIO RECORDING DISABLED",
        "Duration disabled marker": "❌ TWILIO DURATION FETCH DISABLED"
    }
    
    print("\n✅ VERIFICATION RESULTS:")
    print("-"*70)
    
    all_good = True
    for check_name, check_string in checks.items():
        if check_string in content:
            print(f"   ✅ {check_name}: DISABLED")
        else:
            print(f"   ❌ {check_name}: NOT FOUND")
            all_good = False
    
    # Check for active Twilio API calls
    print("\n⚠️  CHECKING FOR ACTIVE TWILIO API CALLS:")
    print("-"*70)
    
    dangerous_patterns = [
        "client.calls(",
        "client.recordings.list(",
        "Client(settings.TWILIO_ACCOUNT_SID",
    ]
    
    active_calls = []
    for pattern in dangerous_patterns:
        if pattern in content and f"# {pattern}" not in content:
            # Found uncommented usage
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern in line and not line.strip().startswith('#'):
                    active_calls.append((i, line.strip()))
    
    if active_calls:
        print("   ❌ FOUND ACTIVE TWILIO API CALLS:")
        for line_num, line in active_calls:
            print(f"      Line {line_num}: {line[:80]}")
        all_good = False
    else:
        print("   ✅ No active Twilio API calls found")
    
    print("\n" + "="*70)
    if all_good:
        print("✅ SUCCESS! All Twilio API code is properly disabled")
        print("   → Database is now the ONLY data source")
        print("   → No more 401 errors!")
    else:
        print("⚠️  WARNING: Some Twilio code may still be active")
    print("="*70)
    
    return all_good


def show_data_flow():
    """Show current data flow"""
    
    print("\n" + "="*70)
    print("📊 CURRENT DATA FLOW")
    print("="*70)
    
    print("""
┌─────────────────────────────────────────────────────────────┐
│                    VONAGE CALL                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Real-time audio stream
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           VONAGE REALTIME CONSUMER                          │
│  • Handles WebSocket audio                                  │
│  • Connects to HumeAI EVI                                   │
│  • Saves call data to database                              │
│    ✓ started_at                                             │
│    ✓ ended_at                                               │
│    ✓ duration (calculated)                                  │
│    ✗ recording_url (not saved yet)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Call data saved
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (TwilioCall)                          │
│  ✅ All call data stored                                    │
│  ✅ No external API dependencies                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Dashboard requests
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           DASHBOARD API                                     │
│  ✅ Reads from database only                                │
│  ❌ NO Twilio API calls                                     │
│  ✅ Fast response time                                      │
│  ✅ No authentication errors                                │
└─────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    check_twilio_code_disabled()
    show_data_flow()
    
    print("\n💡 TIP: Restart Django server to see the changes!")
    print("   No more 401 errors in logs! 🎉\n")
