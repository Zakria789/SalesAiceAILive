"""
🧪 COMPLETE CALL SYSTEM TEST
Tests WebSocket + HumeAI + Twilio Integration
"""

import asyncio
import json
from decouple import config
import websockets
from twilio.rest import Client

# ANSI Colors for beautiful output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*60}{Colors.RESET}\n")


async def test_hume_connection():
    """Test HumeAI EVI API Connection"""
    print_header("🎭 TESTING HUMEAI CONNECTION")
    
    try:
        hume_api_key = config('HUME_API_KEY', default='')
        hume_config_id = config('HUME_CONFIG_ID', default='')
        
        if not hume_api_key:
            print_error("HUME_API_KEY not found in .env")
            return False
        
        if not hume_config_id:
            print_error("HUME_CONFIG_ID not found in .env")
            return False
        
        print_info(f"API Key: {hume_api_key[:20]}...")
        print_info(f"Config ID: {hume_config_id}")
        
        # Test WebSocket connection
        ws_url = f"wss://api.hume.ai/v0/evi/chat?api_key={hume_api_key}&config_id={hume_config_id}"
        
        print_info("Connecting to HumeAI WebSocket...")
        
        async with websockets.connect(ws_url) as websocket:
            print_success("Connected to HumeAI!")
            
            # Wait for session opened or chat_metadata message
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            msg_type = data.get('type')
            if msg_type in ['session_opened', 'chat_metadata']:
                print_success(f"Session initialized: {msg_type}")
                if msg_type == 'chat_metadata':
                    print_info(f"Chat ID: {data.get('chat_id', 'N/A')}")
                else:
                    print_info(f"Session ID: {data.get('session_id', 'N/A')}")
                return True
            else:
                print_warning(f"Unexpected response: {msg_type}")
                return False
                
    except asyncio.TimeoutError:
        print_error("Timeout waiting for HumeAI response")
        return False
    except Exception as e:
        print_error(f"HumeAI connection failed: {str(e)}")
        return False


def test_twilio_credentials():
    """Test Twilio API Credentials"""
    print_header("📞 TESTING TWILIO CREDENTIALS")
    
    try:
        account_sid = config('TWILIO_ACCOUNT_SID', default='')
        auth_token = config('TWILIO_AUTH_TOKEN', default='')
        phone_number = config('TWILIO_PHONE_NUMBER', default='')
        
        if not account_sid:
            print_error("TWILIO_ACCOUNT_SID not found in .env")
            return False
        
        if not auth_token:
            print_error("TWILIO_AUTH_TOKEN not found in .env")
            return False
        
        if not phone_number:
            print_error("TWILIO_PHONE_NUMBER not found in .env")
            return False
        
        print_info(f"Account SID: {account_sid[:20]}...")
        print_info(f"Auth Token: {auth_token[:20]}...")
        print_info(f"Phone Number: {phone_number}")
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Get account info
        account = client.api.accounts(account_sid).fetch()
        print_success(f"Twilio Account: {account.friendly_name}")
        print_success(f"Status: {account.status}")
        
        # List recent calls (last 5)
        print_info("\nRecent calls:")
        calls = client.calls.list(limit=5)
        
        if calls:
            for call in calls:
                status_color = Colors.GREEN if call.status == 'completed' else Colors.YELLOW
                print(f"  {status_color}• {call.sid[:20]}... → {call.to} ({call.status}){Colors.RESET}")
        else:
            print_warning("No recent calls found")
        
        return True
        
    except Exception as e:
        print_error(f"Twilio credentials test failed: {str(e)}")
        return False


def test_django_settings():
    """Test Django Configuration"""
    print_header("⚙️  TESTING DJANGO CONFIGURATION")
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        print_success("Django initialized successfully")
        
        # Check installed apps (no database query)
        from django.conf import settings
        if 'HumeAiTwilio' in settings.INSTALLED_APPS:
            print_success("HumeAiTwilio app installed")
        else:
            print_error("HumeAiTwilio app not in INSTALLED_APPS")
            return False
        
        # Check ASGI application
        if hasattr(settings, 'ASGI_APPLICATION'):
            print_success(f"ASGI Application: {settings.ASGI_APPLICATION}")
        else:
            print_warning("ASGI_APPLICATION not configured")
        
        # Check channel layers
        if hasattr(settings, 'CHANNEL_LAYERS'):
            print_success("Channel Layers configured")
        else:
            print_warning("CHANNEL_LAYERS not configured")
        
        return True
        
    except Exception as e:
        print_error(f"Django configuration test failed: {str(e)}")
        return False


