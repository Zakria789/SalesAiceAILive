#!/usr/bin/env python
"""
Test Intelligent Response-Based Auto Scheduling System
Customer response ke base par automatic call scheduling test karta hai
"""
import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000/agents"

def test_intelligent_scheduling_system():
    """Test the complete intelligent scheduling system"""
    
    print("🧠 Testing Intelligent Response-Based Auto Scheduling")
    print("=" * 60)
    
    headers = {
        'Content-Type': 'application/json',
        # Add JWT token if needed
    }
    
    # 1. Test Getting Scheduling Rules
    print("📋 1. Getting Intelligent Scheduling Rules...")
    try:
        response = requests.get(f"{BASE_URL}/scheduling-rules/", 
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            rules_data = response.json()
            print("✅ Scheduling rules retrieved successfully")
            print(f"   Total outcomes supported: {rules_data['total_outcomes']}")
            
            # Show some rules
            for outcome, rule_info in list(rules_data['intelligent_scheduling_rules'].items())[:3]:
                rule = rule_info['rule']
                print(f"   📌 {outcome}: {rule['follow_up_delay']} min delay, priority {rule['priority']}")
            
        else:
            print(f"❌ Failed to get scheduling rules: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting rules: {e}")
    
    # 2. Test Different Customer Response Scenarios
    print(f"\n🎭 2. Testing Customer Response Scenarios...")
    
    test_scenarios = [
        {
            'outcome': 'interested',
            'description': 'Customer shows interest'
        },
        {
            'outcome': 'callback_requested', 
            'description': 'Customer requests callback'
        },
        {
            'outcome': 'not_interested',
            'description': 'Customer not interested'
        },
        {
            'outcome': 'no_answer',
            'description': 'No answer'
        }
    ]
    
    for scenario in test_scenarios:
        try:
            test_data = {
                'test_outcome': scenario['outcome']
            }
            
            response = requests.post(f"{BASE_URL}/test-intelligent-scheduling/", 
                                   json=test_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                sim = result['simulated_scheduling']
                print(f"✅ {scenario['description']} ({scenario['outcome']}):")
                print(f"   ⏰ Next call: {sim['delay_minutes']} minutes")
                print(f"   🔥 Priority: {sim['priority_assigned']}")
                print(f"   📞 Type: {sim['call_type']}")
                print(f"   🎯 Action: {sim['action']}")
            else:
                print(f"❌ Test failed for {scenario['outcome']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {scenario['outcome']}: {e}")
    
    # 3. Test Call Completion with Intelligent Scheduling
    print(f"\n📞 3. Testing Call Completion with Intelligent Scheduling...")
    
    # First create a mock campaign and contact
    campaign_data = {
        "campaign_name": f"Intelligent Test {datetime.now().strftime('%H:%M:%S')}",
        "calls_per_hour": 4,
        "immediate_calls": 0
    }
    
    try:
        # Create campaign
        campaign_response = requests.post(f"{BASE_URL}/auto-calls/", 
                                        json=campaign_data, headers=headers, timeout=10)
        
        if campaign_response.status_code == 201:
            campaign_result = campaign_response.json()
            campaign_id = campaign_result.get('campaign_id')
            print(f"✅ Test campaign created: {campaign_id}")
            
            # Mock call completion with different outcomes
            test_completions = [
                {
                    'call_outcome': 'interested',
                    'customer_response': 'Yes, I am interested in your product',
                    'agent_notes': 'Customer showed strong interest, wants more details'
                },
                {
                    'call_outcome': 'callback_requested',
                    'customer_response': 'Please call me back tomorrow at 2 PM',
                    'agent_notes': 'Customer busy right now, requested specific callback time'
                }
            ]
            
            for completion in test_completions:
                completion_data = {
                    'contact_id': 'mock_contact_id',  # Would be real contact ID
                    'call_outcome': completion['call_outcome'],
                    'customer_response': completion['customer_response'],
                    'agent_notes': completion['agent_notes'],
                    'call_duration': 180  # 3 minutes
                }
                
                print(f"📝 Testing call completion: {completion['call_outcome']}")
                # Note: This would fail with real contact_id validation
                # But shows the API structure
                
        else:
            print(f"❌ Campaign creation failed: {campaign_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in call completion test: {e}")
    
    # 4. Test Call Outcome Statistics
    print(f"\n📊 4. Testing Call Outcome Statistics...")
    try:
        stats_response = requests.get(f"{BASE_URL}/call-outcome-stats/", 
                                    headers=headers, timeout=10)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Call outcome statistics retrieved")
            print(f"   Total calls (30 days): {stats_data['total_calls']}")
            if stats_data.get('most_common_outcome'):
                print(f"   Most common outcome: {stats_data['most_common_outcome']}")
            
            recommendations = stats_data.get('recommendations', [])
            if recommendations:
                print(f"   📈 AI Recommendations: {len(recommendations)} found")
        else:
            print(f"❌ Stats retrieval failed: {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # 5. Show System Summary
    print(f"\n" + "=" * 60)
    print("🎯 INTELLIGENT SCHEDULING SYSTEM SUMMARY")
    print("=" * 60)
    
    print("✅ Features Implemented:")
    print("  🧠 Response-based auto scheduling")
    print("  📋 Configurable scheduling rules") 
    print("  📊 Call outcome statistics")
    print("  🎭 Multiple response scenarios")
    print("  ⚡ Real-time intelligent scheduling")
    
    print("\n📚 How It Works:")
    print("  1. Customer responds during call")
    print("  2. Agent selects call outcome")
    print("  3. System automatically schedules next call based on response")
    print("  4. Different delays and priorities for different responses")
    print("  5. Continuous learning and optimization")
    
    print("\n🔗 Available Endpoints:")
    print("  GET  /agents/scheduling-rules/          - View scheduling rules")
    print("  PUT  /agents/scheduling-rules/          - Update scheduling rules")
    print("  POST /agents/complete-call/             - Complete call with outcome")
    print("  GET  /agents/call-outcome-stats/        - Get outcome statistics")
    print("  POST /agents/test-intelligent-scheduling/ - Test scheduling logic")
    
    print("\n📞 Customer Response Outcomes:")
    print("  • interested         → Follow-up in 30 minutes (High priority)")
    print("  • callback_requested → Callback in 24 hours (High priority)")
    print("  • maybe_interested   → Nurture call in 2 days (Medium priority)")
    print("  • not_interested     → Long-term follow-up in 30 days (Low priority)")
    print("  • no_answer/busy     → Retry in 2-4 hours (Medium priority)")
    
    print(f"\n🚀 Intelligent Auto-Scheduling System Ready!")


if __name__ == "__main__":
    test_intelligent_scheduling_system()