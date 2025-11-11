"""
Set new enhanced config as default for Test Agent
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent

def main():
    print("=" * 80)
    print("🔧 SETTING DEFAULT CONFIG ID")
    print("=" * 80)
    
    try:
        # Get Test Agent
        agent = HumeAgent.objects.get(name="Test Agent v2")
        
        print(f"\n✅ Found agent: {agent.name}")
        print(f"   Current Config ID: {agent.hume_config_id}")
        
        # New enhanced config ID
        new_config_id = "20d9ed94-1b05-44c8-8c05-7f87b36f0b20"
        
        print(f"\n🔄 Setting as default config...")
        print(f"   New Config ID: {new_config_id}")
        
        # Update agent
        agent.hume_config_id = new_config_id
        agent.save()
        
        print(f"\n✅ SUCCESS! Default config updated!")
        print(f"\n📋 Agent Details:")
        print(f"   Name: {agent.name}")
        print(f"   Config ID: {agent.hume_config_id}")
        print(f"   Voice: {agent.voice_name if hasattr(agent, 'voice_name') else 'ITO'}")
        
        print(f"\n💡 All future calls will use this enhanced config automatically!")
        
    except HumeAgent.DoesNotExist:
        print("\n⚠️ 'Test Agent v2' not found. Looking for 'Test Agent'...")
        
        try:
            agent = HumeAgent.objects.get(name="Test Agent")
            print(f"\n✅ Found: {agent.name}")
            print(f"   Current Config ID: {agent.hume_config_id}")
            
            # The script already updated it, just confirm
            if agent.hume_config_id == "20d9ed94-1b05-44c8-8c05-7f87b36f0b20":
                print(f"\n✅ Already using enhanced config!")
            else:
                print(f"\n🔄 Updating to enhanced config...")
                agent.hume_config_id = "20d9ed94-1b05-44c8-8c05-7f87b36f0b20"
                agent.save()
                print(f"\n✅ Updated successfully!")
                
        except HumeAgent.DoesNotExist:
            print("\n❌ No Test Agent found in database!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
