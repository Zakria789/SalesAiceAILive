"""
Test Live Updates API
=====================

Quick test to see what the live-updates API returns

Run: python test_live_updates_api.py
"""

import os
import django
import sys

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import TwilioCall, ConversationLog
from django.db.models import Q, Case, When

def test_live_updates():
    print("\n" + "="*70)
    print("🔍 TESTING LIVE UPDATES API LOGIC")
    print("="*70 + "\n")
    
    # Simulate the API query
    live_calls = TwilioCall.objects.filter(
        Q(status='in_progress') | Q(status='completed'),
        provider='vonage'
    ).select_related('agent').order_by(
        Case(
            When(status='in_progress', then=0),
            default=1
        ),
        '-started_at'
    )[:10]
    
    print(f"📊 Found {live_calls.count()} calls\n")
    
    if live_calls.count() == 0:
        print("❌ NO CALLS FOUND!")
        print("\n🔍 Debug Info:")
        
        # Check total Vonage calls
        total_vonage = TwilioCall.objects.filter(provider='vonage').count()
        print(f"   Total Vonage calls: {total_vonage}")
        
        # Check by status
        in_progress = TwilioCall.objects.filter(provider='vonage', status='in_progress').count()
        completed = TwilioCall.objects.filter(provider='vonage', status='completed').count()
        print(f"   In Progress: {in_progress}")
        print(f"   Completed: {completed}")
        
        # Show recent completed calls
        recent = TwilioCall.objects.filter(provider='vonage', status='completed').order_by('-created_at')[:3]
        print(f"\n   📞 Last 3 Completed Calls:")
        for call in recent:
            transcript_count = ConversationLog.objects.filter(call=call).count()
            print(f"      - {call.call_sid[:15]}... | Status: {call.status} | Transcript: {transcript_count} msgs")
        
        return
    
    for idx, call in enumerate(live_calls, 1):
        transcript = ConversationLog.objects.filter(call=call).order_by('-timestamp')[:10]
        transcript_count = transcript.count()
        
        status_icon = "🔴" if call.status == 'in_progress' else "✅"
        print(f"{status_icon} {idx}. Call: {call.call_sid[:20]}...")
        print(f"   Status: {call.status}")
        print(f"   Customer: {call.customer_name or call.to_number}")
        print(f"   Agent: {call.agent.name if call.agent else 'No Agent'}")
        print(f"   Transcript: {transcript_count} messages")
        
        if transcript_count > 0:
            print(f"   📝 Latest messages:")
            for log in list(reversed(transcript))[:3]:
                speaker = "👤 Customer" if log.role == 'user' else "🤖 Agent"
                msg_preview = log.message[:50] + "..." if len(log.message) > 50 else log.message
                print(f"      {speaker}: {msg_preview}")
        print()
    
    print("="*70)
    print("✅ API WOULD RETURN:", live_calls.count(), "calls")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_live_updates()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
