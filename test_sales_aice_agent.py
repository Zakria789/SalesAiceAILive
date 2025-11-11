"""
🎯 TEST SALES AICE AI AGENT (The Only One with HumeAI Config)
==============================================================
"""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import Agent
from HumeAiTwilio.hume_agent_service import hume_agent_service

print("\n" + "="*70)
print("🎯 TESTING SALES AICE AI AGENT")
print("="*70)

# Get the agent
agent = Agent.objects.get(name="Sales AICE AI Agent")

print(f"\n📋 Agent Details:")
print(f"   Name: {agent.name}")
print(f"   ID: {agent.id}")
print(f"   Type: {agent.agent_type}")
print(f"   Status: {agent.status}")
print(f"   Config ID: {agent.hume_config_id}")

print(f"\n📝 Sales Script ({len(agent.sales_script_text)} chars):")
print("-"*70)
print(agent.sales_script_text)
print("-"*70)

print(f"\n💼 Business Info:")
print("-"*70)
import json
print(json.dumps(agent.business_info, indent=2))
print("-"*70)

print(f"\n📚 Knowledge Base ({len(agent.knowledge_files)} items):")
print("-"*70)
if isinstance(agent.knowledge_files, dict):
    for key, value in agent.knowledge_files.items():
        print(f"   • {key}: {value[:100]}..." if len(str(value)) > 100 else f"   • {key}: {value}")
elif isinstance(agent.knowledge_files, list):
    for item in agent.knowledge_files:
        print(f"   • {str(item)[:100]}..." if len(str(item)) > 100 else f"   • {item}")
else:
    print(f"   {agent.knowledge_files}")
print("-"*70)

print(f"\n🔮 Generated System Prompt:")
print("="*70)
base_prompt = f"You are {agent.name}, a professional sales AI agent."
enhanced_prompt = hume_agent_service._build_system_prompt(base_prompt, agent)

print(enhanced_prompt)
print("="*70)

print(f"\n✅ This agent is READY for testing!")
print(f"   Config ID: {agent.hume_config_id}")
print(f"   To test: Use agent_id='{agent.id}' in call initiation")
print(f"\n🚀 TEST COMMAND:")
print(f"""
$headers = @{{'Content-Type'='application/json'; 'ngrok-skip-browser-warning'='true'}}
$body = @{{phone_no='+923403471112'; agent_id='{agent.id}'}} | ConvertTo-Json
Invoke-RestMethod -Uri 'https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/initiate-call/' -Method POST -Headers $headers -Body $body
""")

print("\n" + "="*70 + "\n")
