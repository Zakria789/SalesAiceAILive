"""
🧪 Test Provider-Based API Responses
Test all call-related APIs to verify they return provider-specific data
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://uncontortioned-na-ponderously.ngrok-free.dev"
HEADERS = {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true'
}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def test_initiate_call():
    """Test 1: Initiate Call API - Should return provider-specific data"""
    print_section("TEST 1: Initiate Call API")
    
    url = f"{BASE_URL}/api/hume-twilio/initiate-call/"
    data = {
        "phone_no": "+923030061756",
        "agent_id": "1"
    }
    
    try:
        print(f"📤 POST {url}")
        print(f"📦 Body: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"📊 Response:")
        print(json.dumps(result, indent=2))
        
        # Validate provider-specific fields
        if result.get('success'):
            provider = result.get('provider')
            call_data = result.get('call', {})
            
            print(f"\n🔍 Provider Check:")
            print(f"   Provider: {provider}")
            
            if provider == 'vonage':
                required_fields = ['uuid', 'conversation_uuid', 'status']
                print(f"   ✅ Checking Vonage fields: {required_fields}")
                for field in required_fields:
                    value = call_data.get(field)
                    status = "✅" if value else "❌"
                    print(f"      {status} {field}: {value}")
            else:
                required_fields = ['sid', 'from', 'to', 'price_unit']
                print(f"   ✅ Checking Twilio fields: {required_fields}")
                for field in required_fields:
                    value = call_data.get(field)
                    status = "✅" if value is not None else "❌"
                    print(f"      {status} {field}: {value}")
            
            return call_data.get('uuid') or call_data.get('sid')
        else:
            print(f"❌ Error: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_get_call_status(call_sid):
    """Test 2: Get Call Status API - Should return provider-specific data"""
    print_section("TEST 2: Get Call Status API")
    
    if not call_sid:
        print("⏭️  Skipping - No call_sid from previous test")
        return
    
    url = f"{BASE_URL}/api/hume-twilio/call-status/{call_sid}/"
    
    try:
        print(f"📤 GET {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=30)
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"📊 Response:")
        print(json.dumps(result, indent=2))
        
        # Validate provider field
        if result.get('success'):
            provider = result.get('provider')
            call_data = result.get('call', {})
            
            print(f"\n🔍 Provider Check:")
            print(f"   Provider: {provider}")
            print(f"   Call Status: {call_data.get('status')}")
            print(f"   Duration: {call_data.get('duration')} seconds")
            
            if provider == 'vonage':
                print(f"   ✅ Vonage UUID: {call_data.get('call_sid')}")
                print(f"   ✅ Conversation UUID: {call_data.get('conversation_uuid')}")
                print(f"   ✅ Network: {call_data.get('network')}")
            else:
                print(f"   ✅ Twilio SID: {call_data.get('call_sid')}")
                print(f"   ✅ Price: {call_data.get('price')} {call_data.get('price_unit')}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_get_call_data(call_sid):
    """Test 3: Get Complete Call Data API - Should work with provider-specific pricing"""
    print_section("TEST 3: Get Complete Call Data API")
    
    if not call_sid:
        print("⏭️  Skipping - No call_sid from previous test")
        return
    
    url = f"{BASE_URL}/api/hume-twilio/get-call-data/{call_sid}/"
    
    try:
        print(f"📤 GET {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=30)
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        
        if result.get('success'):
            call_data = result.get('call', {})
            conversation = result.get('conversation', {})
            data_sources = result.get('data_sources', {})
            
            print(f"\n📊 Call Summary:")
            print(f"   Status: {call_data.get('status')}")
            print(f"   Duration: {call_data.get('duration')} seconds")
            print(f"   Direction: {call_data.get('direction_badge')}")
            print(f"   Total Messages: {conversation.get('total_messages')}")
            
            print(f"\n💾 Data Sources:")
            for key, source in data_sources.items():
                print(f"   {key}: {source}")
            
            print(f"\n💰 Pricing Info:")
            if 'price' in call_data:
                print(f"   Price: {call_data.get('price')} {call_data.get('price_unit', '')}")
            elif 'rate' in call_data:
                print(f"   Rate: {call_data.get('rate')}")
            else:
                print(f"   Not available (call may not be completed)")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("  PROVIDER-BASED API RESPONSE TESTS")
    print("🧪" * 35)
    print(f"\nTesting APIs at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Initiate Call (returns call_sid)
    call_sid = test_initiate_call()
    
    # Wait a moment for call to process
    if call_sid:
        print("\n⏳ Waiting 3 seconds for call to process...")
        import time
        time.sleep(3)
    
    # Test 2: Get Call Status
    test_get_call_status(call_sid)
    
    # Test 3: Get Complete Call Data
    test_get_call_data(call_sid)
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\n📝 Expected Behavior:")
    print("   - Vonage calls should return: uuid, conversation_uuid, network")
    print("   - Twilio calls should return: sid, from, to, price, price_unit")
    print("   - All APIs should include 'provider' field")
    print("   - Database should store provider info correctly")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()
