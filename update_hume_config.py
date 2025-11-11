"""
Update HumeAgent to use correct config ID: 13624648-658a-49b1-81cb-a0f2e2b05de5
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

print("=" * 80)
print("UPDATING HUME AGENT CONFIG")
print("=" * 80)

# Get active agent
agents = HumeAgent.objects.filter(status='active')

print(f"\nFound {agents.count()} active agent(s)")

for agent in agents:
    print(f"\nAgent: {agent.name}")
    print(f"  Old Config: {agent.hume_config_id}")
    
    # Update to correct config
    agent.hume_config_id = "13624648-658a-49b1-81cb-a0f2e2b05de5"
    agent.voice_name = "ITO"  # Update voice model
    agent.save()
    
    print(f"  New Config: {agent.hume_config_id}")
    print(f"  Voice: {agent.voice_name}")
    print("  ✅ Updated!")

print("\n" + "=" * 80)
print("UPDATE COMPLETE")
print("=" * 80)
print("\nNew Config ID: 13624648-658a-49b1-81cb-a0f2e2b05de5")
print("Voice Model: ITO")
print("=" * 80)
