#!/usr/bin/env python
"""Comprehensive system check before call testing"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from HumeAiTwilio.models import HumeAgent, TwilioCall
from decouple import config
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 80)
print("🔍 COMPLETE SYSTEM HEALTH CHECK")
print("=" * 80)

# 1. Environment Variables
print("\n[1] ✅ ENVIRONMENT CONFIGURATION:")
HUME_API_KEY = config('HUME_API_KEY', default='')
HUME_CONFIG_ID = config('HUME_CONFIG_ID', default='')
VONAGE_API_KEY = config('VONAGE_API_KEY', default='')
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default='')
VONAGE_APPLICATION_ID = config('VONAGE_APPLICATION_ID', default='')
BASE_URL = config('BASE_URL', default='')

print(f"   HUME_API_KEY: {'✅' if HUME_API_KEY else '❌'}")
print(f"   HUME_CONFIG_ID: {'✅' if HUME_CONFIG_ID else '❌'} → {HUME_CONFIG_ID if HUME_CONFIG_ID else 'NOT SET'}")
print(f"   VONAGE_API_KEY: {'✅' if VONAGE_API_KEY else '❌'}")
print(f"   VONAGE_APPLICATION_ID: {'✅' if VONAGE_APPLICATION_ID else '❌'}")
print(f"   BASE_URL (ngrok): {'✅' if BASE_URL else '❌'} → {BASE_URL if BASE_URL else 'NOT SET'}")

# 2. Database Agents
print("\n[2] 📊 DATABASE AGENTS:")
active_agents = HumeAgent.objects.filter(status='active')
print(f"   Total active agents: {active_agents.count()}")

default_agent = active_agents.order_by('created_at').first()
if default_agent:
    print(f"   ✅ Default Agent: {default_agent.name}")
    print(f"      Config ID: {default_agent.hume_config_id}")
    print(f"      Voice: {default_agent.voice_name}")
    print(f"      Status: {default_agent.status}")
else:
    print(f"   ❌ No active agents found!")

# 3. Recent Calls Analysis
print("\n[3] 📞 RECENT CALLS (Last 10):")
recent_calls = TwilioCall.objects.filter(
    provider='vonage'
).order_by('-created_at')[:10]

if recent_calls.exists():
    print(f"   Total calls: {recent_calls.count()}")
    
    # Statistics
    total_duration = sum([c.duration for c in recent_calls if c.duration])
    avg_duration = total_duration / len([c for c in recent_calls if c.duration]) if any(c.duration for c in recent_calls) else 0
    
    print(f"   Average duration: {avg_duration:.1f} seconds")
    
    # Show last 3 calls
    print(f"\n   Last 3 calls:")
    for call in recent_calls[:3]:
        print(f"      • {call.call_sid[:8]}... | Status: {call.status} | Duration: {call.duration}s | Agent: {call.agent.name if call.agent else 'None'}")
else:
    print(f"   No recent calls found")

# 4. System Readiness
print("\n[4] 🎯 SYSTEM READINESS:")

issues = []
warnings = []

if not HUME_API_KEY:
    issues.append("HUME_API_KEY not set")
if not HUME_CONFIG_ID:
    issues.append("HUME_CONFIG_ID not set")
if not VONAGE_API_KEY:
    issues.append("VONAGE_API_KEY not set")
if not default_agent:
    issues.append("No active HumeAgent in database")
if default_agent and default_agent.hume_config_id != HUME_CONFIG_ID:
    warnings.append(f"Agent config ({default_agent.hume_config_id}) differs from .env ({HUME_CONFIG_ID})")

if issues:
    print(f"   ❌ BLOCKING ISSUES:")
    for issue in issues:
        print(f"      - {issue}")
else:
    print(f"   ✅ No blocking issues")

if warnings:
    print(f"   ⚠️  WARNINGS:")
    for warning in warnings:
        print(f"      - {warning}")

# 5. Final Verdict
print("\n" + "=" * 80)
if not issues:
    print("✅ SYSTEM READY FOR TESTING!")
    print("=" * 80)
    print(f"\n📋 CURRENT CONFIGURATION:")
    print(f"   Agent: {default_agent.name}")
    print(f"   HumeAI Config: {default_agent.hume_config_id}")
    print(f"   Voice Model: {default_agent.voice_name}")
    print(f"   Provider: Vonage")
    print(f"   WebSocket: wss://api.hume.ai/v0/assistant/chat")
    
    print(f"\n🎤 EXPECTED BEHAVIOR:")
    print(f"   1. Call initiates via Vonage")
    print(f"   2. Vonage connects to HumeAI WebSocket")
    print(f"   3. HumeAI agent speaks (if config is trained)")
    print(f"   4. Call duration > 5 seconds")
    print(f"   5. No 'invalid stream url' errors")
    
    print(f"\n⚠️  IF AGENT IS SILENT:")
    print(f"   • Check HumeAI dashboard (platform.hume.ai)")
    print(f"   • Verify config '{default_agent.hume_config_id}' is:")
    print(f"      - Published (not draft)")
    print(f"      - Has voice model assigned")
    print(f"      - Has system prompt configured")
    print(f"      - Status is 'Active'")
    
    print(f"\n🚀 READY TO TEST CALL!")
else:
    print("❌ SYSTEM NOT READY - Fix issues above")
    print("=" * 80)

print()
