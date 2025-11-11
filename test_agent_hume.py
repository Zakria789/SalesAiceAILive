import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import Agent
from agents.serializers import AgentCreateUpdateSerializer  
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

print(f"Testing agent creation for user: {user.email}")
print("=" * 60)

test_data = {
    'name': 'Test Agent V3 - HumeAI',
    'agent_type': 'outbound',
    'status': 'active',
    'voice_model': 'ITO',
    'voice_tone': 'Professional and friendly',
    'sales_script_text': 'Hello! This is a test agent for HumeAI integration.'
}

serializer = AgentCreateUpdateSerializer(
    data=test_data,
    context={'request': type('obj', (object,), {'user': user})}
)

if serializer.is_valid():
    print("✅ Validation passed")
    print("\n🚀 Creating agent...")
    print("=" * 60)
    
    agent = serializer.save()
    
    print(f"\n✅ AGENT CREATED SUCCESSFULLY!")
    print(f"   Agent ID: {agent.id}")
    print(f"   Agent Name: {agent.name}")
    print(f"\n📱 HumeAI Configuration:")
    print(f"   Config ID: {agent.hume_ai_config.get('evi_config_id')}")
    print(f"   HumeAI Created: {agent.hume_ai_config.get('hume_created', False)}")
    print(f"   Created At: {agent.hume_ai_config.get('created_at', 'N/A')}")
    
    if agent.hume_ai_config.get('hume_created'):
        print(f"\n🎉 SUCCESS! New config created on HumeAI platform!")
    else:
        print(f"\n⚠️  Using default config (HumeAI creation may have failed)")
else:
    print("❌ Validation failed:")
    print(serializer.errors)
