"""
Test Live Updates API Logic
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import TwilioCall, ConversationLog
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

print("\n" + "="*70)
print("🧪 TESTING LIVE UPDATES API LOGIC")
print("="*70 + "\n")

# Replicate API logic
# Get in_progress calls
active_calls = TwilioCall.objects.filter(
    status='in_progress',
    provider='vonage'
).select_related('agent')

print(f"1️⃣ Active calls (in_progress): {active_calls.count()}")
for call in active_calls:
    print(f"   - {call.call_sid[:15]}...")

# Get recently completed calls (last 2 minutes) with transcript
recent_completed = TwilioCall.objects.filter(
    status='completed',
    provider='vonage',
    ended_at__gte=timezone.now() - timedelta(minutes=2)
).select_related('agent').annotate(
    transcript_count=Count('conversationlog')
).filter(transcript_count__gt=0)

print(f"\n2️⃣ Recent completed (last 2 min with transcript): {recent_completed.count()}")
for call in recent_completed:
    transcript_count = ConversationLog.objects.filter(call=call).count()
    time_since_end = (timezone.now() - call.ended_at).total_seconds()
    print(f"   - {call.call_sid[:15]}...")
    print(f"     Ended: {int(time_since_end)}s ago")
    print(f"     Transcript: {transcript_count} messages")

# Combine
live_calls = list(active_calls) + list(recent_completed)
print(f"\n✅ TOTAL LIVE CALLS: {len(live_calls)}")

if len(live_calls) > 0:
    print("\n📋 Would return to frontend:")
    for call in live_calls:
        transcript = ConversationLog.objects.filter(call=call)
        print(f"   Call: {call.call_sid[:20]}...")
        print(f"   Status: {call.status}")
        print(f"   Transcript: {transcript.count()} messages")
        if transcript.exists():
            sample = transcript.order_by('timestamp')[:2]
            for msg in sample:
                print(f"     - {msg.role}: {msg.message[:40]}...")
        print()
else:
    print("\n❌ NO CALLS TO RETURN (empty response)")

print("="*70)
