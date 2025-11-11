"""
Quick Test - Call Initiation APIs

Tests all 4 call initiation endpoints:
1. Get available agents
2. Initiate single call
3. Get call status
4. Bulk call initiation
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_get_agents():
    """Test: Get available agents"""
    print("\n" + "="*60)
    print("TEST 1: Get Available Agents")
    print("="*60)
    
    url = f"{BASE_URL}/api/call/agents/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data.get('agents', [])
    else:
        print(f"Error: {response.text}")
        return []

def test_initiate_call():
    """Test: Initiate single call"""
    print("\n" + "="*60)
    print("TEST 2: Initiate Single Call")
    print("="*60)
    
    url = f"{BASE_URL}/api/call/initiate/"
    
    # Test data
    data = {
        "phone_number": "+1234567890",  # Replace with your test number
        "agent_id": "sarah_sales",
        "customer_name": "Test Customer",
        "metadata": {
            "source": "test_script",
            "campaign": "testing",
            "priority": "high"
        }
    }
    
    print(f"Request Data:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(url, json=data)
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        # Return call_sid for status check
        return result.get('call', {}).get('call_sid')
    else:
        print(f"Error: {response.text}")
        return None

def test_call_status(call_sid):
    """Test: Get call status"""
    print("\n" + "="*60)
    print("TEST 3: Get Call Status")
    print("="*60)
    
    if not call_sid:
        print("No call_sid provided. Skipping status check.")
        return
    
    url = f"{BASE_URL}/api/call/status/{call_sid}/"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")

def test_bulk_calls():
    """Test: Bulk call initiation"""
    print("\n" + "="*60)
    print("TEST 4: Bulk Call Initiation")
    print("="*60)
    
    url = f"{BASE_URL}/api/call/initiate-bulk/"
    
    # Test data - multiple calls
    data = {
        "calls": [
            {
                "phone_number": "+1234567890",
                "agent_id": "sarah_sales",
                "customer_name": "Customer 1",
                "metadata": {"campaign": "bulk_test_1"}
            },
            {
                "phone_number": "+0987654321",
                "agent_id": "alex_support",
                "customer_name": "Customer 2",
                "metadata": {"campaign": "bulk_test_2"}
            },
            {
                "phone_number": "+1122334455",
                "agent_id": "emma_onboarding",
                "customer_name": "Customer 3"
            }
        ]
    }
    
    print(f"Request Data:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(url, json=data)
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")

def test_validation_errors():
    """Test: Validation error handling"""
    print("\n" + "="*60)
    print("TEST 5: Validation Error Handling")
    print("="*60)
    
    url = f"{BASE_URL}/api/call/initiate/"
    
    # Test missing phone number
    print("\nTest 5a: Missing phone number")
    data = {"agent_id": "sarah_sales"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code} - {response.json().get('error')}")
    
    # Test invalid phone format (no country code)
    print("\nTest 5b: Invalid phone format")
    data = {"phone_number": "1234567890", "agent_id": "sarah_sales"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code} - {response.json().get('error')}")
    
    # Test invalid agent_id
    print("\nTest 5c: Invalid agent_id")
    data = {"phone_number": "+1234567890", "agent_id": "invalid_agent"}
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code} - {response.json().get('error')}")

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print(" CALL INITIATION API TESTS")
    print("="*70)
    
    try:
        # Test 1: Get agents
        agents = test_get_agents()
        
        time.sleep(1)
        
        # Test 2: Initiate call
        call_sid = test_initiate_call()
        
        time.sleep(2)
        
        # Test 3: Get call status (if call was initiated)
        if call_sid:
            test_call_status(call_sid)
        
        time.sleep(1)
        
        # Test 4: Bulk calls
        test_bulk_calls()
        
        time.sleep(1)
        
        # Test 5: Validation errors
        test_validation_errors()
        
        print("\n" + "="*70)
        print(" ALL TESTS COMPLETED")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure Daphne server is running on port 8002!")
    print("   Run: daphne -p 8002 core.asgi:application\n")
    
    input("Press Enter to start tests...")
    run_all_tests()
