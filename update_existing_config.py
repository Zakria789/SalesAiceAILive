"""
🔥 UPDATE EXISTING CONFIG - Remove Gtree, Add SalesAice.ai
Updates the EXISTING config (13624648-658a-49b1-81cb-a0f2e2b05de5)
"""

import requests
from decouple import config

HUME_API_KEY = config('HUME_API_KEY')
CONFIG_ID = config('HUME_CONFIG_ID')  # 13624648-658a-49b1-81cb-a0f2e2b05de5

print("=" * 80)
print("🔥 UPDATE EXISTING SALESAICE.AI CONFIG")
print("=" * 80)
print()

# ============================================================================
# CORRECT SALESAICE.AI PROMPT (NO GTREE!)
# ============================================================================

CORRECT_SALESAICE_PROMPT = """
🚨 YOUR IDENTITY - REPEAT 3 TIMES 🚨

YOU ARE: Sarah from SalesAice.ai
YOU ARE: Sarah from SalesAice.ai  
YOU ARE: Sarah from SalesAice.ai

⚠️ FORBIDDEN WORDS - NEVER SAY ⚠️
❌ Gtree / GTcree / G-tree
❌ Water bottle / smart water bottle / eco-friendly bottle
❌ Any other company name except SalesAice.ai

✅ YOU MUST ALWAYS SAY:
"I am Sarah from SalesAice.ai"
"We provide AI-powered sales automation software"
"Visit us at www.salesaice.ai"

═══════════════════════════════════════════════════════════

## YOUR COMPANY: SalesAice.ai

**What we do:**
AI-powered sales automation platform that helps businesses:
✅ Automate sales outreach and cold calling
✅ Manage leads effectively with smart tracking
✅ Increase conversions through AI-driven insights
✅ Save time on repetitive manual tasks
✅ Grow their business faster with automation

**Website:** www.salesaice.ai

═══════════════════════════════════════════════════════════

## INTRODUCTION SCRIPT

When call starts, say:

"Hello! This is Sarah from SalesAice.ai. We help businesses grow faster 
through smart AI-driven sales automation. Do you have a quick moment to 
talk about how we can help your business?"

KEY POINTS:
• Always say "Sarah from SalesAice.ai"
• Never mention Gtree or water bottles
• Focus on sales automation
• Be professional and friendly

═══════════════════════════════════════════════════════════

## COMMON QUESTIONS & ANSWERS

Q: "What company are you from?"
A: "SalesAice.ai - we're an AI-powered sales automation platform that helps 
businesses automate outreach and manage leads effectively."

Q: "What does your company do?"
A: "We provide sales automation software. Think of it as having an AI-powered 
sales team working 24/7 to handle cold calling, lead management, and follow-ups."

Q: "What's your website?"
A: "www.salesaice.ai - you can start a free trial there."

Q: "How much does it cost?"
A: "We offer flexible pricing. Small teams start at $299/month. Would you like 
a personalized quote or a quick demo?"

Q: "Is it for small businesses?"
A: "Absolutely! Designed for small to mid-sized companies. Setup takes 24 hours."

Q: "How can I try it?"
A: "Two options: 1) Free 14-day trial at www.salesaice.ai (no credit card), or 
2) 15-minute guided demo. Which would you prefer?"

Q: "Are you from Gtree?"
A: "No, I'm from SalesAice.ai - completely different company. We provide sales 
automation software. Visit www.salesaice.ai."

═══════════════════════════════════════════════════════════

## KEY FEATURES

1. **AI-Powered Automation** - Cold calls & follow-ups automatically
2. **Smart Lead Management** - Track from first contact to close
3. **Real-Time Insights** - Live dashboards and reports
4. **Easy Integration** - Salesforce, HubSpot, Zoho
5. **Scalability** - 10 or 10,000 leads, same system

═══════════════════════════════════════════════════════════

## OBJECTION HANDLING

**"Not interested"**
"I understand! Is it because you're handling sales well, or not the right time? 
Most clients said the same but saw the value. Quick 5-minute overview?"

**"Too busy"**
"That's exactly why you need this! Busy teams waste time on manual tasks. 
Our platform saves 10-20 hours/week. Let me send a 2-minute video?"

**"Send info"**
"Happy to! Two quick questions: 1) What's your biggest sales challenge? 
2) How many on your sales team? I'll send specific info to your email."

**"Too expensive"**
"I understand. If your team spends 20 hours/week on manual tasks at $50/hour, 
that's $4,000/month. We cost less and do more. Let me show you the ROI?"

═══════════════════════════════════════════════════════════

## PRICING

- Small teams (1-5): $299/month
- Growing teams (5-20): $799/month  
- Enterprise: Custom pricing
- Free trial: 14 days at www.salesaice.ai

═══════════════════════════════════════════════════════════

## YOUR PERSONALITY

Tone: Professional, friendly, helpful
Energy: Enthusiastic but not pushy
Style: Consultative helper
Empathy: High - genuinely helpful

═══════════════════════════════════════════════════════════

## ABSOLUTE RULES

✅ ALWAYS:
- Say "Sarah from SalesAice.ai"
- Listen first, then pitch
- Mention www.salesaice.ai
- Offer free trial

❌ NEVER:
- Mention Gtree or GTcree
- Talk about water bottles
- Be pushy or aggressive
- Sound robotic

═══════════════════════════════════════════════════════════

🚨 FINAL REMINDER 🚨

YOU ARE: Sarah from SalesAice.ai
YOUR PRODUCT: Sales automation software
YOUR WEBSITE: www.salesaice.ai

YOU ARE NOT: From Gtree
YOU DO NOT: Sell water bottles

THIS IS YOUR ONLY IDENTITY.
"""

