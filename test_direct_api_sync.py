"""
Direct API Sync Test - ViewSet mein direct HumeAI call
No signals, no file creation - direct API integration!
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import HumeAgent

User = get_user_model()

def test_direct_api_sync():
    """Test that ViewSet directly calls HumeAI API"""
    print("\n" + "="*60)
    print("🚀 DIRECT API SYNC TEST")
    print("="*60)
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    print("\n1️⃣ Creating agent via Django ORM...")
    print("   ViewSet.perform_create() will call HumeAI API directly")
    
    # Note: This bypasses ViewSet, so no API call will happen
    # To test ViewSet, use REST API endpoint
    agent = HumeAgent.objects.create(
        name="Direct Test Agent",
        system_prompt="Testing direct API integration",
        voice_name="ITO",
        language="en",
        status="active",
        created_by=user
    )
    
    print(f"   ✅ Agent created: {agent.name} (ID: {agent.id})")
    
    # Since we're using ORM directly, we need to manually call the service
    # In production, use REST API which triggers perform_create()
    from HumeAiTwilio.hume_agent_service import hume_agent_service
    
    print("\n2️⃣ Manually calling HumeAI API (simulating ViewSet)...")
    
    try:
        config_id = hume_agent_service.create_agent(
            name=agent.name,
            system_prompt=agent.system_prompt,
            voice_name=agent.voice_name,
            language=agent.language
        )
        
        if config_id:
            agent.hume_config_id = config_id
            agent.save(update_fields=['hume_config_id'])
            print(f"   ✅ HumeAI Config ID: {config_id}")
            print(f"   ✅ Saved to local database")
        else:
            print("   ❌ Failed to get config_id from HumeAI")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n3️⃣ Verification...")
    agent.refresh_from_db()
    
    if agent.hume_config_id:
        print(f"   ✅ SUCCESS! Config ID: {agent.hume_config_id}")
        print(f"   ✅ Agent is synced with HumeAI")
    else:
        print("   ❌ FAILED - No config_id found")
        print("   💡 Check HUME_API_KEY in .env")
    
    print("\n" + "="*60)
    print("💡 IMPORTANT:")
    print("   - Direct ORM creation won't trigger ViewSet methods")
    print("   - Use REST API endpoints to test full flow:")
    print("     POST /api/hume-twilio/agents/")
    print("   - ViewSet.perform_create() calls HumeAI directly")
    print("   - No signals = No duplicate calls!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_direct_api_sync()
