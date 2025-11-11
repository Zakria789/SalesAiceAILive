"""
Test HumeAI config creation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import requests

def test_hume_config_creation():
    """Test creating a HumeAI config"""
    
    api_key = settings.HUME_AI_API_KEY
    base_url = "https://api.hume.ai/v0"
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test config data
    config_data = {
        "evi_version": "3",
        "name": "Test Voice Agent - Demo",
        "voice": {
            "provider": "HUME_AI",
            "name": "ITO",
        },
        "language_model": {
            "model_provider": "ANTHROPIC",
            "model_resource": "claude-3-5-sonnet-20241022"
        },
        "system_prompt": "You are a helpful AI assistant for sales calls.",
        "tools": []
    }
    
    print("🧪 Testing HumeAI config creation...")
    print(f"📤 POST {base_url}/evi/configs")
    print(f"📦 Payload: {config_data}")
    
    response = requests.post(
        f"{base_url}/evi/configs",
        headers=headers,
        json=config_data,
        timeout=15
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    print(response.text)
    
    if response.status_code in [200, 201]:
        result = response.json()
        config_id = result.get('id')
        print(f"\n✅ SUCCESS! Config created: {config_id}")
        return config_id
    else:
        print(f"\n❌ FAILED! Status {response.status_code}")
        return None

if __name__ == "__main__":
    test_hume_config_creation()
