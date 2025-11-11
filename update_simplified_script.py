"""
Update Test Agent with SIMPLIFIED sales script
Direct answers after greeting - no extra conversation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

def main():
    print("=" * 80)
    print("🔄 UPDATING TO SIMPLIFIED SALES SCRIPT")
    print("=" * 80)
    
    try:
        # Get Test Agent
        agent = HumeAgent.objects.get(name="Test Agent")
        
        print(f"\n✅ Found agent: {agent.name}")
        
        # SIMPLIFIED Sales Script - Just the essential parts
        simplified_script = """Hello! This is calling from SalesAice.ai — we help businesses grow faster through smart AI-driven sales automation.

Our platform automates repetitive sales tasks, helps track leads effectively, and gives real-time performance insights.

I'd love to quickly show you how it works. Would you like me to share a short demo or a quick overview?"""
        
        # SIMPLIFIED Business Info
        business_info = {
            "company_name": "SalesAice.ai",
            "company_website": "www.salesaice.ai",
            "industry": "AI-Powered Sales Automation",
            "business_description": "SalesAice.ai is an AI-powered sales automation platform designed to help businesses improve lead management, automate outreach, and increase conversions through smart data insights."
        }
        
        # SIMPLIFIED Knowledge Base - Just Q&A
        knowledge_files = {
            "common_questions_and_answers": """Q: What exactly does your software do?
A: SalesAice.ai automates sales outreach, manages leads, and provides insights using AI — so your team can focus on closing deals, not manual tasks.

Q: How much does it cost?
A: We offer flexible pricing based on your team size and usage — I can share a quote or schedule a quick demo for you.

Q: Is it suitable for small businesses?
A: Absolutely! Many of our clients are small to mid-sized companies — we designed it to be simple, scalable, and affordable.

Q: How can I try it?
A: You can start with a free trial right from our website: www.salesaice.ai"""
        }
        
        # Update agent
        agent.sales_script_text = simplified_script
        agent.business_info = business_info
        agent.knowledge_files = knowledge_files
        agent.save()
        
        print(f"\n✅ Updated with SIMPLIFIED script!")
        print(f"\n📋 What's included:")
        print(f"   ✅ Sales Script: {len(simplified_script)} chars")
        print(f"   ✅ Business Info: {len(business_info)} fields")
        print(f"   ✅ Q&A Knowledge: 4 questions")
        
        print(f"\n📄 SALES SCRIPT:")
        print("-" * 80)
        print(simplified_script[:200] + "...")
        print("-" * 80)
        
        print(f"\n💡 Now agent will:")
        print(f"   1. Greet: 'Hello! How are you today?'")
        print(f"   2. When asked purpose → Use sales script")
        print(f"   3. When asked questions → Use exact Q&A answers")
        
        print(f"\n⚠️  IMPORTANT: Need to update HumeAI config with new simplified prompt!")
        print(f"\n📌 Run: python update_humeai_post.py")
        
    except HumeAgent.DoesNotExist:
        print("\n❌ Test Agent not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
