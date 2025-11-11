"""
Quick Test Script - Human-Like Conversation
Run after configuring HumeAI Dashboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import ConversationLog, TwilioCall
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*80)
print("🧪 HUMAN-LIKE CONVERSATION TEST")
print("="*80)

# Get most recent call
recent_call = TwilioCall.objects.filter(provider='vonage').order_by('-created_at').first()

if not recent_call:
    print("\n❌ No Vonage calls found!")
    print("\n💡 Make a test call first:")
    print("   $headers = @{'Content-Type'='application/json'}")
    print("   $body = @{phone_no='+923030061756'; agent_id='1'} | ConvertTo-Json")
    print("   Invoke-RestMethod -Uri 'https://your-ngrok.ngrok-free.dev/api/hume-twilio/initiate-call/' -Method POST -Headers $headers -Body $body")
    exit()

print(f"\n📞 Latest Call:")
print(f"   UUID: {recent_call.call_sid}")
print(f"   Status: {recent_call.status}")
print(f"   Duration: {recent_call.duration}s")
print(f"   Agent: {recent_call.agent.name if recent_call.agent else 'None'}")
print(f"   Started: {recent_call.started_at}")

# Get conversation logs
convs = ConversationLog.objects.filter(call=recent_call).order_by('timestamp')
conv_count = convs.count()

print(f"\n💬 Conversation Logs: {conv_count} messages")

if conv_count == 0:
    print("\n❌ NO CONVERSATIONS SAVED!")
    print("\n🔍 Troubleshooting:")
    print("   1. Check server logs for HumeAI connection")
    print("   2. Verify HumeAI Dashboard configuration")
    print("   3. Check if transcripts are empty in logs")
    print("   4. Restart server: Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force")
else:
    print("\n✅ CONVERSATIONS FOUND!")
    print("\n" + "-"*80)
    
    for i, conv in enumerate(convs, 1):
        role_emoji = "💬" if conv.role == 'user' else "🤖"
        role_label = "CUSTOMER" if conv.role == 'user' else "AGENT"
        
        print(f"\n{i}. {role_emoji} [{role_label}]")
        print(f"   Time: {conv.timestamp}")
        
        if len(conv.message) > 150:
            print(f"   Message: {conv.message[:150]}...")
        else:
            print(f"   Message: {conv.message}")
    
    print("\n" + "-"*80)
    
    # Analyze conversation quality
    user_msgs = convs.filter(role='user').count()
    agent_msgs = convs.filter(role='assistant').count()
    
    print(f"\n📊 Conversation Analysis:")
    print(f"   Customer messages: {user_msgs}")
    print(f"   Agent responses: {agent_msgs}")
    print(f"   Total exchanges: {conv_count}")
    
    # Check for human-like qualities
    print(f"\n🎯 Human-Like Score:")
    
    score = 0
    max_score = 5
    
    # 1. Has greeting?
    if agent_msgs > 0:
        first_agent = convs.filter(role='assistant').first()
        if first_agent and any(word in first_agent.message.lower() for word in ['hello', 'hi', 'hey', 'greet']):
            print("   ✅ Natural greeting")
            score += 1
        else:
            print("   ❌ No greeting detected")
    
    # 2. Customer spoke first?
    if conv_count > 0:
        first_msg = convs.first()
        if first_msg.role == 'user':
            print("   ✅ Customer spoke first")
            score += 1
        else:
            print("   ⚠️  Agent spoke first (check if greeting)")
            score += 0.5
    
    # 3. Back-and-forth conversation?
    if user_msgs > 0 and agent_msgs > 0:
        if abs(user_msgs - agent_msgs) <= 2:
            print("   ✅ Balanced conversation")
            score += 1
        else:
            print("   ⚠️  Unbalanced (one side dominated)")
            score += 0.5
    
    # 4. Multiple exchanges?
    if conv_count >= 4:
        print("   ✅ Multiple exchanges (natural flow)")
        score += 1
    else:
        print("   ⚠️  Few exchanges (short conversation)")
        score += 0.5
    
    # 5. Non-empty messages?
    empty_count = sum(1 for c in convs if not c.message.strip())
    if empty_count == 0:
        print("   ✅ All messages have content")
        score += 1
    else:
        print(f"   ❌ {empty_count} empty messages")
    
    percentage = (score / max_score) * 100
    print(f"\n   Score: {score}/{max_score} ({percentage:.0f}%)")
    
    if percentage >= 80:
        print("   🎉 EXCELLENT - Very human-like!")
    elif percentage >= 60:
        print("   👍 GOOD - Mostly human-like")
    elif percentage >= 40:
        print("   ⚠️  FAIR - Needs improvement")
    else:
        print("   ❌ POOR - Not human-like yet")

print("\n" + "="*80)
print("📖 For complete setup guide, see:")
print("   HUMAN_LIKE_CONVERSATION_COMPLETE_GUIDE.md")
print("="*80 + "\n")
