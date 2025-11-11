"""
Try updating HumeAI config using POST (create new version)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent
from HumeAiTwilio.hume_agent_service import HumeAgentService
import requests
import json

def main():
    print("=" * 80)
    print("🔄 UPDATING HUMEAI CONFIG (POST METHOD)")
    print("=" * 80)
    
    try:
        # Get Test Agent
        agent = HumeAgent.objects.get(name="Test Agent")
        print(f"\n✅ Agent: {agent.name}")
        print(f"   Config ID: {agent.hume_config_id}")
        
        # Build enhanced prompt
        service = HumeAgentService()
        base_prompt = "You are a helpful sales assistant. Be friendly and professional."
        enhanced_prompt = service._build_system_prompt(base_prompt, agent)
        
        print(f"\n📊 Enhanced prompt: {len(enhanced_prompt)} chars")
        
        # Get API credentials
        from django.conf import settings
        api_key = settings.HUME_AI_API_KEY
        
        # Try POST method to create new version
        url = f"https://api.hume.ai/v0/evi/configs"
        headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": f"{agent.name} Simplified",  # New name for simplified version
            "version_description": "Simplified: Greeting + Direct Answers Only",
            "prompt": {
                "text": enhanced_prompt
            },
            "voice": {
                "provider": "HUME_AI",
                "name": agent.voice_name if hasattr(agent, 'voice_name') and agent.voice_name else "ITO"
            },
            "language": {
                "code": "en"
            },
            "evi_version": "3"
        }
        
        print(f"\n📡 Making POST request to create new version...")
        print(f"   URL: {url}")
        print(f"   Payload keys: {list(payload.keys())}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(json.dumps(data, indent=2)[:1000])
            
            new_config_id = data.get('id') or data.get('config_id')
            new_version = data.get('version')
            
            if new_config_id:
                print(f"\n📝 New Config ID: {new_config_id}")
                print(f"   Version: {new_version}")
                
                if new_config_id != agent.hume_config_id:
                    print(f"\n⚠️  Config ID changed! Update database:")
                    print(f"   Old: {agent.hume_config_id}")
                    print(f"   New: {new_config_id}")
                    
                    # Update agent with new config ID
                    agent.hume_config_id = new_config_id
                    agent.save()
                    print(f"   ✅ Database updated with new config ID")
        else:
            print(f"\n❌ FAILED!")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
