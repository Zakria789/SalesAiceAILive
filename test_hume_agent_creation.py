"""
Test HumeAI Agent Creation
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from HumeAiTwilio.hume_agent_service import hume_agent_service
from decouple import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hume_agent_creation():
    print("=" * 70)
    print("🤖 TESTING HUMEAI AGENT CREATION")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = config('HUME_API_KEY', default='')
    if not api_key:
        print("❌ HUME_API_KEY not found in environment!")
        print("   Add it to .env file: HUME_API_KEY=your_key_here")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]}")
    print()
    
    # Test agent creation
    print("Creating test agent in HumeAI...")
    print()
    
    config_id = hume_agent_service.create_agent(
        name="Test Agent",
        system_prompt="You are a helpful AI assistant for testing purposes.",
        voice_name="ITO",
        language="en"
    )
    
    print()
    print("=" * 70)
    if config_id:
        print(f"✅ SUCCESS! HumeAI agent created")
        print(f"   Config ID: {config_id}")
        print()
        print("🎉 HumeAI integration is working!")
    else:
        print("❌ FAILED to create HumeAI agent")
        print()
        print("Common issues:")
        print("1. Invalid API key")
        print("2. Network/firewall blocking HumeAI API")
        print("3. HumeAI API endpoint changed")
        print("4. Rate limiting")
        print()
        print("Check server logs above for detailed error messages")
    print()

if __name__ == "__main__":
    test_hume_agent_creation()
