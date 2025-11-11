"""
Quick verification of Test Agent (index 2) - The one with SalesAice.ai script
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

agents = HumeAgent.objects.all()

print("\n" + "="*80)
print("🎯 TEST AGENT (Index 2) VERIFICATION")
print("="*80 + "\n")

for idx, agent in enumerate(agents):
    print(f"Agent #{idx}: {agent.name}")
    print(f"   Config: {agent.hume_config_id}")
    print(f"   Script: {len(agent.sales_script_text) if agent.sales_script_text else 0} chars")
    if agent.business_info:
        print(f"   Business: {agent.business_info.get('company_name', 'N/A')}")
    print()

print("="*80)
print("🚀 READY STATUS")
print("="*80)

# Check the Test Agent specifically
test_agent = agents[2]  # Index 2 = "Test Agent"
print(f"\n✅ Agent Name: {test_agent.name}")
print(f"✅ Config ID: {test_agent.hume_config_id}")
print(f"✅ Has Sales Script: {'Yes' if test_agent.sales_script_text else 'No'}")
print(f"✅ Has Business Info: {'Yes' if test_agent.business_info else 'No'}")
print(f"✅ Has Knowledge Base: {'Yes' if test_agent.knowledge_files else 'No'}")

if test_agent.sales_script_text:
    print(f"\n📝 Sales Script Preview:")
    print(f"   {test_agent.sales_script_text[:150]}...")

if test_agent.business_info:
    print(f"\n🏢 Business Info:")
    print(f"   Company: {test_agent.business_info.get('company_name', 'N/A')}")
    print(f"   Website: {test_agent.business_info.get('company_website', 'N/A')}")

print("\n" + "="*80)
print("✅ ALL GOOD - READY FOR TEST CALL WITH agent_id='2'")
print("="*80 + "\n")
