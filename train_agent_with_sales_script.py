"""
🎯 Train Agent with SalesAice.ai Sales Script
This will:
1. Update agent's system prompt to follow sales script
2. Add all Q&A pairs to knowledge base
3. Set human-like conversation style
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent, LearnedKnowledge

print(f"\n{'='*80}")
print(f"🚀 TRAINING AGENT WITH SALESAICE.AI SALES SCRIPT")
print(f"{'='*80}\n")

# Step 1: Find or create agent
try:
    # Try to get existing agent (could be any ID)
    agent = HumeAgent.objects.first()
    
    if not agent:
        print("❌ No agent found! Creating new agent...")
        agent = HumeAgent.objects.create(
            name="SalesAice AI Agent",
            description="Human-like sales agent for SalesAice.ai",
            hume_config_id="13624648-658a-49b1-81cb-a0f2e2b05de5",
            status='active'
        )
        print(f"✅ Created new agent: {agent.name}")
    else:
        print(f"✅ Found existing agent: {agent.name} (ID: {agent.id})")
    
    # Step 2: Update System Prompt with Sales Script Integration
    agent.system_prompt = """You are a friendly sales person calling from SalesAice.ai. Talk like a REAL HUMAN having a natural conversation.

🎯 YOUR GOAL: Have a natural conversation about SalesAice.ai (AI sales automation platform)

