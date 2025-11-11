"""
Update all call statuses to 'completed'
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import TwilioCall

def update_all_call_statuses():
    print("=" * 70)
    print("📞 UPDATING ALL CALL STATUSES TO 'COMPLETED'")
    print("=" * 70)
    print()
    
    # Get all calls
    all_calls = TwilioCall.objects.all()
    total_calls = all_calls.count()
    
    print(f"Found {total_calls} total calls")
    print()
    
    # Count by current status
    status_counts = {}
    for call in all_calls:
        status = call.status or 'unknown'
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Current status distribution:")
    for status, count in status_counts.items():
        print(f"   {status}: {count} calls")
    print()
    
    # Update all to completed
    updated_count = all_calls.update(status='completed')
    
    print("=" * 70)
    print(f"✅ SUCCESS! Updated {updated_count} calls to 'completed' status")
    print()
    
    # Verify
    completed_calls = TwilioCall.objects.filter(status='completed').count()
    print(f"Verification: {completed_calls} calls now have 'completed' status")
    print()

if __name__ == "__main__":
    update_all_call_statuses()
