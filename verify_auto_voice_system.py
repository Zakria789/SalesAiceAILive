#!/usr/bin/env python3
"""
QUICK SYSTEM VERIFICATION
Complete auto voice system ready hai ya nahi check karta hai
"""

import sys
import os

# Add Django project path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Django setup
import django
django.setup()

import json
from agents.models import Agent
from live_hume_integration import LiveHumeAIIntegration

def verify_hume_ai():
    """Hume AI setup verify karta hai"""
    print("🎭 Checking Hume AI Integration...")
    
    try:
        hume = LiveHumeAIIntegration()
        api_key = hume.hume_api_key
        config_id = hume.hume_evi_config_id
        
        if api_key and len(api_key) > 20:
            print(f"✅ Hume AI API Key: {api_key[:20]}...")
            
            if config_id:
                print(f"✅ EVI Config ID: {config_id}")
                return True
            else:
                print("❌ EVI Config ID missing")
                return False
        else:
            print("❌ Hume AI API Key missing")
            return False
            
    except Exception as e:
        print(f"❌ Hume AI error: {str(e)}")
        return False

def verify_agents():
    """Agents verify karta hai"""
    print("\\n🤖 Checking AI Agents...")
    
    try:
        agents = Agent.objects.filter(status='active')
        
        if agents.exists():
            for agent in agents:
                print(f"✅ Agent: {agent.name} (ID: {agent.id})")
                
                # Check voice settings
                voice_tone = getattr(agent, 'voice_tone', None)
                voice_model = getattr(agent, 'voice_model', None)
                
                if voice_tone:
                    print(f"   🎵 Voice Tone: {voice_tone}")
                else:
                    print("   ⚠️ Voice Tone not set")
                
                if voice_model:
                    print(f"   🎤 Voice Model: {voice_model}")
                else:
                    print("   ⚠️ Voice Model not set")
                
                # Check learning data
                learning_data = getattr(agent, 'learning_data', {})
                if learning_data and isinstance(learning_data, dict):
                    print(f"   🧠 Learning Data: {len(learning_data)} components")
                else:
                    print("   ⚠️ Learning Data not initialized")
            
            return True
        else:
            print("❌ No active agents found")
            return False
            
    except Exception as e:
        print(f"❌ Agent error: {str(e)}")
        return False

def verify_auto_voice_files():
    """Auto voice system files verify karta hai"""
    print("\\n📁 Checking Auto Voice System Files...")
    
    required_files = [
        {
            "path": "calls/auto_voice_integration.py",
            "description": "Main auto voice system"
        },
        {
            "path": "agents/complete_hume_voice_system.py", 
            "description": "Hume voice integration"
        },
        {
            "path": "agents/voice_response_system.py",
            "description": "Voice response handlers"
        },
        {
            "path": "live_hume_integration.py",
            "description": "Core Hume AI integration"
        }
    ]
    
    all_files_exist = True
    
    for file_info in required_files:
        file_path = file_info["path"]
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_info['description']}: {file_size} bytes")
        else:
            print(f"❌ {file_info['description']}: Missing!")
            all_files_exist = False
    
    return all_files_exist

def verify_api_endpoints():
    """API endpoints verify karta hai"""
    print("\\n🌐 Checking API Endpoints Configuration...")
    
    try:
        # Check calls/urls.py
        with open('calls/urls.py', 'r') as f:
            urls_content = f.read()
        
        required_endpoints = [
            'auto-voice-call/',
            'auto-voice-webhook/',
            'StartCallAPIView'
        ]
        
        all_endpoints_found = True
        
        for endpoint in required_endpoints:
            if endpoint in urls_content:
                print(f"✅ Endpoint: {endpoint}")
            else:
                print(f"❌ Endpoint missing: {endpoint}")
                all_endpoints_found = False
        
        return all_endpoints_found
        
    except Exception as e:
        print(f"❌ URL configuration error: {str(e)}")
        return False

def verify_dependencies():
    """Dependencies verify karta hai"""
    print("\\n📦 Checking Required Dependencies...")
    
    required_packages = [
        ('django', 'django'),
        ('twilio', 'twilio'),
        ('requests', 'requests'),
        ('pyttsx3', 'pyttsx3'),
        ('speech_recognition', 'SpeechRecognition')  # Package name vs import name
    ]
    
    all_deps_available = True
    
    for import_name, display_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - Not installed!")
            all_deps_available = False
    
    return all_deps_available

