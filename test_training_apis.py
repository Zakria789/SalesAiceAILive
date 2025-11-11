"""
🧪 Test Continuous Learning APIs
=================================

Tests all 6 training APIs
"""

import requests
import json

BASE_URL = "http://localhost:8002/api/agent"


def test_train_from_call():
    """Test API 1: Train from call"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Train from Call")
    print("="*70)
    
    payload = {
        "call_sid": "CA123456789",
        "conversation": [
            {"role": "agent", "text": "Hello! This is Sarah from SalesAice.ai", "timestamp": "2025-10-22T10:00:00"},
            {"role": "user", "text": "Hi, what do you do?", "timestamp": "2025-10-22T10:00:05"},
            {"role": "agent", "text": "We help businesses automate sales with AI", "timestamp": "2025-10-22T10:00:10"},
            {"role": "user", "text": "How much does it cost?", "timestamp": "2025-10-22T10:00:15"},
            {"role": "agent", "text": "Starting at $299/month for small teams", "timestamp": "2025-10-22T10:00:20"}
        ],
        "outcome": "successful",
        "metadata": {
            "duration": 120,
            "customer_name": "John Doe"
        }
    }
    
    response = requests.post(f"{BASE_URL}/train-from-call/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_train_from_document():
    """Test API 2: Train from document"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Train from Document")
    print("="*70)
    
    # Create a test document
    with open('test_doc.txt', 'w') as f:
        f.write("""
        SalesAice.ai Product Information
        
        Our platform offers:
        - AI-powered cold calling
        - Smart lead scoring
        - Automated follow-ups
        - Real-time analytics
        
        Pricing:
        - Small: $299/month (1-5 users)
        - Growing: $799/month (5-20 users)
        - Enterprise: Custom pricing
        
        Free 14-day trial available!
        """)
    
    with open('test_doc.txt', 'rb') as f:
        files = {'file': f}
        data = {
            'category': 'product_info',
            'title': 'SalesAice Product Guide'
        }
        response = requests.post(f"{BASE_URL}/train-from-document/", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_train_from_sales_script():
    """Test API 3: Train from sales script"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Train from Sales Script")
    print("="*70)
    
    payload = {
        "script_name": "Cold Call Script v1",
        "sections": {
            "opening": "Hello! This is Sarah from SalesAice.ai. We help businesses automate sales with AI. Do you have a moment?",
            "value_proposition": "We've helped over 500 companies increase their sales by 30% through AI automation.",
            "objection_handling": {
                "price": "I understand budget is important. Our ROI typically pays for itself in the first month.",
                "timing": "I appreciate you're busy. That's exactly why automation helps - it saves 10-20 hours per week.",
                "not_interested": "I understand. Can I ask what challenges you're facing with your current sales process?"
            },
            "closing": "Would you like to see a quick 15-minute demo? I can show you how it works for companies like yours."
        }
    }
    
    response = requests.post(f"{BASE_URL}/train-from-sales-script/", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_query_knowledge():
    """Test API 4: Query knowledge"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Query Knowledge")
    print("="*70)
    
    queries = [
        "What is the pricing?",
        "How much does it cost?",
        "What features do you have?",
        "Do you have a free trial?"
    ]
    
    for query in queries:
        payload = {
            "query": query,
            "n_results": 2,
            "source": "all"
        }
        
        response = requests.post(f"{BASE_URL}/query-knowledge/", json=payload)
        print(f"\n❓ Query: {query}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                print(f"📋 Top Result:")
                print(f"   Content: {data['results'][0]['content'][:100]}...")
                print(f"   Distance: {data['results'][0]['distance']:.3f}")


def test_get_stats():
    """Test API 5: Get stats"""
    print("\n" + "="*70)
    print("🧪 TEST 5: Get Training Stats")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/training-stats/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("CONTINUOUS LEARNING API TESTS")
    print("🚀"*35)
    
    try:
        # Test 1: Train from call
        test_train_from_call()
        
        # Test 2: Train from document
        test_train_from_document()
        
        # Test 3: Train from sales script
        test_train_from_sales_script()
        
        # Test 4: Query knowledge
        test_query_knowledge()
        
        # Test 5: Get stats
        test_get_stats()
        
        print("\n" + "✅"*35)
        print("ALL TESTS COMPLETE!")
        print("✅"*35)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    run_all_tests()
