"""
HumeAI + Twilio Intelligent Scheduling Complete Test
Complete system ko test karne ke liye comprehensive test script

🚀 Features Test Kar Rahe Hain:
1. HumeAI call completion se automatic scheduling
2. Customer response analysis (emotions + keywords)
3. Intelligent next call scheduling based on outcome
4. Complete API integration testing
"""

import requests
import json
from datetime import datetime
import time

# Test Configuration
BASE_URL = "http://localhost:8000/api/hume-twilio"
API_TOKEN = "your_api_token_here"  # Replace with actual token

HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

TEST_SCENARIOS = [
    {
        'name': 'Interested Customer - Should Schedule Soon',
        'phone': '+1234567890',
        'outcome': 'interested',
        'expected_next_call': 'within 1 hour'
    },
    {
        'name': 'Callback Requested - Should Schedule for Tomorrow',
        'phone': '+1234567891',
        'outcome': 'callback_requested',
        'expected_next_call': 'next day'
    },
    {
        'name': 'Maybe Interested - Should Schedule in 3 Days',
        'phone': '+1234567892',
        'outcome': 'maybe_interested',
        'expected_next_call': '3 days later'
    },
    {
        'name': 'Not Interested - Should Not Schedule',
        'phone': '+1234567893',
        'outcome': 'not_interested',
        'expected_next_call': 'no scheduling'
    },
    {
        'name': 'No Answer - Should Schedule Retry',
        'phone': '+1234567894',
        'outcome': 'no_answer',
        'expected_next_call': '2 hours later'
    }
]


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)


def print_result(success, message, data=None):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if data:
        print(f"   Data: {json.dumps(data, indent=2, default=str)[:200]}...")


