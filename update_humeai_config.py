"""
🔥 UPDATE HumeAI Config with Enhanced System Prompt
This will push the database content to HumeAI so agent uses it in real-time
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent
from HumeAiTwilio.hume_agent_service import HumeAgentService

def main():
    print("=" * 80)
    print("🔄 UPDATING HUMEAI CONFIG WITH ENHANCED PROMPT")
    print("=" * 80)
    
    try:
        # Get Test Agent
        agent = HumeAgent.objects.get(name="Test Agent")
        print(f"\n✅ Found agent: {agent.name}")
        print(f"   Config ID: {agent.hume_config_id}")
        
        # Build enhanced prompt
        service = HumeAgentService()
        
        # Get current config from HumeAI
        print(f"\n📥 Fetching current config from HumeAI...")
        current_config = service.get_agent(agent.hume_config_id)
        
        if not current_config:
            print(f"❌ Failed to fetch config from HumeAI!")
            return
        
        print(f"✅ Current config fetched")
        
        # Get current prompt
        current_prompt = current_config.get('prompt', {}).get('text', '')
        print(f"\n📊 Current prompt length: {len(current_prompt)} chars")
        
        # Build enhanced prompt from database
        base_prompt = current_prompt if current_prompt else "You are a helpful sales assistant. Be friendly and professional."
        
        # Use ONLY base prompt without enhancement to avoid duplication
        # The enhancement will be added fresh
        if len(current_prompt) > 1000:  # If already enhanced, use simple base
            base_prompt = "You are a helpful sales assistant for voice calls. Be friendly, professional, and conversational."
        
        enhanced_prompt = service._build_system_prompt(base_prompt, agent)
        
        print(f"📊 Enhanced prompt length: {len(enhanced_prompt)} chars")
        print(f"   Added content: +{len(enhanced_prompt) - len(base_prompt)} chars")
        
        # Show preview of what will be sent
        print(f"\n📄 PROMPT PREVIEW (first 500 chars):")
        print("-" * 80)
        print(enhanced_prompt[:500] + "...")
        print("-" * 80)
        
        # Confirm update
        print(f"\n⚠️  THIS WILL UPDATE HUMEAI CONFIG: {agent.hume_config_id}")
        print(f"   Agent: {agent.name}")
        print(f"   Current prompt: {len(current_prompt)} chars")
        print(f"   New prompt: {len(enhanced_prompt)} chars")
        
        confirm = input("\n🔄 Proceed with update? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("\n❌ Update cancelled")
            return
        
        # Update config in HumeAI
        print(f"\n🚀 Updating HumeAI config...")
        
        success = service.update_agent(
            config_id=agent.hume_config_id,
            name=agent.name,  # HumeAI requires name field
            system_prompt=enhanced_prompt
        )
        
        if success:
            print(f"\n✅ SUCCESS! HumeAI config updated!")
            print(f"\n📋 WHAT CHANGED:")
            print(f"   ✅ Added CONVERSATION STYLE instructions")
            print(f"   ✅ Added NATURAL GREETING instructions")
            print(f"   ✅ Added SALES SCRIPT with EXACT wording requirement")
            print(f"   ✅ Added BUSINESS INFORMATION")
            print(f"   ✅ Added KNOWLEDGE BASE with strict usage rules")
            print(f"\n🎯 NEXT STEPS:")
            print(f"   1. Make a new test call")
            print(f"   2. Agent should greet naturally: 'Hello! How are you today?'")
            print(f"   3. When you ask 'What does it do?', agent will use EXACT database content")
            print(f"\n💡 NO SERVER RESTART NEEDED - Changes are live in HumeAI!")
        else:
            print(f"\n❌ FAILED to update HumeAI config!")
            print(f"   Check API credentials and config ID")
            
    except HumeAgent.DoesNotExist:
        print("❌ Test Agent not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
