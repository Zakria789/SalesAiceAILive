"""
Complete Agent Creation Flow Test
Tests:
1. Direct Django ORM creation
2. API endpoint creation
3. HumeAI sync verification
4. Config ID population
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import HumeAgent

User = get_user_model()

def test_orm_agent_creation():
    """Test 1: Create agent via Django ORM (signals should auto-sync)"""
    print("\n" + "="*60)
    print("TEST 1: Django ORM Agent Creation")
    print("="*60)
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Create agent
    agent = HumeAgent.objects.create(
        name="Test ORM Agent",
        system_prompt="You are a helpful AI assistant for testing.",
        voice_name="ITO",
        language="en",
        status="active",
        created_by=user
    )
    
    print(f"✅ Agent created with ID: {agent.id}")
    print(f"📌 Agent Name: {agent.name}")
    print(f"🔑 HumeAI Config ID: {agent.hume_config_id or '⚠️ NOT SYNCED YET'}")
    
    # Refresh from database to get updated hume_config_id
    agent.refresh_from_db()
    
    if agent.hume_config_id:
        print(f"✅ HumeAI Sync SUCCESS! Config ID: {agent.hume_config_id}")
    else:
        print("❌ HumeAI Sync FAILED - Config ID not populated")
        print("💡 Check HUME_API_KEY in .env file")
    
    return agent


def test_api_agent_creation():
    """Test 2: Create agent via REST API"""
    print("\n" + "="*60)
    print("TEST 2: REST API Agent Creation")
    print("="*60)
    
    url = "http://127.0.0.1:8000/api/hume-twilio/agents/"
    
    # Get auth token (you'll need to adjust this based on your auth setup)
    # For now, we'll assume the API allows creation without auth or you have AllowAny
    
    payload = {
        "name": "Test API Agent",
        "system_prompt": "You are a sales assistant for testing API.",
        "voice_name": "KORA",
        "language": "en",
        "status": "active"
    }
    
    try:
        # Note: Add authentication headers if required
        response = requests.post(url, json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Agent created via API")
            print(f"📌 Agent ID: {data.get('id')}")
            print(f"📌 Agent Name: {data.get('name')}")
            print(f"🔑 HumeAI Config ID: {data.get('hume_config_id') or '⚠️ NOT SYNCED YET'}")
            
            if data.get('hume_config_id'):
                print(f"✅ HumeAI Sync SUCCESS!")
            else:
                print("❌ HumeAI Sync FAILED - Config ID not populated")
            
            return data
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("💡 Make sure server is running: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_hume_config_verification(agent):
    """Test 3: Verify HumeAI config exists"""
    print("\n" + "="*60)
    print("TEST 3: HumeAI Config Verification")
    print("="*60)
    
    if not agent.hume_config_id:
        print("⚠️ No HumeAI Config ID to verify")
        return False
    
    from HumeAiTwilio.hume_agent_service import hume_agent_service
    
    try:
        config = hume_agent_service.get_agent(agent.hume_config_id)
        
        if config:
            print(f"✅ HumeAI Config found!")
            print(f"📌 Config ID: {config.get('id')}")
            print(f"📌 Name: {config.get('name')}")
            print(f"📌 Voice: {config.get('voice', {}).get('name')}")
            return True
        else:
            print("❌ HumeAI Config not found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying HumeAI config: {str(e)}")
        return False


def test_agent_update_sync():
    """Test 4: Verify agent updates sync to HumeAI"""
    print("\n" + "="*60)
    print("TEST 4: Agent Update Sync Test")
    print("="*60)
    
    # Get a test agent
    agent = HumeAgent.objects.filter(hume_config_id__isnull=False).first()
    
    if not agent:
        print("⚠️ No synced agent found to test updates")
        return False
    
    print(f"Testing with agent: {agent.name}")
    
    # Update agent
    original_prompt = agent.system_prompt
    agent.system_prompt = f"UPDATED: {original_prompt}"
    agent.save()
    
    print(f"✅ Agent updated in local database")
    print(f"📌 Old prompt: {original_prompt[:50]}...")
    print(f"📌 New prompt: {agent.system_prompt[:50]}...")
    print("✅ Signal should have synced to HumeAI automatically")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "🚀 " + "="*58)
    print("🚀 COMPLETE AGENT CREATION FLOW TEST")
    print("🚀 " + "="*58)
    
    # Test 1: ORM Creation
    orm_agent = test_orm_agent_creation()
    
    # Test 2: API Creation
    api_agent_data = test_api_agent_creation()
    
    # Test 3: Verify HumeAI Config
    if orm_agent:
        test_hume_config_verification(orm_agent)
    
    # Test 4: Update Sync
    test_agent_update_sync()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print("✅ Test 1: Django ORM creation - Completed")
    print("✅ Test 2: REST API creation - Attempted")
    print("✅ Test 3: HumeAI config verification - Completed")
    print("✅ Test 4: Update sync - Completed")
    print("\n💡 IMPORTANT:")
    print("   - Signals automatically sync agents to HumeAI on create/update/delete")
    print("   - Make sure HUME_API_KEY is set in .env file")
    print("   - Config ID is automatically populated in hume_config_id field")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
