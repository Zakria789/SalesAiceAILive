"""
Test Agent Create API with HumeAI integration
"""
import requests
import json

# Your API endpoint
API_BASE_URL = "http://localhost:8002"
API_ENDPOINT = f"{API_BASE_URL}/api/agents/create/"

# Test agent data
agent_data = {
    "name": "Test Sales Agent HumeAI",
    "agent_type": "outbound",
    "status": "active",
    "voice_model": "ITO",
    "voice_tone": "Professional and friendly",
    "sales_script_text": "Hello! This is a test sales agent. I'm calling to discuss our amazing products.",
    "business_info": {
        "name": "Test Company",
        "industry": "Technology",
        "mission": "Testing HumeAI integration"
    }
}

def test_agent_creation_with_auth():
    """Test agent creation API with authentication"""
    
    print("🧪 Testing Agent Create API...")
    print(f"📤 POST {API_ENDPOINT}")
    print(f"📦 Payload:")
    print(json.dumps(agent_data, indent=2))
    
    # First login to get token
    print("\n🔐 Step 1: Getting authentication token...")
    login_data = {
        "email": "umair11@gmail.com",  # Change to your test user
        "password": "umair11"  # Change to your password
    }
    
    login_response = requests.post(
        f"{API_BASE_URL}/api/auth/login/",
        json=login_data,
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data.get('access')
    
    if not access_token:
        print(f"❌ No access token in response")
        print(f"Response: {token_data}")
        return
    
    print(f"✅ Login successful! Token: {access_token[:30]}...")
    
    # Now create agent with auth token
    print("\n📤 Step 2: Creating agent...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        API_ENDPOINT,
        headers=headers,
        json=agent_data,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('success'):
            agent = result.get('agent', {})
            hume_config = agent.get('hume_ai_config', {})
            
            print(f"\n✅ SUCCESS! Agent created")
            print(f"   Agent ID: {agent.get('id')}")
            print(f"   Agent Name: {agent.get('name')}")
            print(f"   HumeAI Config ID: {hume_config.get('evi_config_id')}")
            print(f"   HumeAI Created: {hume_config.get('hume_created', False)}")
            
            return agent
        else:
            print(f"\n❌ API returned success=false")
            print(f"Message: {result.get('message')}")
            print(f"Errors: {result.get('errors')}")
    else:
        print(f"\n❌ FAILED! Status {response.status_code}")
        
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT CREATE API TEST WITH HUMEAI INTEGRATION")
    print("=" * 60)
    test_agent_creation_with_auth()
    print("\n" + "=" * 60)