def test_intelligent_scheduling_system():
    """Test complete intelligent scheduling system"""
    print_header("HUME AI + TWILIO INTELLIGENT SCHEDULING TEST")
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'scenarios': []
    }
    
    # Test 1: Get System Status
    print("\n1️⃣ Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/intelligent/scheduling-stats/", headers=HEADERS)
        if response.status_code == 200:
            stats = response.json()
            print_result(True, "System status retrieved successfully", stats.get('stats'))
            results['passed_tests'] += 1
        else:
            print_result(False, f"Failed to get system status: {response.status_code}")
            results['failed_tests'] += 1
    except Exception as e:
        print_result(False, f"System status error: {str(e)}")
        results['failed_tests'] += 1
    
    results['total_tests'] += 1
    
    # Test 2: Test Each Scenario
    for i, scenario in enumerate(TEST_SCENARIOS, 2):
        print(f"\n{i}️⃣ Testing Scenario: {scenario['name']}")
        
        try:
            # Test intelligent scheduling with sample data
            test_data = {
                'test_phone': scenario['phone'],
                'test_outcome': scenario['outcome']
            }
            
            response = requests.post(
                f"{BASE_URL}/intelligent/test-scheduling/", 
                headers=HEADERS,
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if scheduling worked as expected
                scheduling_result = result.get('scheduling_result', {})
                next_call_scheduled = scheduling_result.get('next_call_scheduled', False)
                
                # Validate expected outcome
                if scenario['outcome'] in ['interested', 'callback_requested', 'maybe_interested', 'no_answer']:
                    expected_scheduled = True
                else:  # not_interested, busy
                    expected_scheduled = False
                
                success = next_call_scheduled == expected_scheduled
                
                scenario_result = {
                    'scenario': scenario['name'],
                    'phone': scenario['phone'],
                    'outcome': scenario['outcome'],
                    'next_call_scheduled': next_call_scheduled,
                    'expected': expected_scheduled,
                    'success': success,
                    'scheduling_details': scheduling_result
                }
                
                results['scenarios'].append(scenario_result)
                
                if success:
                    print_result(True, f"Scenario passed: {scenario['outcome']} -> scheduled={next_call_scheduled}")
                    results['passed_tests'] += 1
                else:
                    print_result(False, f"Scenario failed: expected scheduled={expected_scheduled}, got {next_call_scheduled}")
                    results['failed_tests'] += 1
                    
            else:
                print_result(False, f"API call failed: {response.status_code} - {response.text}")
                results['failed_tests'] += 1
                
        except Exception as e:
            print_result(False, f"Scenario test error: {str(e)}")
            results['failed_tests'] += 1
        
        results['total_tests'] += 1
    
    # Test 3: Customer Call History Test
    print(f"\n{len(TEST_SCENARIOS) + 2}️⃣ Testing Customer Call History...")
    try:
        test_phone = TEST_SCENARIOS[0]['phone']
        response = requests.get(
            f"{BASE_URL}/intelligent/customer-history/",
            headers=HEADERS,
            params={'phone_number': test_phone}
        )
        
        if response.status_code == 200:
            history = response.json()
            print_result(True, "Customer history retrieved", {
                'total_calls': history.get('total_calls'),
                'scheduled_calls': history.get('scheduled_calls')
            })
            results['passed_tests'] += 1
        else:
            print_result(False, f"Failed to get customer history: {response.status_code}")
            results['failed_tests'] += 1
            
    except Exception as e:
        print_result(False, f"Customer history error: {str(e)}")
        results['failed_tests'] += 1
    
    results['total_tests'] += 1
    
    return results


def test_hume_emotion_analysis():
    """Test HumeAI emotion analysis integration"""
    print_header("HUME AI EMOTION ANALYSIS TEST")
    
    # Test emotion mapping
    test_emotions = [
        {'emotion': 'Joy', 'expected_outcome': 'interested'},
        {'emotion': 'Excitement', 'expected_outcome': 'interested'},
        {'emotion': 'Anger', 'expected_outcome': 'not_interested'},
        {'emotion': 'Confusion', 'expected_outcome': 'maybe_interested'},
        {'emotion': 'Disappointment', 'expected_outcome': 'not_interested'}
    ]
    
    from HumeAiTwilio.intelligent_hume_scheduler import HumeTwilioIntelligentScheduler
    
    scheduler = HumeTwilioIntelligentScheduler()
    
    passed = 0
    total = len(test_emotions)
    
    for test in test_emotions:
        emotion = test['emotion']
        expected = test['expected_outcome']
        
        # Test emotion mapping
        actual = scheduler.hume_emotion_to_outcome.get(emotion)
        
        if actual == expected:
            print_result(True, f"Emotion mapping: {emotion} -> {actual}")
            passed += 1
        else:
            print_result(False, f"Emotion mapping failed: {emotion} -> {actual} (expected {expected})")
    
    return {'total': total, 'passed': passed, 'failed': total - passed}


def generate_test_report(results):
    """Generate comprehensive test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = results['total_tests']
    passed_tests = results['passed_tests']
    failed_tests = results['failed_tests']
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\n🔍 Scenario Details:")
    for scenario in results.get('scenarios', []):
        status = "✅" if scenario['success'] else "❌"
        print(f"   {status} {scenario['scenario']}")
        print(f"      Phone: {scenario['phone']}")
        print(f"      Outcome: {scenario['outcome']}")
        print(f"      Scheduled: {scenario['next_call_scheduled']}")
    
    # Overall assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Intelligent scheduling system is working great!")
    elif success_rate >= 60:
        print(f"\n👍 GOOD! System is mostly working, minor issues need attention.")
    else:
        print(f"\n⚠️ NEEDS WORK! System requires debugging and fixes.")
    
    return success_rate >= 80


def test_api_endpoints():
    """Test all API endpoints availability"""
    print_header("API ENDPOINTS AVAILABILITY TEST")
    
    endpoints = [
        '/intelligent/scheduling-stats/',
        '/intelligent/test-scheduling/',
        '/intelligent/customer-history/',
        '/agents-list/',
        '/get-all-calls/'
    ]
    
    available = 0
    total = len(endpoints)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)
            if response.status_code in [200, 400]:  # 400 might be expected for missing params
                print_result(True, f"Endpoint available: {endpoint}")
                available += 1
            else:
                print_result(False, f"Endpoint error {response.status_code}: {endpoint}")
        except requests.exceptions.RequestException as e:
            print_result(False, f"Endpoint unreachable: {endpoint} - {str(e)}")
    
    return {'total': total, 'available': available, 'unavailable': total - available}


if __name__ == "__main__":
    print("🚀 Starting HumeAI + Twilio Intelligent Scheduling Complete Test Suite")
    print("=" * 80)
    
    # Test 1: API Endpoints
    endpoint_results = test_api_endpoints()
    
    # Test 2: Emotion Analysis
    emotion_results = test_hume_emotion_analysis()
    
    # Test 3: Intelligent Scheduling
    scheduling_results = test_intelligent_scheduling_system()
    
    # Final Report
    print_header("FINAL TEST REPORT")
    
    print("📋 Test Suite Results:")
    print(f"   API Endpoints: {endpoint_results['available']}/{endpoint_results['total']} available")
    print(f"   Emotion Analysis: {emotion_results['passed']}/{emotion_results['total']} passed")
    print(f"   Intelligent Scheduling: {scheduling_results['passed_tests']}/{scheduling_results['total_tests']} passed")
    
    overall_success = (
        endpoint_results['available'] >= endpoint_results['total'] * 0.8 and
        emotion_results['passed'] >= emotion_results['total'] * 0.8 and
        scheduling_results['passed_tests'] >= scheduling_results['total_tests'] * 0.8
    )
    
    if overall_success:
        print("\n🎉 SYSTEM READY! HumeAI + Twilio intelligent scheduling is fully operational!")
        print("\n🚀 Next Steps:")
        print("   1. Deploy to production environment")
        print("   2. Configure real HumeAI API keys")
        print("   3. Set up Twilio webhooks with public URL")
        print("   4. Start making intelligent auto-scheduled calls!")
    else:
        print("\n⚠️ SYSTEM NEEDS ATTENTION! Please fix issues before production.")
        print("\n🔧 Recommended Actions:")
        print("   1. Check Django server is running on localhost:8000")
        print("   2. Verify database migrations are applied")
        print("   3. Ensure all required packages are installed")
        print("   4. Check API authentication settings")
    
    print(f"\n🕐 Test completed at: {datetime.now()}")
    print("=" * 80)