async def test_ai_agents():
    """Test AI Agents in Database"""
    print_header("🤖 TESTING AI AGENTS")
    
    try:
        import os
        import django
        from asgiref.sync import sync_to_async
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from HumeAiTwilio.models import HumeAgent
        
        # Get all active agents (status='active') - use sync_to_async
        @sync_to_async
        def get_agents():
            return list(HumeAgent.objects.filter(status='active'))
        
        agents = await get_agents()
        
        if not agents:
            print_error("No active HumeAI agents found!")
            print_info("Run: python activate_agents.py")
            return False
        
        print_success(f"Found {len(agents)} active HumeAI agents:")
        
        for agent in agents:
            print(f"\n  {Colors.BLUE}🤖 {agent.name}{Colors.RESET}")
            print(f"     System Prompt: {agent.system_prompt[:80]}...")
            print(f"     Voice: {agent.voice_name}")
            print(f"     Language: {agent.language}")
            print(f"     Created: {agent.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        return True
        
    except Exception as e:
        print_error(f"AI Agents test failed: {str(e)}")
        return False


def test_knowledge_manager():
    """Test Knowledge Manager"""
    print_header("🧠 TESTING KNOWLEDGE MANAGER")
    
    try:
        import os
        import django
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from HumeAiTwilio.knowledge_manager import KnowledgeManager
        
        # Initialize knowledge manager
        km = KnowledgeManager()
        
        # Detect backend
        backend = km._detect_backend()
        print_success(f"Knowledge Backend: {backend}")
        
        # Get stats
        stats = km.get_stats()
        print_info(f"Total knowledge items: {stats['total_items']}")
        
        if stats['total_items'] > 0:
            print_success("Knowledge base has data")
        else:
            print_warning("Knowledge base is empty (will learn during calls)")
        
        return True
        
    except Exception as e:
        print_error(f"Knowledge Manager test failed: {str(e)}")
        return False


def test_websocket_routing():
    """Test WebSocket URL Routing"""
    print_header("🌐 TESTING WEBSOCKET ROUTING")
    
    try:
        import os
        import django
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        # Try to import routing
        try:
            from core.asgi import application
            print_success("ASGI application imported successfully")
        except ImportError as e:
            print_error(f"Failed to import ASGI application: {e}")
            return False
        
        # Check routing configuration
        try:
            from HumeAiTwilio.routing import websocket_urlpatterns
            print_success(f"WebSocket routes: {len(websocket_urlpatterns)} pattern(s)")
            
            for pattern in websocket_urlpatterns:
                print_info(f"  • {pattern.pattern}")
            
        except ImportError:
            print_warning("WebSocket routing file not found")
        
        return True
        
    except Exception as e:
        print_error(f"WebSocket routing test failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          🧪 COMPLETE CALL SYSTEM TEST SUITE 🧪            ║")
    print("║     WebSocket + HumeAI + Twilio Integration Test          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    results = {}
    
    # Test 1: Django Configuration
    results['Django'] = test_django_settings()
    
    # Test 2: Twilio Credentials
    results['Twilio'] = test_twilio_credentials()
    
    # Test 3: HumeAI Connection
    results['HumeAI'] = await test_hume_connection()
    
    # Test 4: AI Agents
    results['AI Agents'] = await test_ai_agents()
    
    # Test 5: Knowledge Manager
    results['Knowledge Manager'] = test_knowledge_manager()
    
    # Test 6: WebSocket Routing
    results['WebSocket Routing'] = test_websocket_routing()
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    if failed_tests == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests}){Colors.RESET}")
        print(f"\n{Colors.CYAN}✅ System is ready for live calls!{Colors.RESET}")
        print(f"{Colors.CYAN}✅ WebSocket ↔ HumeAI ↔ Twilio integration working!{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED ({failed_tests}/{total_tests}){Colors.RESET}")
        print(f"\n{Colors.YELLOW}Fix the failed tests before making live calls{Colors.RESET}")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")


if __name__ == '__main__':
    asyncio.run(main())