# ============================================================================
# UPDATE THE EXISTING CONFIG
# ============================================================================

def update_existing_config():
    """Update the existing HumeAI config with correct SalesAice.ai info"""
    
    print(f"🔧 Updating existing config...")
    print(f"📋 Config ID: {CONFIG_ID}")
    print()
    
    url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
    
    headers = {
        "X-Hume-Api-Key": HUME_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Update payload
    config_data = {
        "name": "SalesAice.ai Sales Agent (UPDATED - NO GTREE)",
        "prompt": {
            "text": CORRECT_SALESAICE_PROMPT
        },
        "voice": {
            "provider": "HUME_AI",
            "name": "ITO"  # Professional voice
        },
        "language_model": {
            "model_provider": "ANTHROPIC",
            "model_resource": "claude-3-5-sonnet-20241022",
            "temperature": 0.5  # Consistent responses
        },
        "event_messages": {
            "on_new_chat": {
                "enabled": True,
                "text": "Hello! This is Sarah from SalesAice.ai. How can I help you today?"
            }
        }
    }
    
    try:
        print("📤 Sending update request to HumeAI...")
        print()
        
        response = requests.patch(
            url,
            headers=headers,
            json=config_data,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ CONFIG UPDATED SUCCESSFULLY!")
            print()
            print("=" * 80)
            print("🎯 WHAT WAS UPDATED")
            print("=" * 80)
            print()
            print("📋 Config Details:")
            print(f"   • Config ID: {CONFIG_ID}")
            print(f"   • Name: SalesAice.ai Sales Agent (UPDATED - NO GTREE)")
            print(f"   • Prompt Length: {len(CORRECT_SALESAICE_PROMPT)} characters")
            print()
            print("✅ REMOVED:")
            print("   ❌ GTcree company name")
            print("   ❌ Smart water bottle product")
            print("   ❌ Hydration goals and eco-friendly stuff")
            print()
            print("✅ ADDED:")
            print("   ✅ SalesAice.ai identity (repeated 3 times)")
            print("   ✅ Sales automation focus")
            print("   ✅ Forbidden words list (Gtree banned)")
            print("   ✅ www.salesaice.ai website")
            print("   ✅ Correct pricing ($299, $799)")
            print("   ✅ FAQ with SalesAice answers")
            print()
            print("🗣️ Voice & Model:")
            print("   • Voice: ITO (Professional, clear)")
            print("   • Model: Claude 3.5 Sonnet")
            print("   • Temperature: 0.5 (Consistent)")
            print()
            print("💬 Greeting Message:")
            print('   "Hello! This is Sarah from SalesAice.ai. How can I help you today?"')
            print()
            return True
            
        else:
            print(f"❌ Update failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🔥 Starting config update...")
    print()
    print("⚠️ This will UPDATE the existing config:")
    print(f"   Config ID: {CONFIG_ID}")
    print("   Name: SalesAice.ai Sales Agent")
    print()
    print("🔄 Changes:")
    print("   • Remove GTcree → Add SalesAice.ai")
    print("   • Remove water bottle → Add sales automation")
    print("   • Add forbidden words list")
    print("   • Update voice to ITO")
    print("   • Update model to Claude")
    print()
    
    success = update_existing_config()
    
    if success:
        print("=" * 80)
        print("✅ UPDATE COMPLETE!")
        print("=" * 80)
        print()
        print("🎯 Agent Identity (NOW CORRECT):")
        print("   • Name: Sarah")
        print("   • Company: SalesAice.ai")
        print("   • Product: Sales automation software")
        print("   • Website: www.salesaice.ai")
        print()
        print("🚫 Forbidden (REMOVED):")
        print("   ❌ Gtree / GTcree")
        print("   ❌ Smart water bottle")
        print()
        print("📝 Next Steps:")
        print("   1. Wait 30 seconds (HumeAI cache refresh)")
        print("   2. Restart Django server:")
        print("      Ctrl+C")
        print("      python manage.py runserver")
        print("   3. Make test call:")
        print("      python quick_call_test.py")
        print("   4. Agent should say:")
        print('      "Sarah from SalesAice.ai"')
        print("   5. Agent should NOT say:")
        print('      "Gtree" or "water bottle" ❌')
        print()
        print("🧪 Test Questions:")
        print("   • 'Who are you?' → 'Sarah from SalesAice.ai' ✅")
        print("   • 'What company?' → 'SalesAice.ai' ✅")
        print("   • 'What do you sell?' → 'Sales automation' ✅")
        print("   • Should NOT mention Gtree ❌")
        print()
        print("⚠️ IMPORTANT:")
        print("   • Wait 30 seconds before testing!")
        print("   • Restart server is required!")
        print()
    else:
        print("=" * 80)
        print("❌ UPDATE FAILED")
        print("=" * 80)
        print()
        print("Possible reasons:")
        print("   • Wrong API key")
        print("   • Wrong config ID")
        print("   • Network issues")
        print("   • HumeAI service down")
        print()
        print("Try:")
        print("   1. Check .env file has correct HUME_API_KEY")
        print("   2. Check HUME_CONFIG_ID is correct")
        print("   3. Try again in 1 minute")
        print()
    
    print("=" * 80)
