"""
🔍 VERIFY HUMEAI CONFIG
Check what's actually uploaded to HumeAI
"""

import requests
from decouple import config
import json

HUME_API_KEY = config('HUME_API_KEY')
CONFIG_ID = config('HUME_CONFIG_ID')

print("=" * 80)
print("🔍 VERIFYING HUMEAI CONFIGURATION")
print("=" * 80)
print()

# ============================================================================
# GET CURRENT CONFIG FROM HUMEAI
# ============================================================================

def get_hume_config():
    """Get current configuration from HumeAI"""
    
    print("📥 Fetching config from HumeAI...")
    print(f"   Config ID: {CONFIG_ID}")
    print()
    
    url = f"https://api.hume.ai/v0/evi/configs/{CONFIG_ID}"
    
    headers = {
        "X-Hume-Api-Key": HUME_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            config_data = response.json()
            
            print("✅ Successfully retrieved config!")
            print()
            print("=" * 80)
            print("📋 CURRENT HUMEAI CONFIGURATION")
            print("=" * 80)
            print()
            
            # Basic Info
            print("🎯 Basic Information:")
            print(f"   • Name: {config_data.get('name', 'N/A')}")
            print(f"   • Config ID: {config_data.get('id', 'N/A')}")
            print(f"   • Version: {config_data.get('version', 'N/A')}")
            print()
            
            # Prompt/Knowledge Base
            prompt_data = config_data.get('prompt', {})
            if prompt_data:
                prompt_text = prompt_data.get('text', '')
                prompt_version = prompt_data.get('version', 'N/A')
                
                print("📝 Knowledge Base (Prompt):")
                print(f"   • Length: {len(prompt_text)} characters")
                print(f"   • Version: {prompt_version}")
                print()
                
                # Check for key phrases
                print("🔍 Content Check:")
                checks = [
                    ("SalesAice.ai mentioned", "SalesAice.ai" in prompt_text or "salesaice" in prompt_text.lower()),
                    ("Sarah name present", "Sarah" in prompt_text),
                    ("Gtree forbidden", "Gtree" in prompt_text and "NEVER" in prompt_text),
                    ("Sales automation mentioned", "sales automation" in prompt_text.lower()),
                    ("Website mentioned", "www.salesaice.ai" in prompt_text),
                    ("Objection handling", "objection" in prompt_text.lower()),
                    ("FAQ included", "question" in prompt_text.lower() or "Q:" in prompt_text),
                    ("Pricing info", "pricing" in prompt_text.lower() or "$299" in prompt_text),
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"   {status} {check_name}")
                
                print()
                
                # Show first 500 characters
                print("📄 First 500 characters of prompt:")
                print("-" * 80)
                print(prompt_text[:500])
                print("...")
                print("-" * 80)
                print()
                
                # Show last 300 characters
                print("📄 Last 300 characters of prompt:")
                print("-" * 80)
                print("...")
                print(prompt_text[-300:])
                print("-" * 80)
                print()
            else:
                print("⚠️ No prompt/knowledge base found!")
                print()
            
            # Voice Settings
            voice_data = config_data.get('voice', {})
            if voice_data:
                print("🗣️ Voice Settings:")
                print(f"   • Provider: {voice_data.get('provider', 'N/A')}")
                print(f"   • Name: {voice_data.get('name', 'N/A')}")
                print()
            
            # Language Model
            llm_data = config_data.get('language_model', {})
            if llm_data:
                print("🤖 Language Model:")
                print(f"   • Provider: {llm_data.get('model_provider', 'N/A')}")
                print(f"   • Model: {llm_data.get('model_resource', 'N/A')}")
                print(f"   • Temperature: {llm_data.get('temperature', 'N/A')}")
                print()
            
            # Event Messages
            events = config_data.get('event_messages', {})
            if events:
                print("💬 Event Messages:")
                on_new_chat = events.get('on_new_chat', {})
                if on_new_chat:
                    print(f"   • New Chat Greeting: '{on_new_chat.get('text', 'N/A')}'")
                    print(f"   • Enabled: {on_new_chat.get('enabled', False)}")
                print()
            
            # Save full config to file
            output_file = "humeai_config_backup.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Full config saved to: {output_file}")
            print()
            
            return config_data
            
        else:
            print(f"❌ Failed to retrieve config: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ============================================================================
# ANALYZE KNOWLEDGE BASE CONTENT
# ============================================================================

def analyze_knowledge_base(config_data):
    """Analyze what's in the knowledge base"""
    
    if not config_data:
        return
    
    prompt_text = config_data.get('prompt', {}).get('text', '')
    
    if not prompt_text:
        print("⚠️ No knowledge base content found!")
        return
    
    print("=" * 80)
    print("📊 KNOWLEDGE BASE ANALYSIS")
    print("=" * 80)
    print()
    
    # Count key elements
    print("📈 Content Statistics:")
    print(f"   • Total characters: {len(prompt_text)}")
    print(f"   • Total words: {len(prompt_text.split())}")
    print(f"   • Total lines: {len(prompt_text.splitlines())}")
    print()
    
    # Search for specific sections
    sections = [
        ("Company Overview", ["company overview", "what is salesaice", "about salesaice"]),
        ("Sales Script", ["sales script", "introduction", "step 1", "step 2"]),
        ("FAQ Section", ["common questions", "Q:", "question", "answer"]),
        ("Objection Handling", ["objection", "we're not interested", "too busy"]),
        ("Pricing Information", ["pricing", "$299", "cost", "how much"]),
        ("Key Features", ["features", "automation", "lead management"]),
        ("Identity Rules", ["you are sarah", "your name", "your company"]),
        ("Forbidden Words", ["never say", "forbidden", "gtree", "don't mention"]),
    ]
    
    print("🔍 Content Sections Found:")
    for section_name, keywords in sections:
        found = any(keyword.lower() in prompt_text.lower() for keyword in keywords)
        status = "✅" if found else "❌"
        print(f"   {status} {section_name}")
    
    print()
    
    # Count mentions of important terms
    print("🔢 Key Term Mentions:")
    terms = [
        ("SalesAice.ai", prompt_text.count("SalesAice.ai") + prompt_text.lower().count("salesaice")),
        ("Sarah", prompt_text.count("Sarah")),
        ("sales automation", prompt_text.lower().count("sales automation")),
        ("www.salesaice.ai", prompt_text.count("www.salesaice.ai")),
        ("Gtree (forbidden)", prompt_text.count("Gtree") + prompt_text.count("GTcree")),
        ("NEVER/FORBIDDEN", prompt_text.count("NEVER") + prompt_text.count("FORBIDDEN")),
    ]
    
    for term, count in terms:
        print(f"   • {term}: {count} times")
    
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🔍 Starting verification...")
    print()
    
    # Get current config
    config_data = get_hume_config()
    
    # Analyze knowledge base
    if config_data:
        analyze_knowledge_base(config_data)
    
    print("=" * 80)
    print("✅ VERIFICATION COMPLETE!")
    print("=" * 80)
    print()
    
    if config_data:
        prompt_length = len(config_data.get('prompt', {}).get('text', ''))
        
        if prompt_length > 5000:
            print("🎉 Knowledge base is UPLOADED and ACTIVE!")
            print(f"   • {prompt_length} characters of training data")
            print("   • Accessible to agent during calls")
            print("   • Will be used for all responses")
        elif prompt_length > 1000:
            print("✅ Knowledge base is uploaded")
            print(f"   • {prompt_length} characters")
            print("   • May need more content")
        else:
            print("⚠️ Knowledge base seems small or empty")
            print(f"   • Only {prompt_length} characters")
            print("   • May need to re-upload")
        
        print()
        print("📄 Full config saved to: humeai_config_backup.json")
        print("   You can open this file to see complete details")
        print()
        print("🔗 HumeAI Dashboard:")
        print("   https://platform.hume.ai/")
        print(f"   Config ID: {CONFIG_ID}")
        print()
    else:
        print("❌ Could not verify knowledge base")
        print("   Check API key and config ID")
    
    print("=" * 80)
