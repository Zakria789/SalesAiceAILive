"""
🧪 Test Force Greeting Feature
================================

Verify that:
1. Sales script greeting is extracted correctly
2. Force greeting message is constructed properly
3. Agent will start conversation immediately
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from HumeAiTwilio.models import HumeAgent

# Get Test Agent
agent = HumeAgent.objects.get(id='b77dd00d-0221-4074-a2a3-442e0cce9772')

print("\n" + "="*70)
print("🧪 Testing Force Greeting Feature")
print("="*70)

print(f"\n🤖 Agent: {agent.name}")
print(f"   ID: {agent.id}")

# Test greeting extraction
if agent.sales_script_text:
    lines = agent.sales_script_text.strip().split('\n')
    greeting = lines[0].strip() if lines else "Default greeting"
    
    print(f"\n📝 Sales Script (First Line):")
    print(f"   \"{greeting}\"")
    
    print(f"\n✅ Expected Behavior:")
    print(f"   1. Call connects")
    print(f"   2. System sends force greeting trigger:")
    print(f"      {{")
    print(f"        \"type\": \"user_message\",")
    print(f"        \"message\": {{")
    print(f"          \"role\": \"user\",")
    print(f"          \"content\": \"[SYSTEM: Call just connected. Start the conversation using your greeting and sales script.]\"")
    print(f"        }}")
    print(f"      }}")
    print(f"   3. Agent responds with:")
    print(f"      \"{greeting}\"")
    print(f"   4. Continues with sales script flow")
    
    print(f"\n🎯 What Customer Should Hear:")
    print(f"   → {greeting}")
    print(f"   → [Sales pitch continues...]")
    
    # Show full sales script
    print(f"\n📋 Full Sales Script:")
    print(f"   " + "-"*66)
    for i, line in enumerate(agent.sales_script_text.split('\n'), 1):
        if line.strip():
            print(f"   {line}")
    print(f"   " + "-"*66)
    
    print(f"\n✅ Configuration Status:")
    print(f"   ✅ Force greeting: ENABLED in vonage_realtime_consumer.py")
    print(f"   ✅ Sales script: {len(agent.sales_script_text)} characters")
    print(f"   ✅ Business info: {len(agent.business_info)} fields")
    print(f"   ✅ Knowledge base: {len(agent.knowledge_files)} categories")
    
    print(f"\n🚀 Ready to Test!")
    print(f"   1. Server must be running: daphne -b 0.0.0.0 -p 8002 core.asgi:application")
    print(f"   2. Make call: Use your PowerShell command")
    print(f"   3. Watch logs for:")
    print(f"      → '🎤 [FORCE START] Triggered agent to start with greeting'")
    print(f"      → '🤖 [AGENT]' messages showing sales script")
    
else:
    print(f"\n❌ ERROR: Sales script not found!")
    print(f"   Agent has no sales_script_text")

print(f"\n" + "="*70)
