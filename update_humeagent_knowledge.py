"""
🔧 Update Existing HumeAgent with Database Knowledge
====================================================

This script updates your existing HumeAgent to include:
- Sales script
- Business information
- Knowledge base

Run after database integration is complete.
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from HumeAiTwilio.models import HumeAgent

def update_humeagent():
    """Update existing HumeAgent with sales script and knowledge base"""
    
    print("\n" + "="*60)
    print("🔧 HumeAgent Database Integration Update")
    print("="*60)
    
    # List all HumeAgents
    agents = HumeAgent.objects.filter(status='active')
    
    if not agents.exists():
        print("\n❌ No active HumeAgents found")
        print("Create a new agent first using the API or admin panel")
        return
    
    print(f"\n📋 Found {agents.count()} active HumeAgent(s):")
    for i, agent in enumerate(agents, 1):
        print(f"  {i}. {agent.name} (ID: {agent.id})")
    
    # Select agent to update
    try:
        choice = input(f"\nEnter agent number to update (1-{agents.count()}) or 'all' for all agents: ").strip().lower()
        
        if choice == 'all':
            selected_agents = agents
        else:
            idx = int(choice) - 1
            if idx < 0 or idx >= agents.count():
                print("❌ Invalid choice")
                return
            selected_agents = [list(agents)[idx]]
    
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Update cancelled")
        return
    
    # Get data to add
    print("\n" + "="*60)
    print("📝 Enter Sales Script & Knowledge Base")
    print("="*60)
    print("(Press Enter to skip any field)")
    
    sales_script = input("\n1. Sales Script (multi-line, end with empty line):\n")
    if sales_script:
        lines = [sales_script]
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        sales_script = "\n".join(lines)
    
    # Business Info
    company_name = input("\n2. Company Name: ").strip()
    company_website = input("3. Company Website: ").strip()
    industry = input("4. Industry: ").strip()
    description = input("5. Business Description: ").strip()
    greeting = input("6. Custom Greeting: ").strip()
    
    business_info = {}
    if company_name:
        business_info['company_name'] = company_name
    if company_website:
        business_info['company_website'] = company_website
    if industry:
        business_info['industry'] = industry
    if description:
        business_info['business_description'] = description
    if greeting:
        business_info['greeting'] = greeting
    
    # Knowledge Files
    print("\n7. Knowledge Base (enter key-value pairs, empty key to finish):")
    knowledge_files = {}
    while True:
        key = input("   Key (e.g., 'products', 'pricing'): ").strip()
        if not key:
            break
        value = input(f"   Value for '{key}': ").strip()
        if value:
            knowledge_files[key] = value
    
    # Update agent(s)
    print("\n" + "="*60)
    print("💾 Updating Agent(s)")
    print("="*60)
    
    for agent in selected_agents:
        print(f"\n📝 Updating: {agent.name}")
        
        if sales_script:
            agent.sales_script_text = sales_script
            print(f"  ✅ Sales script added ({len(sales_script)} chars)")
        
        if business_info:
            agent.business_info = business_info
            print(f"  ✅ Business info added: {list(business_info.keys())}")
        
        if knowledge_files:
            agent.knowledge_files = knowledge_files
            print(f"  ✅ Knowledge files added: {list(knowledge_files.keys())}")
        
        agent.save()
        print(f"  💾 Agent saved!")
    
    # Summary
    print("\n" + "🎉" * 30)
    print(f"✅ Successfully updated {len(selected_agents)} agent(s)!")
    print("🎉" * 30)
    print("\n📊 Next Steps:")
    print("  1. Make a test call to verify database integration")
    print("  2. Agent will now use sales script and knowledge base")
    print("  3. Check logs to see enhanced prompt being built")
    print("\n🚀 Your agents are now database-powered!")


def quick_update_example():
    """Quick update with example data"""
    
    print("\n" + "="*60)
    print("⚡ Quick Update with Example Data")
    print("="*60)
    
    agents = HumeAgent.objects.filter(status='active')
    
    if not agents.exists():
        print("\n❌ No active HumeAgents found")
        return
    
    agent = agents.first()
    print(f"\n📝 Updating: {agent.name}")
    
    # Example data
    agent.sales_script_text = """Hi! This is calling from TechSolutions.
We specialize in AI-powered business automation.
Our solutions can help reduce your operational costs by up to 40%.
Are you interested in learning more about how we can help your business?"""
    
    agent.business_info = {
        "company_name": "TechSolutions Inc",
        "company_website": "www.techsolutions.com",
        "industry": "AI & Business Automation",
        "business_description": "We help businesses automate repetitive tasks using cutting-edge AI technology",
        "greeting": "Hello! This is TechSolutions calling."
    }
    
    agent.knowledge_files = {
        "product_catalog": "AI Assistant Pro ($299/mo), Business Automation Suite ($599/mo), Enterprise Plan ($999/mo)",
        "pricing": "All plans include 24/7 support, free onboarding, and unlimited users",
        "features": "Natural language processing, Workflow automation, CRM integration, Analytics dashboard",
        "faqs": "Q: How long is setup? A: 1-2 weeks | Q: Do you offer trials? A: Yes, 14-day free trial | Q: Can we cancel anytime? A: Yes, no contracts"
    }
    
    agent.save()
    
    print(f"✅ Updated with example data!")
    print(f"\n📝 Sales Script: {agent.sales_script_text[:80]}...")
    print(f"📚 Business Info: {agent.business_info.get('company_name')}")
    print(f"📂 Knowledge Files: {list(agent.knowledge_files.keys())}")
    print("\n🎉 Done! Make a test call to see it in action.")


if __name__ == '__main__':
    import sys
    
    print("\n" + "🚀" * 30)
    print("🔧 HumeAgent Database Integration Updater")
    print("🚀" * 30)
    
    print("\nChoose an option:")
    print("  1. Manual update (enter your own data)")
    print("  2. Quick update (use example data)")
    print("  3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        update_humeagent()
    elif choice == '2':
        quick_update_example()
    elif choice == '3':
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice")
