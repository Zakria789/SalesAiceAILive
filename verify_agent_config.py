"""
Verify that all agents have the correct simplified config ID
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

print("\n" + "="*80)
print("🔍 AGENT CONFIG VERIFICATION")
print("="*80 + "\n")

expected_config = "04d4ea50-ee37-4c18-aa89-fb20259d9596"

agents = HumeAgent.objects.all()
print(f"📊 Total Agents: {agents.count()}\n")

for idx, agent in enumerate(agents):
    print(f"Agent #{idx}: {agent.name}")
    print(f"   ID: {agent.id}")
    print(f"   Config ID: {agent.hume_config_id}")
    
    if agent.hume_config_id == expected_config:
        print(f"   ✅ CORRECT - Using simplified config\n")
    else:
        print(f"   ❌ WRONG - Should be {expected_config}\n")

print("="*80)
print("🎯 Expected Config: 04d4ea50-ee37-4c18-aa89-fb20259d9596")
print("   (Simplified: Greeting + Direct Answers Only)")
print("="*80 + "\n")
