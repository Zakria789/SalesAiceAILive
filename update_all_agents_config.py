"""
Update all references to new simplified config ID
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

def main():
    print("=" * 80)
    print("🔄 UPDATING ALL AGENTS WITH NEW CONFIG ID")
    print("=" * 80)
    
    new_config_id = "04d4ea50-ee37-4c18-aa89-fb20259d9596"
    
    print(f"\n📝 New Config ID: {new_config_id}")
    print(f"   (Simplified: Greeting + Direct Answers Only)")
    
    # Get all agents
    agents = HumeAgent.objects.all()
    updated_count = 0
    
    for agent in agents:
        old_config = agent.hume_config_id
        
        print(f"\n{'='*80}")
        print(f"Agent: {agent.name}")
        print(f"  Old Config: {old_config}")
        print(f"  New Config: {new_config_id}")
        
        # Update
        agent.hume_config_id = new_config_id
        agent.save()
        
        print(f"  ✅ Updated!")
        updated_count += 1
    
    print(f"\n{'='*80}")
    print(f"✅ UPDATED {updated_count} AGENT(S)")
    print(f"{'='*80}")
    
    print(f"\n💡 All agents now use simplified config:")
    print(f"   - Natural greeting")
    print(f"   - Direct sales script")
    print(f"   - Exact Q&A answers")
    
    print(f"\n🚀 Ready to test! No server restart needed!")

if __name__ == "__main__":
    main()
