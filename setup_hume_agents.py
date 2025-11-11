#!/usr/bin/env python
"""
Check HumeAI agents in database
If no active agent exists, create default "Sarah" agent
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent
from decouple import config

print("=" * 80)
print("🤖 CHECKING HUMEAI AGENTS")
print("=" * 80)

# Get config ID from environment
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
print(f"\n📋 HumeAI Config ID from .env: {HUME_CONFIG_ID}")

# Check existing agents
all_agents = HumeAgent.objects.all()
active_agents = HumeAgent.objects.filter(status='active')

print(f"\n📊 Total agents: {all_agents.count()}")
print(f"✅ Active agents: {active_agents.count()}")

if all_agents.exists():
    print("\n📋 All agents:")
    for agent in all_agents:
        status_emoji = "✅" if agent.status == 'active' else "❌"
        print(f"  {status_emoji} {agent.name}")
        print(f"     Config ID: {agent.hume_config_id}")
        print(f"     Status: {agent.status}")
        print(f"     Voice: {agent.voice_name}")
        print(f"     Greeting: {agent.greeting_message}")
        print()
else:
    print("\n⚠️  NO AGENTS FOUND! Creating default 'Sarah' agent...")
    
    if not HUME_CONFIG_ID:
        print("❌ ERROR: HUME_CONFIG_ID not set in .env")
        print("Please add: HUME_CONFIG_ID=13624648-658a-49b1-81cb-a0f2e2b05de5")
        exit(1)
    
    # Create default agent
    sarah = HumeAgent.objects.create(
        name="Sarah",
        description="Default SalesAice.ai customer service agent",
        hume_config_id=HUME_CONFIG_ID,
        voice_name="ITO",
        language="en",
        system_prompt="You are Sarah, a friendly and professional customer service representative for SalesAice.ai. You are helpful, empathetic, and focused on providing excellent customer service. Be warm and engaging in your responses.",
        greeting_message="Hello! This is Sarah from SalesAice.ai. How can I help you today?",
        status='active'
    )
    
    print(f"✅ Created agent: {sarah.name}")
    print(f"   ID: {sarah.id}")
    print(f"   Config: {sarah.hume_config_id}")
    print(f"   Status: {sarah.status}")
    print(f"   Greeting: {sarah.greeting_message}")

print("\n✅ Setup complete!")
print("=" * 80)

# Verify active agent exists
active_agent = HumeAgent.objects.filter(status='active').first()
if active_agent:
    print(f"\n🎯 Next call will use: {active_agent.name}")
    print(f"   Config ID: {active_agent.hume_config_id}")
else:
    print(f"\n❌ ERROR: No active agent found!")
