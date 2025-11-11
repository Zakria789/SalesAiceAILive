"""
🔥 Update Test Agent with Sales Script & Knowledge Base
======================================================

This will add sales script and knowledge to your "Test Agent"
that was used in the last call.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from HumeAiTwilio.models import HumeAgent

# Get Test Agent
agent = HumeAgent.objects.get(id='b77dd00d-0221-4074-a2a3-442e0cce9772')

print(f"\n🤖 Updating Agent: {agent.name}")
print(f"   ID: {agent.id}")

# 🔥 Add Sales Script (SalesAice.ai Real Script)
agent.sales_script_text = """Hello! This is calling from SalesAice.ai — we help businesses grow faster through smart AI-driven sales automation.

Our platform automates repetitive sales tasks, helps track leads effectively, and gives real-time performance insights.

I'd love to quickly show you how it works. Would you like me to share a short demo or a quick overview?"""

print(f"\n✅ Sales Script Added ({len(agent.sales_script_text)} characters)")

# 🔥 Add Business Information (SalesAice.ai)
agent.business_info = {
    "company_name": "SalesAice.ai",
    "company_website": "www.salesaice.ai",
    "industry": "AI-Powered Sales Automation",
    "business_description": "SalesAice.ai is an AI-powered sales automation platform designed to help businesses improve lead management, automate outreach, and increase conversions through smart data insights.",
    "greeting": "Hello! This is calling from SalesAice.ai.",
    "tagline": "Grow faster through smart AI-driven sales automation",
    "target_market": "Small to mid-sized companies looking to automate sales"
}

print(f"✅ Business Info Added: {list(agent.business_info.keys())}")

# 🔥 Add Knowledge Base Files (SalesAice.ai FAQs & Info)
agent.knowledge_files = {
    "product_overview": """
    SalesAice.ai - AI-Powered Sales Automation Platform
    
    Key Features:
    ✅ Automates repetitive sales tasks
    ✅ Manages leads effectively
    ✅ Provides real-time performance insights
    ✅ AI-driven sales automation
    ✅ Smart data insights for conversions
    
    Purpose:
    Help businesses improve lead management, automate outreach, and increase conversions.
    """,
    
    "common_questions_and_answers": """
    Q: What exactly does your software do?
    A: SalesAice.ai automates sales outreach, manages leads, and provides insights using AI — so your team can focus on closing deals, not manual tasks.
    
    Q: How much does it cost?
    A: We offer flexible pricing based on your team size and usage — I can share a quote or schedule a quick demo for you.
    
    Q: Is it suitable for small businesses?
    A: Absolutely! Many of our clients are small to mid-sized companies — we designed it to be simple, scalable, and affordable.
    
    Q: How can I try it?
    A: You can start with a free trial right from our website: www.salesaice.ai
    """,
    
    "sales_process": """
    Step 1 — Introduction
    "Hello! This is [Agent Name] calling from SalesAice.ai — we help businesses grow faster through smart AI-driven sales automation."
    
    Step 2 — Value Proposition
    "Our platform automates repetitive sales tasks, helps track leads effectively, and gives real-time performance insights."
    
    Step 3 — Engagement Question
    "I'd love to quickly show you how it works. Would you like me to share a short demo or a quick overview?"
    """,
    
    "key_benefits": """
    ✅ Save time by automating manual sales tasks
    ✅ Track leads effectively with AI
    ✅ Get real-time insights on performance
    ✅ Focus on closing deals, not repetitive work
    ✅ Increase conversions with smart data
    ✅ Simple, scalable, and affordable
    ✅ Perfect for small to mid-sized businesses
    """,
    
    "next_steps": """
    Options for Interested Customers:
    1. Schedule a quick demo
    2. Share a quick overview
    3. Start a free trial at www.salesaice.ai
    4. Get a personalized quote based on team size
    """
}

print(f"✅ Knowledge Base Added: {list(agent.knowledge_files.keys())}")

# 💾 Save Agent
agent.save()

print(f"\n💾 Agent Updated Successfully!")
print(f"\n📊 Summary:")
print(f"  📝 Sales Script: {len(agent.sales_script_text)} characters")
print(f"  📚 Business Info: {len(agent.business_info)} fields")
print(f"  📂 Knowledge Files: {len(agent.knowledge_files)} categories")

print(f"\n🎉 Done! Next call will use this database knowledge!")
print(f"\n🔥 Make a test call to see it in action:")
print(f"   python make_test_call.py")
