"""
🧪 Test HumeAgent Database Integration
======================================

Tests that HumeAgent model now has:
- sales_script_text
- business_info
- knowledge_files

And that hume_agent_service uses them correctly.
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from HumeAiTwilio.models import HumeAgent
from HumeAiTwilio.hume_agent_service import HumeAgentService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_humeagent_fields():
    """Test 1: Verify HumeAgent has new database fields"""
    print("\n" + "="*60)
    print("🧪 TEST 1: HumeAgent Model Fields")
    print("="*60)
    
    # Get HumeAgent model fields
    field_names = [f.name for f in HumeAgent._meta.get_fields()]
    
    # Check for required fields
    required_fields = ['sales_script_text', 'business_info', 'knowledge_files']
    
    print("\n📋 Checking for database integration fields:")
    for field in required_fields:
        if field in field_names:
            print(f"✅ {field} - FOUND")
        else:
            print(f"❌ {field} - MISSING")
            return False
    
    print("\n✅ All required fields exist in HumeAgent model!")
    return True


def test_create_humeagent_with_data():
    """Test 2: Create HumeAgent with sales_script and knowledge_base"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Create HumeAgent with Database Data")
    print("="*60)
    
    try:
        # Get existing user or use first available user
        try:
            user = User.objects.first()
            if not user:
                print("❌ No users found in database. Create a user first.")
                return None
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
        
        # Create HumeAgent with complete data
        agent = HumeAgent.objects.create(
            name="Test Sales Agent",
            system_prompt="You are a professional sales agent.",
            voice_name="ITO",
            language="en",
            
            # 🔥 NEW FIELDS - Database Integration
            sales_script_text="""Hi! I'm calling from TechSolutions.
We specialize in AI-powered business automation.
Are you interested in reducing your operational costs by 40%?""",
            
            business_info={
                "company_name": "TechSolutions Inc",
                "company_website": "www.techsolutions.com",
                "industry": "AI & Automation",
                "business_description": "We help businesses automate repetitive tasks using AI",
                "greeting": "Hello! This is TechSolutions calling."
            },
            
            knowledge_files={
                "product_catalog": "AI Assistant Pro ($299/mo), Business Automation Suite ($599/mo)",
                "pricing": "All plans include 24/7 support and free training",
                "features": "Natural language processing, Workflow automation, Integration with 50+ tools",
                "faqs": "Q: Setup time? A: 1-2 weeks | Q: Trial? A: 14-day free trial"
            },
            
            created_by=user,
            status='active'
        )
        
        print(f"\n✅ HumeAgent created: {agent.name} (ID: {agent.id})")
        print(f"📝 Sales Script: {agent.sales_script_text[:80]}...")
        print(f"📚 Business Info: {agent.business_info.get('company_name')}")
        print(f"📂 Knowledge Files: {list(agent.knowledge_files.keys())}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Error creating HumeAgent: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_service_integration(agent):
    """Test 3: Verify HumeAgentService uses database fields"""
    print("\n" + "="*60)
    print("🧪 TEST 3: HumeAgentService Database Integration")
    print("="*60)
    
    if not agent:
        print("❌ No agent provided for testing")
        return False
    
    try:
        service = HumeAgentService()
        
        # Test _build_system_prompt method
        base_prompt = "You are a helpful assistant."
        enhanced_prompt = service._build_system_prompt(base_prompt, agent)
        
        print(f"\n📝 Base prompt: {len(base_prompt)} chars")
        print(f"📝 Enhanced prompt: {len(enhanced_prompt)} chars")
        print(f"\n🔥 Enhanced Prompt Preview:")
        print("-" * 60)
        print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
        print("-" * 60)
        
        # Verify components are included
        checks = {
            "Sales Script": "SALES SCRIPT" in enhanced_prompt,
            "Business Info": "BUSINESS INFORMATION" in enhanced_prompt,
            "Knowledge Base": "KNOWLEDGE BASE" in enhanced_prompt,
            "Company Name": "TechSolutions" in enhanced_prompt
        }
        
        print(f"\n✅ Verification:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'Included' if result else 'Missing'}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("🧪 HumeAgent Database Integration Test Suite")
    print("🚀" * 30)
    
    # Test 1: Check fields exist
    if not test_humeagent_fields():
        print("\n❌ FAILED: Missing required fields")
        return
    
    # Test 2: Create agent with data
    agent = test_create_humeagent_with_data()
    if not agent:
        print("\n❌ FAILED: Could not create test agent")
        return
    
    # Test 3: Verify service integration
    if not test_service_integration(agent):
        print("\n❌ FAILED: Service integration not working")
        return
    
    # Cleanup
    print("\n" + "="*60)
    print("🧹 Cleanup")
    print("="*60)
    agent.delete()
    print("✅ Test agent deleted")
    
    # Final summary
    print("\n" + "🎉" * 30)
    print("✅ ALL TESTS PASSED!")
    print("🎉" * 30)
    print("\n📊 Summary:")
    print("  ✅ HumeAgent model has sales_script_text, business_info, knowledge_files")
    print("  ✅ HumeAgent can be created with database data")
    print("  ✅ HumeAgentService builds enhanced prompts from database")
    print("\n🚀 Ready for production calls with database integration!")


if __name__ == '__main__':
    main()