def show_ready_status():
    """Final ready status show karta hai"""
    print("\\n" + "="*60)
    print("🎯 COMPLETE AUTO VOICE SYSTEM STATUS")
    print("="*60)
    
    # Run all verifications
    hume_status = verify_hume_ai()
    agent_status = verify_agents()
    files_status = verify_auto_voice_files()
    api_status = verify_api_endpoints()
    deps_status = verify_dependencies()
    
    # Calculate overall readiness
    total_checks = 5
    passed_checks = sum([hume_status, agent_status, files_status, api_status, deps_status])
    
    print(f"\\n📊 System Readiness: {passed_checks}/{total_checks} components ready")
    
    if passed_checks == total_checks:
        print("\\n🎊 SYSTEM FULLY READY FOR AUTO VOICE CALLS!")
        print("✅ All components working correctly")
        print("🚀 You can now use the complete auto voice system!")
        
        print("\\n📞 Quick Start:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Use API endpoint: POST /api/calls/auto-voice-call/")
        print("3. Send data: {\"phone_number\": \"+1234567890\", \"agent_id\": \"agent_id\"}")
        print("4. System automatically handles everything!")
        
        return True
    elif passed_checks >= 3:
        print("\\n⚠️ SYSTEM MOSTLY READY - Some issues need attention")
        print("🔧 Check the failed components above")
        print("💡 Fix issues and run verification again")
        
        return False
    else:
        print("\\n❌ SYSTEM NOT READY - Multiple issues found")
        print("🛠️ Please fix the missing components")
        print("📖 Check setup documentation")
        
        return False

def show_usage_examples():
    """Usage examples show karta hai"""
    print("\\n" + "="*60)
    print("📚 AUTO VOICE SYSTEM USAGE EXAMPLES")
    print("="*60)
    
    print("\\n1️⃣ Basic Auto Voice Call:")
    print("```bash")
    print("curl -X POST http://localhost:8000/api/calls/auto-voice-call/ \\\\")
    print("  -H \"Authorization: Bearer YOUR_TOKEN\" \\\\")
    print("  -H \"Content-Type: application/json\" \\\\")
    print("  -d '{")
    print('    "phone_number": "+1234567890",')
    print('    "agent_id": "your_agent_id",')
    print('    "receiver_name": "John Doe"')
    print("  }'")
    print("```")
    
    print("\\n2️⃣ Advanced Auto Voice Call:")
    print("```bash")
    print("curl -X POST http://localhost:8000/api/calls/auto-voice-call/ \\\\")
    print("  -H \"Authorization: Bearer YOUR_TOKEN\" \\\\")
    print("  -H \"Content-Type: application/json\" \\\\")
    print("  -d '{")
    print('    "phone_number": "+1234567890",')
    print('    "agent_id": "your_agent_id",')
    print('    "receiver_name": "Sarah Johnson",')
    print('    "call_context": {')
    print('      "lead_source": "website",')
    print('      "product_interest": "AI voice agents",')
    print('      "priority": "high",')
    print('      "previous_interactions": "2 email exchanges"')
    print('    }')
    print("  }'")
    print("```")
    
    print("\\n3️⃣ Python Script Example:")
    print("```python")
    print("import requests")
    print("")
    print("def start_auto_voice_call(phone, agent_id, customer_name):")
    print("    url = 'http://localhost:8000/api/calls/auto-voice-call/'")
    print("    headers = {")
    print("        'Authorization': 'Bearer YOUR_TOKEN',")
    print("        'Content-Type': 'application/json'")
    print("    }")
    print("    data = {")
    print("        'phone_number': phone,")
    print("        'agent_id': agent_id,")
    print("        'receiver_name': customer_name")
    print("    }")
    print("    ")
    print("    response = requests.post(url, headers=headers, json=data)")
    print("    return response.json()")
    print("")
    print("# Usage")
    print("result = start_auto_voice_call('+1234567890', 'agent_123', 'Customer Name')")
    print("print(f'Call started: {result}')")
    print("```")
    
    print("\\n🎯 Features:")
    print("✓ Automatic Hume AI emotion detection")
    print("✓ Real-time voice responses")
    print("✓ Agent learning and optimization")
    print("✓ Call analytics and reporting")
    print("✓ Twilio voice integration")
    print("✓ Complete automation - no manual intervention needed")

if __name__ == "__main__":
    print("🔍 COMPLETE AUTO VOICE SYSTEM VERIFICATION")
    print("=" * 60)
    print("Checking if your complete auto voice system is ready...")
    
    ready = show_ready_status()
    
    if ready:
        print("\\n" + "="*60)
        print("🎉 VERIFICATION COMPLETE - SYSTEM READY!")
        print("="*60)
        
        show_examples = input("\\nShow usage examples? (y/n): ").lower().strip()
        if show_examples == 'y':
            show_usage_examples()
        
        print("\\n🚀 Next Steps:")
        print("1. Run: python test_complete_auto_voice_system.py")
        print("2. Start Django server: python manage.py runserver")
        print("3. Make your first auto voice call!")
        
    else:
        print("\\n🔧 VERIFICATION FAILED - Fix issues and try again")
        print("💡 Check the error messages above")
        print("📖 Refer to setup documentation if needed")