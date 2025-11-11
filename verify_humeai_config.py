"""
Verify if HumeAI config was actually updated with enhanced prompt
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.models import HumeAgent
from HumeAiTwilio.hume_agent_service import HumeAgentService

def main():
    print("=" * 80)
    print("🔍 VERIFYING HUMEAI CONFIG UPDATE")
    print("=" * 80)
    
    try:
        # Get Test Agent
        agent = HumeAgent.objects.get(name="Test Agent")
        print(f"\n✅ Found agent: {agent.name}")
        print(f"   Config ID: {agent.hume_config_id}")
        
        # Fetch current config from HumeAI
        service = HumeAgentService()
        print(f"\n📥 Fetching config from HumeAI API...")
        
        config = service.get_agent(agent.hume_config_id)
        
        if not config:
            print(f"❌ Failed to fetch config from HumeAI!")
            return
        
        print(f"✅ Config fetched successfully!")
        
        # Extract prompt
        prompt = config.get('prompt', {})
        prompt_text = prompt.get('text', '')
        
        print(f"\n📊 CURRENT HUMEAI CONFIG:")
        print(f"   Config ID: {config.get('id', 'N/A')}")
        print(f"   Name: {config.get('name', 'N/A')}")
        print(f"   Prompt Length: {len(prompt_text)} characters")
        
        # Check if enhanced
        checks = {
            "CONVERSATION STYLE": "CONVERSATION STYLE" in prompt_text,
            "Natural greeting": "Hello! How are you today?" in prompt_text or "asking 'How are you?'" in prompt_text,
            "SALES SCRIPT section": "SALES SCRIPT" in prompt_text,
            "EXACT wording instruction": "EXACT" in prompt_text and "word-for-word" in prompt_text,
            "SalesAice.ai mention": "SalesAice.ai" in prompt_text,
            "START SALES SCRIPT marker": "--- START SALES SCRIPT ---" in prompt_text,
            "END SALES SCRIPT marker": "--- END SALES SCRIPT ---" in prompt_text,
            "KNOWLEDGE BASE": "KNOWLEDGE BASE" in prompt_text,
            "DO NOT make up": "DO NOT make up" in prompt_text,
            "FAQ section": "What exactly does your software do?" in prompt_text
        }
        
        print(f"\n✅ VERIFICATION CHECKS:")
        all_passed = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
            if not result:
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 ALL CHECKS PASSED! Config is updated correctly!")
            print(f"\n💡 Enhanced prompt is LIVE in HumeAI")
        else:
            print(f"\n⚠️  SOME CHECKS FAILED - Config may not be fully updated")
        
        # Show first 800 chars
        if len(prompt_text) > 0:
            print(f"\n📄 PROMPT PREVIEW (first 800 chars):")
            print("-" * 80)
            print(prompt_text[:800])
            if len(prompt_text) > 800:
                print("...")
            print("-" * 80)
        else:
            print(f"\n⚠️  WARNING: Prompt is EMPTY!")
        
        # Voice settings
        voice = config.get('voice', {})
        print(f"\n🎤 VOICE SETTINGS:")
        print(f"   Provider: {voice.get('provider', 'N/A')}")
        print(f"   Name: {voice.get('name', 'N/A')}")
        
        # Language
        language = config.get('language', {})
        print(f"\n🌍 LANGUAGE:")
        print(f"   Code: {language.get('code', 'N/A')}")
        
        print(f"\n✅ Verification complete!")
        
    except HumeAgent.DoesNotExist:
        print("❌ Test Agent not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
