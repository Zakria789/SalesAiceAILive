"""
Test the dashboard query to see if it works with agent assignment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from HumeAiTwilio.models import TwilioCall, HumeAgent
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=" * 80)
print("🧪 TESTING DASHBOARD QUERY WITH AGENT ASSIGNMENT")
print("=" * 80)

# Get the vonage@gmail.com user
user = User.objects.get(email='vonage@gmail.com')
print(f"\n✅ User: {user.email} (ID: {user.id})")

# Show user's agents
user_agents = HumeAgent.objects.filter(created_by=user)
print(f"\n📋 User's Agents: {user_agents.count()}")
for agent in user_agents:
    print(f"  - {agent.name} (ID: {agent.id})")

# Test the query (last 30 days)
end_date = timezone.now().date()
start_date = end_date - timedelta(days=30)

print(f"\n📅 Date Range: {start_date} to {end_date}")

# Query 1: Direct user calls
direct_calls = TwilioCall.objects.filter(
    user=user,
    started_at__date__gte=start_date,
    started_at__date__lte=end_date
)
print(f"\n📊 Query Results:")
print(f"  1️⃣ Direct user calls (user={user.email}): {direct_calls.count()}")

# Query 2: Agent calls
agent_calls = TwilioCall.objects.filter(
    agent__created_by=user,
    started_at__date__gte=start_date,
    started_at__date__lte=end_date
)
print(f"  2️⃣ Agent calls (agent.created_by={user.email}): {agent_calls.count()}")

# Query 3: Combined (Dashboard query)
combined_calls = TwilioCall.objects.filter(
    started_at__date__gte=start_date,
    started_at__date__lte=end_date
).filter(
    Q(user=user) | Q(agent__created_by=user)
)
print(f"  3️⃣ Combined (user OR agent.created_by): {combined_calls.count()}")

# Show sample calls
print(f"\n📞 Sample Combined Calls (first 10):")
for call in combined_calls[:10]:
    user_email = call.user.email if call.user else 'NULL'
    agent_name = call.agent.name if call.agent else 'NULL'
    agent_owner = call.agent.created_by.email if call.agent and call.agent.created_by else 'NULL'
    
    print(f"\n  Call ID: {str(call.id)[:8]}...")
    print(f"    Direction: {call.direction}")
    print(f"    Status: {call.status}")
    print(f"    User: {user_email}")
    print(f"    Agent: {agent_name}")
    print(f"    Agent Owner: {agent_owner}")
    print(f"    Started: {call.started_at}")

# Breakdown by direction
inbound = combined_calls.filter(direction='inbound').count()
outbound = combined_calls.filter(direction__in=['outbound', 'outbound_api']).count()

print(f"\n📊 Call Breakdown:")
print(f"  - Inbound: {inbound}")
print(f"  - Outbound: {outbound}")
print(f"  - Total: {combined_calls.count()}")

print("\n✅ Test completed!")
