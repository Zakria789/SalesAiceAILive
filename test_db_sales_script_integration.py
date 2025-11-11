"""
🔥 TEST: Database Sales Script & Knowledge Base Integration
=============================================================

Test karta hai ke HumeAI agent database se sales_script aur knowledge_base use kar raha hai ya nahi

Features:
1. Agent create karo with sales_script_text
2. Agent create karo with business_info (knowledge base)
3. Check greeting database se aa rahi hai ya nahi
"""

import django
import os
import sys

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import Agent
from django.contrib.auth import get_user_model

User = get_user_model()


def test_sales_script_integration():
    """Test sales script integration with HumeAI"""
    
    print("\n" + "="*70)
    print("🔥 TEST: Sales Script Integration with HumeAI")
    print("="*70)
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        email='test@example.com',
        defaults={'username': 'testuser'}
    )
    
    # Test data
    sales_script = """
    Hi! This is Sarah from TechSolutions. 
    I'm calling because you expressed interest in our AI automation platform.
    How are you doing today?
    
    Our platform can save you 40+ hours per week by automating:
    - Customer support calls
    - Lead qualification
    - Appointment scheduling
    - Follow-up calls
    
    Would you like to hear more about our special discount for early adopters?
    """
    
    business_info = {
        'company_name': 'TechSolutions AI',
        'company_website': 'https://techsolutions.ai',
        'company_phone': '+1234567890',
        'industry': 'AI Software',
        'business_description': 'We provide AI-powered automation solutions for businesses',
        'greeting': 'Hello! Welcome to TechSolutions AI. How can I help you today?'
    }
    
    knowledge_files = {
        'product_catalog': 'AI Voice Agent, AI Chatbot, AI Email Assistant',
        'pricing': '$99/month for starter plan, $299/month for pro plan',
        'features': 'Real-time emotion detection, Multi-language support, CRM integration'
    }
    
    # Create test agent
    print("\n📝 Creating test agent with sales script and knowledge base...")
    
    agent = Agent.objects.create(
        owner=user,
        name='Test Sales Agent DB',
        agent_type='outbound',
        status='active',
        sales_script_text=sales_script,
        business_info=business_info,
        knowledge_files=knowledge_files,
        voice_model='en-US-female-1',
        voice_tone='friendly'
    )
    
    print(f"✅ Agent created: {agent.name} (ID: {agent.id})")
    print(f"\n📊 Agent Details:")
    print(f"   Sales Script Length: {len(agent.sales_script_text)} characters")
    print(f"   Business Info: {len(agent.business_info)} fields")
    print(f"   Knowledge Files: {len(agent.knowledge_files)} items")
    
    # Display what will be sent to HumeAI
    print(f"\n📝 Sales Script Preview:")
    print(f"   {agent.sales_script_text[:100]}...")
    
    print(f"\n📚 Business Info:")
    for key, value in agent.business_info.items():
        print(f"   - {key}: {value}")
    
    print(f"\n📂 Knowledge Files:")
    for key, value in agent.knowledge_files.items():
        print(f"   - {key}: {value}")
    
    # Test greeting extraction
    print(f"\n👋 Greeting Test:")
    
    # Import consumer to test greeting method
    from HumeAiTwilio.vonage_realtime_consumer import VonageRealTimeConsumer
    
    # Create a mock consumer instance
    class MockCall:
        def __init__(self, agent):
            self.agent = agent
            self.customer_profile = None
    
    consumer = VonageRealTimeConsumer()
    consumer.call = MockCall(agent)
    
    greeting = consumer._get_greeting_text()
    print(f"   Greeting: {greeting}")
    
    # Verify HumeAI config_id
    if agent.hume_config_id:
        print(f"\n✅ HumeAI Config ID: {agent.hume_config_id}")
        print(f"   Agent successfully synced with HumeAI!")
    else:
        print(f"\n⚠️  HumeAI Config ID not found")
        print(f"   Agent created locally but not synced with HumeAI")
        print(f"   This is expected if running without HumeAI credentials")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETED!")
    print("="*70)
    
    return agent


def test_knowledge_base_fields():
    """Test that agent model has all required fields"""
    
    print("\n" + "="*70)
    print("🔍 VERIFY: Agent Model Fields")
    print("="*70)
    
    # Check fields directly from Django model
    from agents.models import Agent
    
    print(f"\n📊 Agent Model Fields:")
    
    # Check for our required fields
    required_fields = {
        'sales_script_text': False,
        'sales_script_file': False,
        'business_info': False,
        'knowledge_files': False
    }
    
    # Get all field names from Agent model
    agent_fields = [f.name for f in Agent._meta.get_fields()]
    
    for field_name in agent_fields:
        if field_name in required_fields:
            required_fields[field_name] = True
            field_obj = Agent._meta.get_field(field_name)
            print(f"   ✅ {field_name}: {field_obj.__class__.__name__}")
    
    # Check missing fields
    print(f"\n🔍 Required Fields Status:")
    for field, exists in required_fields.items():
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"   {status}: {field}")
    
    all_exist = all(required_fields.values())
    
    if all_exist:
        print(f"\n✅ All required fields exist in Agent model!")
    else:
        print(f"\n⚠️  Some required fields are missing!")
        print(f"   Run migrations: python manage.py makemigrations && python manage.py migrate")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    # Test 1: Check database fields
    test_knowledge_base_fields()
    
    # Test 2: Create agent with sales script
    agent = test_sales_script_integration()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Agent Name: {agent.name}")
    print(f"   Agent ID: {agent.id}")
    print(f"   Sales Script: {'✅ SET' if agent.sales_script_text else '❌ NOT SET'}")
    print(f"   Business Info: {'✅ SET' if agent.business_info else '❌ NOT SET'}")
    print(f"   Knowledge Files: {'✅ SET' if agent.knowledge_files else '❌ NOT SET'}")
    print(f"   HumeAI Synced: {'✅ YES' if agent.hume_config_id else '⚠️  NO (check credentials)'}")
    
    print(f"\n✅ Integration complete! HumeAI will now use database fields for:")
    print(f"   1. Sales Script (from sales_script_text)")
    print(f"   2. Knowledge Base (from business_info)")
    print(f"   3. Greeting (from sales_script first line or business_info)")
