"""
🧪 TEST AGENT AUTO-SYNC
========================

Test automatic HumeAI agent creation with config ID sync
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

def test_agent_creation():
    """Test creating agent with auto HumeAI sync"""
    
    print("\n" + "="*60)
    print("🧪 TESTING AGENT AUTO-SYNC WITH HUMEAI")
    print("="*60 + "\n")
    
    # Create test agent
    agent = HumeAgent.objects.create(
        name="Test Auto-Sync Agent",
        description="Test agent for auto HumeAI sync",
        system_prompt="You are a helpful AI assistant testing auto-sync functionality.",
        voice_name="ITO",
        language="en",
        greeting_message="Hello! I'm a test agent.",
        status="active"
    )
    
    print(f"✅ Local agent created:")
    print(f"   ID: {agent.id}")
    print(f"   Name: {agent.name}")
    print(f"   HumeAI Config ID: {agent.hume_config_id or 'Not synced yet...'}")
    
    # Refresh from database to get updated config_id
    agent.refresh_from_db()
    
    print(f"\n🔄 After signal processing:")
    print(f"   HumeAI Config ID: {agent.hume_config_id or 'FAILED TO SYNC!'}")
    
    if agent.hume_config_id:
        print(f"\n🎉 SUCCESS! Agent synced with HumeAI!")
        print(f"   Local DB: ID {agent.id}")
        print(f"   HumeAI: Config {agent.hume_config_id}")
        
        # Test update
        print(f"\n🔄 Testing agent update...")
        agent.system_prompt = "Updated system prompt for testing."
        agent.save()
        
        print(f"✅ Agent updated (should sync to HumeAI)")
        
        return True
    else:
        print(f"\n❌ FAILED! Agent NOT synced with HumeAI")
        print(f"   Check:")
        print(f"   1. HUME_API_KEY in .env")
        print(f"   2. Internet connection")
        print(f"   3. HumeAI API status")
        return False

if __name__ == '__main__':
    test_agent_creation()