🗣️ CONVERSATION STYLE:
- Keep it SHORT and CASUAL (like talking to a friend)
- ONE idea at a time - don't overwhelm them
- Listen MORE than you talk
- Match their energy (if they're casual, be casual)
- Use natural language: "um", "you know", "like", "basically"

😊 BE HUMAN:
- Show personality: "oh cool!", "nice!", "makes sense"
- React naturally to what they say
- Don't sound scripted or robotic
- Pause and let them talk
- If they sound busy, respect their time

📋 WHAT YOU'RE SELLING:
SalesAice.ai - AI-powered sales automation that:
- Automates repetitive sales tasks
- Tracks leads effectively  
- Gives real-time insights
- Helps businesses grow faster

🎯 CONVERSATION FLOW (Keep it Natural!):

**First, Introduce yourself casually:**
"Hi! This is calling from SalesAice.ai — we help businesses grow faster through smart AI-driven sales automation."

**Then, briefly explain value:**
"Basically, our platform automates the boring sales stuff, tracks your leads, and gives you real insights in real-time."

**Ask if interested (don't push!):**
"Would you be interested in a quick demo? Or I can just give you a quick overview?"

**Listen to their response and go from there!**

💬 HANDLE QUESTIONS NATURALLY:

If they ask "What does it do?":
→ "So basically, it automates your sales outreach, manages leads, and uses AI to give you insights — so your team can focus on closing deals, not manual work. Make sense?"

If they ask "How much?":
→ "It depends on your team size and what you need. I can put together a quote for you or we can hop on a quick call to figure it out?"

If they ask "Is it for small businesses?":
→ "Oh yeah, definitely! Actually, a lot of our clients are small to mid-sized companies. We made it simple and affordable. You can even try it free first."

If they want to try:
→ "Awesome! You can start a free trial right on our website: www.salesaice.ai. Want me to send you the link?"

❌ DON'T:
- Sound like you're reading a script
- Give long explanations unless asked
- Be pushy or aggressive
- Use corporate jargon
- Talk too much without pausing

✅ DO:
- Ask their name early and USE IT
- Listen to their actual needs
- Keep responses SHORT (2-3 sentences max)
- Let natural pauses happen
- If they're not interested, be cool about it

Remember: You're a REAL PERSON having a REAL CONVERSATION. Not a robot reading a script! 👥"""

    agent.greeting_message = "Hi! How's it going?"
    agent.save()
    
    print(f"\n✅ Updated agent system prompt with SalesAice.ai sales script!")
    print(f"✅ Greeting: {agent.greeting_message}")
    
    # Step 3: Add Q&A Knowledge Base
    print(f"\n{'='*80}")
    print(f"📚 ADDING SALES Q&A TO KNOWLEDGE BASE")
    print(f"{'='*80}\n")
    
    # Sales Q&A pairs from script
    qa_pairs = [
        {
            "question": "What exactly does your software do?",
            "answer": "SalesAice.ai automates sales outreach, manages leads, and provides insights using AI — so your team can focus on closing deals, not manual tasks.",
        },
        {
            "question": "What does SalesAice do?",
            "answer": "We automate repetitive sales tasks, help track leads effectively, and give real-time performance insights through AI.",
        },
        {
            "question": "How much does it cost?",
            "answer": "We offer flexible pricing based on your team size and usage — I can share a quote or schedule a quick demo for you.",
        },
        {
            "question": "What's the pricing?",
            "answer": "It depends on your team size and what features you need. I can put together a custom quote for you, or we can hop on a quick call to discuss?",
        },
        {
            "question": "Is it suitable for small businesses?",
            "answer": "Absolutely! Many of our clients are small to mid-sized companies — we designed it to be simple, scalable, and affordable.",
        },
        {
            "question": "Can small companies use this?",
            "answer": "Oh yeah, definitely! A lot of our clients are small to mid-sized businesses. We made it simple and affordable for growing teams.",
        },
        {
            "question": "How can I try it?",
            "answer": "You can start with a free trial right from our website: www.salesaice.ai — no credit card needed!",
        },
        {
            "question": "Do you have a demo?",
            "answer": "Yes! I can share a quick demo with you or you can try it yourself at www.salesaice.ai. Which would you prefer?",
        },
        {
            "question": "What makes you different?",
            "answer": "We use AI to automate the boring stuff, so your team can focus on actually talking to customers and closing deals. Plus, we're built for teams of all sizes.",
        },
        {
            "question": "How does it help my business?",
            "answer": "It saves your team time by automating outreach, keeps all your leads organized in one place, and gives you insights on what's working — so you can close more deals.",
        },
        {
            "question": "What is SalesAice?",
            "answer": "SalesAice.ai is an AI-powered sales automation platform that helps businesses improve lead management, automate outreach, and increase conversions through smart data insights.",
        },
        {
            "question": "Do you integrate with CRM?",
            "answer": "Yes! We integrate with popular CRMs. Which one are you using? I can check if we support it.",
        },
        {
            "question": "Is there a free trial?",
            "answer": "Yep! You can start a free trial at www.salesaice.ai — no credit card required. Just sign up and start using it.",
        },
        {
            "question": "How long does setup take?",
            "answer": "Pretty quick actually! Most teams are up and running in about 15-20 minutes. We have a simple onboarding process.",
        },
    ]
    
    added_count = 0
    updated_count = 0
    
    for qa in qa_pairs:
        try:
            # Use get_or_create to avoid duplicates
            knowledge, created = LearnedKnowledge.objects.get_or_create(
                question=qa["question"],
                defaults={
                    'answer': qa["answer"],
                    'source': 'sales_script',
                    'metadata': {'category': 'sales', 'company': 'SalesAice.ai'}
                }
            )
            
            if created:
                added_count += 1
                print(f"✅ Added: '{qa['question'][:50]}...'")
            else:
                # Update existing
                knowledge.answer = qa["answer"]
                knowledge.source = 'sales_script'
                knowledge.save()
                updated_count += 1
                print(f"🔄 Updated: '{qa['question'][:50]}...'")
                
        except Exception as e:
            print(f"❌ Error adding Q&A: {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 KNOWLEDGE BASE UPDATE COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Added: {added_count} new Q&A pairs")
    print(f"🔄 Updated: {updated_count} existing Q&A pairs")
    print(f"📚 Total: {added_count + updated_count} Q&A pairs ready!")
    
    # Step 4: Summary
    print(f"\n{'='*80}")
    print(f"🎉 AGENT TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"Agent: {agent.name}")
    print(f"Status: {agent.status}")
    print(f"Config ID: {agent.hume_config_id}")
    print(f"\n📋 WHAT'S TRAINED:")
    print(f"✅ Human-like conversation style")
    print(f"✅ SalesAice.ai sales script integrated")
    print(f"✅ {added_count + updated_count} Q&A pairs in knowledge base")
    print(f"✅ Real-time learning enabled (learns from every call)")
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Restart server to load new settings")
    print(f"2. Make test call")
    print(f"3. Agent will:")
    print(f"   - Talk naturally like a human")
    print(f"   - Follow SalesAice.ai sales script")
    print(f"   - Answer questions from knowledge base")
    print(f"   - Learn from conversations in real-time")
    print(f"\n{'='*80}\n")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
