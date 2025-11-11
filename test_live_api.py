"""
Test /api/agents/create/ with Direct Token
"""
import requests
import json
import os

BASE_URL = "http://localhost:8002"
API_ENDPOINT = f"{BASE_URL}/api/agents/create/"

# Direct JWT Token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYyMzQzMzI4LCJpYXQiOjE3NjIzMzk3MjgsImp0aSI6IjRjNGYwYWFlYTNjMTQ2NTRiMzEyNzNiODkzZTliZjQ4IiwidXNlcl9pZCI6IjIifQ.wWvElXfwE_IKN7SObhzFpuuUT09NTb-fz4D-9XV5Muo"

print("\n" + "="*80)
print("🧪 TESTING /api/agents/create/ API")
print("="*80)

# Payload
payload = {
    "name": f"Live API Test Agent {os.urandom(3).hex()}",  # Unique name
    "agent_type": "outbound",
    "status": "active",
    "voice_tone": "enthusiastic",
    "sales_script_text": """STEP 1: Introduction
Hello! This is calling from Coding The Brains. How are you today?

STEP 2: Value Proposition  
We specialize in AI and automation solutions that help businesses:
• Reduce manual work by 70%
• Improve customer response time
• Scale operations efficiently

STEP 3: Discovery
What's your biggest challenge with customer interactions?

STEP 4: Solution
Our AI chatbots and automation tools can help you by:
• Handling queries 24/7
• Automating repetitive tasks
• Providing detailed analytics

STEP 5: Call to Action
I'd love to show you a quick 15-minute demo. Are you available this week?""",
    "business_info": {
        "company_name": "Coding The Brains",
        "company_website": "https://www.codingthebrains.com/",
        "industry": "AI and Automation Services",
        "product_features": [
            "AI Chatbot Development",
            "Machine Learning Solutions",
            "Data Science & Analytics"
        ]
    },
    "operating_hours": {
        "start": "09:00",
        "end": "17:00",
        "timezone": "UTC",
        "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    },
    "auto_answer_enabled": False,
    "website_url": "https://www.codingthebrains.com/",
    "campaign_schedule": {
        "type": "immediate",
        "max_calls_per_day": 100
    }
}

print(f"\n📋 Payload:")
print(f"   Name: {payload['name']}")
print(f"   Sales Script: {len(payload['sales_script_text'])} chars")
print(f"   Business Info: {payload['business_info']['company_name']}")

# Make request
print(f"\n📤 POST {API_ENDPOINT}")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

try:
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    
    print(f"\n📥 Response:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ SUCCESS! Agent Created")
        print(json.dumps(data, indent=2))
        
        if 'agent' in data:
            agent = data['agent']
            print(f"\n📋 Agent Summary:")
            print(f"   ID: {agent.get('id')}")
            print(f"   Name: {agent.get('name')}")
            print(f"   HumeAI Synced: {'✅ YES' if data.get('hume_synced') else '❌ NO'}")
            print(f"   Config ID: {agent.get('hume_config_id', 'N/A')}")
            print(f"   Sales Script: {'✅ SAVED (' + str(len(agent.get('sales_script_text', ''))) + ' chars)' if agent.get('sales_script_text') else '❌ EMPTY'}")
            
    else:
        print(f"\n❌ Failed: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)
