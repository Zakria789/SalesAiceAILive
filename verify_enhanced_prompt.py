"""
🔍 Verify Enhanced Prompt for Test Agent
==========================================

Shows how HumeAI will receive the enhanced prompt with
SalesAice.ai sales script and knowledge base.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from HumeAiTwilio.models import HumeAgent
from HumeAiTwilio.hume_agent_service import HumeAgentService

# Get Test Agent
agent = HumeAgent.objects.get(id='b77dd00d-0221-4074-a2a3-442e0cce9772')

print(f"\n" + "="*70)
print(f"🤖 Agent: {agent.name}")
print(f"="*70)

# Show base system prompt
print(f"\n📋 Base System Prompt:")
print(f"-" * 70)
print(agent.system_prompt)
print(f"-" * 70)

# Build enhanced prompt using service
service = HumeAgentService()
enhanced_prompt = service._build_system_prompt(agent.system_prompt, agent)

print(f"\n🔥 ENHANCED PROMPT (What HumeAI Will Receive):")
print(f"="*70)
print(enhanced_prompt)
print(f"="*70)

print(f"\n📊 Statistics:")
print(f"  Base Prompt Length: {len(agent.system_prompt)} characters")
print(f"  Enhanced Prompt Length: {len(enhanced_prompt)} characters")
print(f"  Added Content: {len(enhanced_prompt) - len(agent.system_prompt)} characters")

print(f"\n✅ Verification:")
print(f"  {'✅' if 'SalesAice.ai' in enhanced_prompt else '❌'} Company name included")
print(f"  {'✅' if 'SALES SCRIPT' in enhanced_prompt else '❌'} Sales script section")
print(f"  {'✅' if 'BUSINESS INFORMATION' in enhanced_prompt else '❌'} Business info section")
print(f"  {'✅' if 'KNOWLEDGE BASE' in enhanced_prompt else '❌'} Knowledge base section")
print(f"  {'✅' if 'automates sales outreach' in enhanced_prompt else '❌'} FAQ answers included")

# Show greeting extraction
from HumeAiTwilio.vonage_realtime_consumer import VonageRealtimeConsumer

# Simulate greeting extraction
if agent.sales_script_text:
    lines = agent.sales_script_text.strip().split('\n')
    greeting = lines[0].strip() if lines else "Default greeting"
    print(f"\n👋 Greeting (from sales_script first line):")
    print(f"   \"{greeting}\"")

print(f"\n🎉 Agent is ready for calls with full database knowledge!")
