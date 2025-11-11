"""
Test Agent Creation API - Verify Prompt & HumeAI Sync
Tests if agent creation API properly:
1. Saves agent to database
2. Syncs to HumeAI with enhanced prompt (sales_script + knowledge_base)
3. Returns correct hume_config_id
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.models import Agent
from HumeAiTwilio.hume_agent_service import hume_agent_service

User = get_user_model()

def test_agent_creation():
    """Test agent creation with sales script and business info"""
    
    print("\n" + "="*80)
    print("🧪 TESTING AGENT CREATION API FLOW")
    print("="*80)
    
    # Get first user
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        print(f"✅ Using user: {user.email}")
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    # Test data
    test_agent_data = {
        'name': f'Test Agent {os.urandom(4).hex()}',  # Unique name
        'agent_type': 'outbound',
        'system_prompt': 'You are a professional sales agent helping customers.',
        'voice_name': 'Ito',
        'language': 'en',
        'status': 'active',
        
        # Sales script
        'sales_script_text': '''
STEP 1: Introduction
- Greet the customer warmly
- Introduce yourself and company
- Ask if they have a few minutes to talk

STEP 2: Discovery
- Ask about their current challenges
- Listen actively to their needs
- Show empathy and understanding

STEP 3: Solution Presentation
- Present our product features that match their needs
- Highlight key benefits
- Share success stories

STEP 4: Handle Objections
- Address concerns professionally
- Provide evidence and testimonials
- Offer guarantees or trial periods

STEP 5: Close
- Summarize the key benefits
- Create urgency with limited-time offer
- Ask for commitment
''',
        
        # Business info (JSON)
        'business_info': json.dumps({
            'company_name': 'TechSolutions Inc',
            'website': 'https://techsolutions.example.com',
            'industry': 'Software Development',
            'features': [
                'Cloud-based platform',
                '24/7 customer support',
                'Advanced analytics dashboard',
                'Mobile app included'
            ],
            'pricing': {
                'basic': '$99/month',
                'pro': '$199/month',
                'enterprise': 'Custom pricing'
            },
            'customers': 'Over 5000 businesses worldwide'
        })
    }
    
    print(f"\n📋 Test Agent Data:")
    print(f"   Name: {test_agent_data['name']}")
    print(f"   Type: {test_agent_data['agent_type']}")
    print(f"   System Prompt: {test_agent_data['system_prompt'][:50]}...")
    print(f"   Sales Script: {len(test_agent_data['sales_script_text'])} chars")
    print(f"   Business Info: {len(test_agent_data['business_info'])} chars")
    
    # Step 1: Create agent in database
    print(f"\n🔹 STEP 1: Creating agent in database...")
    try:
        agent = Agent.objects.create(
            owner=user,
            name=test_agent_data['name'],
            agent_type=test_agent_data['agent_type'],
            system_prompt=test_agent_data['system_prompt'],
            voice_name=test_agent_data['voice_name'],
            language=test_agent_data['language'],
            status=test_agent_data['status'],
            sales_script_text=test_agent_data['sales_script_text'],
            business_info=test_agent_data['business_info']
        )
        print(f"✅ Agent created in database with ID: {agent.id}")
        print(f"   Sales Script: {'✅ Saved' if agent.sales_script_text else '❌ Empty'}")
        print(f"   Business Info: {'✅ Saved' if agent.business_info else '❌ Empty'}")
    except Exception as e:
        print(f"❌ Failed to create agent in database: {e}")
        return
    
    # Step 2: Sync to HumeAI
    print(f"\n🔹 STEP 2: Syncing to HumeAI...")
    try:
        config_id = hume_agent_service.create_agent(
            name=agent.name,
            system_prompt=agent.system_prompt,
            voice_name=agent.voice_name,
            language=agent.language,
            agent_obj=agent  # Pass full agent object with sales_script & business_info
        )
        
        if config_id:
            print(f"✅ HumeAI agent created successfully")
            print(f"   Config ID: {config_id}")
            
            # Save config_id to agent
            agent.hume_config_id = config_id
            agent.save(update_fields=['hume_config_id'])
            print(f"✅ Config ID saved to database")
        else:
            print(f"❌ Failed to create HumeAI agent (no config_id returned)")
            
    except Exception as e:
        print(f"❌ HumeAI sync error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Verify agent in database
    print(f"\n🔹 STEP 3: Verifying agent in database...")
    try:
        agent.refresh_from_db()
        print(f"✅ Agent verification:")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Type: {agent.agent_type}")
        print(f"   Status: {agent.status}")
        print(f"   HumeAI Config ID: {agent.hume_config_id or '❌ Not synced'}")
        print(f"   System Prompt: {len(agent.system_prompt)} chars")
        print(f"   Sales Script: {len(agent.sales_script_text) if agent.sales_script_text else 0} chars")
        print(f"   Business Info: {len(agent.business_info) if agent.business_info else 0} chars")
        
        if agent.sales_script_text:
            print(f"\n📝 Sales Script Preview:")
            print(agent.sales_script_text[:200] + "...")
        
        if agent.business_info:
            print(f"\n📚 Business Info Preview:")
            try:
                info = json.loads(agent.business_info)
                print(f"   Company: {info.get('company_name', 'N/A')}")
                print(f"   Website: {info.get('website', 'N/A')}")
                print(f"   Industry: {info.get('industry', 'N/A')}")
                print(f"   Features: {len(info.get('features', []))} items")
            except:
                print(f"   Raw: {agent.business_info[:100]}...")
                
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    # Step 4: Check HumeAI agent details
    if agent.hume_config_id:
        print(f"\n🔹 STEP 4: Fetching HumeAI agent details...")
        try:
            hume_agent = hume_agent_service.get_agent(agent.hume_config_id)
            
            if hume_agent:
                print(f"✅ HumeAI agent found:")
                print(f"   Config ID: {hume_agent.get('id', 'N/A')}")
                print(f"   Name: {hume_agent.get('name', 'N/A')}")
                print(f"   Version: {hume_agent.get('version', 'N/A')}")
                
                # Check prompt
                prompt_data = hume_agent.get('prompt', {})
                prompt_text = prompt_data.get('text', '')
                print(f"\n📋 Prompt Details:")
                print(f"   Length: {len(prompt_text)} chars")
                print(f"   Contains Sales Script: {'✅ Yes' if 'STEP 1' in prompt_text else '❌ No'}")
                print(f"   Contains Business Info: {'✅ Yes' if 'TechSolutions' in prompt_text else '❌ No'}")
                
                if len(prompt_text) > 0:
                    print(f"\n📝 Prompt Preview (first 500 chars):")
                    print(prompt_text[:500] + "...")
                
                # Check model
                model_data = hume_agent.get('ellm_model', {})
                print(f"\n🤖 Model Configuration:")
                print(f"   Provider: {model_data.get('provider', 'N/A')}")
                print(f"   Model: {model_data.get('model', 'N/A')}")
                
                # Check tools
                tools = hume_agent.get('builtin_tools', [])
                print(f"\n🔧 Builtin Tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'N/A')}: {'✅ Enabled' if tool.get('enabled') else '❌ Disabled'}")
                
                # Check voice
                voice_data = hume_agent.get('voice', {})
                print(f"\n🗣️ Voice Configuration:")
                print(f"   Provider: {voice_data.get('provider', 'N/A')}")
                print(f"   Name: {voice_data.get('name', 'N/A')}")
                
            else:
                print(f"❌ HumeAI agent not found")
                
        except Exception as e:
            print(f"❌ Error fetching HumeAI agent: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Ask if should clean up
    print(f"\n🗑️  Test agent created: {agent.name}")
    cleanup = input("Delete test agent? (y/n): ").strip().lower()
    
    if cleanup == 'y':
        print(f"\n🗑️  Cleaning up...")
        try:
            # Delete from HumeAI first
            if agent.hume_config_id:
                hume_agent_service.delete_agent(agent.hume_config_id)
                print(f"✅ Deleted from HumeAI")
            
            # Delete from database
            agent.delete()
            print(f"✅ Deleted from database")
            print(f"✅ Cleanup complete")
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
    else:
        print(f"⚠️  Test agent left in database")
        print(f"   Agent ID: {agent.id}")
        print(f"   Agent Name: {agent.name}")

if __name__ == "__main__":
    test_agent_creation()
