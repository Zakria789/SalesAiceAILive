"""
Verify Transcript Database - Real-Time Check
============================================

This script checks:
1. Total ConversationLog entries
2. Recent calls with transcripts
3. Sample conversation data

Run: python verify_transcript_now.py
"""

import os
import django
import sys

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import TwilioCall, ConversationLog
from django.utils import timezone
from datetime import timedelta

def check_transcript_data():
    print("\n" + "="*70)
    print("🔍 TRANSCRIPT DATABASE VERIFICATION")
    print("="*70 + "\n")
    
    # 1. Total conversation logs
    total_logs = ConversationLog.objects.count()
    print(f"📊 Total ConversationLog Entries: {total_logs}")
    
    if total_logs == 0:
        print("\n❌ DATABASE EMPTY!")
        print("   → No transcript entries found in ConversationLog table")
        print("   → Make a NEW test call and speak during the call")
        print("   → Check backend logs for: '💾 [DB] Saved message'")
        return
    
    print(f"✅ Database has {total_logs} transcript entries!\n")
    
    # 2. Recent calls with transcripts (last 24 hours)
    recent_time = timezone.now() - timedelta(hours=24)
    recent_calls = TwilioCall.objects.filter(
        provider='vonage',
        created_at__gte=recent_time
    ).order_by('-created_at')[:10]
    
    print(f"📞 Recent Vonage Calls (Last 24h): {recent_calls.count()}\n")
    
    if recent_calls.count() == 0:
        print("⚠️  No recent Vonage calls found!")
        print("   → Make a new test call from frontend")
        return
    
    # 3. Check each call's transcript
    for idx, call in enumerate(recent_calls, 1):
        logs = ConversationLog.objects.filter(call=call).order_by('timestamp')
        log_count = logs.count()
        
        status_icon = "✅" if log_count > 0 else "❌"
        print(f"{status_icon} {idx}. Call: {call.call_sid[:15]}...")
        print(f"   Status: {call.status} | Duration: {call.duration}s")
        print(f"   Transcript Messages: {log_count}")
        
        if log_count > 0:
            print(f"   📝 Sample Conversation:")
            for log in logs[:3]:  # Show first 3 messages
                speaker = "👤 Customer" if log.role == 'user' else "🤖 Agent"
                message_preview = log.message[:60] + "..." if len(log.message) > 60 else log.message
                print(f"      {speaker}: {message_preview}")
        else:
            print(f"   ⚠️  No transcript saved for this call")
        print()
    
    # 4. Check latest transcript entry
    latest_log = ConversationLog.objects.order_by('-timestamp').first()
    if latest_log:
        print("\n" + "─"*70)
        print("🕐 LATEST TRANSCRIPT ENTRY:")
        print("─"*70)
        print(f"Call: {latest_log.call.call_sid}")
        print(f"Role: {latest_log.role}")
        print(f"Message: {latest_log.message}")
        print(f"Time: {latest_log.timestamp}")
        print(f"Sentiment: {latest_log.sentiment or 'N/A'}")
        
    # 5. Active calls check
    active_calls = TwilioCall.objects.filter(
        status='in_progress',
        provider='vonage'
    )
    
    print("\n" + "─"*70)
    print(f"🔴 CURRENTLY ACTIVE CALLS: {active_calls.count()}")
    print("─"*70)
    
    if active_calls.count() > 0:
        for call in active_calls:
            logs = ConversationLog.objects.filter(call=call).count()
            print(f"  📞 {call.call_sid[:15]}... - Transcript: {logs} messages")
    else:
        print("  No active calls right now")
    
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETE")
    print("="*70 + "\n")
    
    # 6. Recommendations
    if total_logs == 0:
        print("🎯 NEXT STEPS:")
        print("   1. Make a NEW test call from frontend")
        print("   2. Speak during the call: 'Hello, testing'")
        print("   3. Wait for agent response")
        print("   4. Check backend logs: docker-compose logs -f --tail=50")
        print("   5. Look for: '💾 [DB] Saved user message'")
        print()
    elif any(ConversationLog.objects.filter(call=call).count() == 0 for call in recent_calls):
        print("🎯 ISSUE FOUND:")
        print("   Some calls have NO transcript saved!")
        print("   → Check HumeAI WebSocket events")
        print("   → Check save_conversation_message() function")
        print()

if __name__ == '__main__':
    try:
        check_transcript_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
