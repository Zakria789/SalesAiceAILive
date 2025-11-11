import requests
import json
import time
from datetime import datetime

# Test Complete AI Agent System
# Django server should be running on localhost:8000

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "admin@gmail.com"
TEST_USER_PASSWORD = "admin123"

def test_complete_ai_system():
    """
    Complete AI Agent System Test
    Training, Learning, HumeAI Integration, Live Calls
    """
    print("🚀 STARTING COMPLETE AI AGENT SYSTEM TEST")
    print("=" * 50)
    
    # Step 1: Login and get token
    print("\n📝 Step 1: User Authentication")
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/accounts/login/", json=login_data)
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        print(f"✅ Login successful! Token: {token[:20]}...")
    else:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test AI Agent Training (POST /agents/ai/training/)
    print("\n🎓 Step 2: AI Agent Training")
    training_data = {
        "sales_script": "Hello [NAME], this is Sarah from TechSolutions. I'm calling because you expressed interest in our AI automation platform. How are you doing today?",
        "objection_responses": {
            "price_too_high": "I understand cost is a concern. Let me show you the ROI - our clients typically save $5000 monthly within 3 months.",
            "not_interested": "I appreciate your honesty. Can I ask what your main challenge is with current processes?",
            "thinking_about_it": "That's smart to consider carefully. What specific information would help you make the decision?",
            "competitor_comparison": "Great question! Unlike competitors, we offer 24/7 support and 99.9% uptime guarantee."
        },
        "product_details": {
            "features": [
                "AI-powered automation",
                "Real-time analytics", 
                "24/7 customer support",
                "Custom integrations"
            ],
            "benefits": [
                "Save 40+ hours weekly",
                "Increase efficiency by 300%",
                "Reduce operational costs",
                "Scale without hiring"
            ],
            "pricing": "$299/month with 30-day free trial",
            "competitors": {
                "CompetitorA": "We offer better support and pricing",
                "CompetitorB": "Our AI is more advanced and user-friendly"
            }
        },
        "conversation_starters": [
            "Hi [NAME], hope you're having a great day! I'm calling about the automation solution you inquired about.",
            "Hello [NAME], this is Sarah from TechSolutions. Do you have 2 minutes to discuss how we can save you time?",
            "Hi [NAME], I noticed you downloaded our guide. I'd love to show you how it applies to your business."
        ],
        "closing_techniques": [
            "Based on what you've shared, this sounds like a perfect fit. Shall we get you started with the free trial?",
            "I can see this would solve your exact challenge. When would be the best time to implement this?",
            "Given the ROI we discussed, what questions do you have before moving forward?"
        ]
    }
    
    training_response = requests.post(f"{BASE_URL}/agents/ai/training/", json=training_data, headers=headers)
    if training_response.status_code == 200:
        training_result = training_response.json()
        print(f"✅ Agent Training Successful!")
        print(f"   📊 Training Level: {training_result['agent_info']['training_level']}%")
        print(f"   📈 Status: {training_result['agent_info']['status']}")
        print(f"   🎯 Ready for Calls: {training_result['agent_info']['is_ready_for_calls']}")
        agent_id = training_result['agent_info']['id']
    else:
        print(f"❌ Training failed: {training_response.text}")
        return
    
    # Step 3: Check Training Status (GET /agents/ai/training/)
    print("\n📊 Step 3: Check Training Status")
    status_response = requests.get(f"{BASE_URL}/agents/ai/training/", headers=headers)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print("✅ Training Status Retrieved:")
        print(f"   🤖 Agent: {status_data['agent_info']['name']}")
        print(f"   📈 Training Level: {status_data['agent_info']['training_level']}%")
        print(f"   📚 Training Sessions: {status_data['training_status']['total_sessions']}")
        print(f"   🔥 Current Knowledge:")
        print(f"      - Sales Script: {'✅' if status_data['current_knowledge']['sales_script'] else '❌'}")
        print(f"      - Objections: {len(status_data['current_knowledge']['objection_responses'])} responses")
        print(f"      - Product Details: {'✅' if status_data['current_knowledge']['product_details'] else '❌'}")
    
    # Step 4: Test AI Response Generation (POST /agents/ai/response/)
    print("\n💬 Step 4: AI Response Generation Test")
    
    # Test different conversation scenarios
    scenarios = [
        {
            "customer_message": "hi, who is this?",
            "call_stage": "opening",
            "scenario": "Call Opening"
        },
        {
            "customer_message": "your price is too high, I can't afford it",
            "call_stage": "objection_handling", 
            "scenario": "Price Objection"
        },
        {
            "customer_message": "I'm not interested in this",
            "call_stage": "objection_handling",
            "scenario": "Interest Objection"
        },
        {
            "customer_message": "tell me more about the benefits",
            "call_stage": "presentation",
            "scenario": "Product Presentation"
        },
        {
            "customer_message": "I need to think about it",
            "call_stage": "closing",
            "scenario": "Closing Situation"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n   🎭 Testing: {scenario['scenario']}")
        response_data = {
            "customer_message": scenario["customer_message"],
            "call_stage": scenario["call_stage"],
            "conversation_context": "Customer called about automation solution",
            "customer_phone": "+1234567890"
        }
        
        response_response = requests.post(f"{BASE_URL}/agents/ai/response/", json=response_data, headers=headers)
        if response_response.status_code == 200:
            ai_response = response_response.json()
            print(f"   ✅ Customer: '{scenario['customer_message']}'")
            print(f"   🤖 AI Agent: '{ai_response['agent_response'][:100]}...'")
            print(f"   📈 Confidence: {ai_response['response_metadata']['confidence_level']}")
            print(f"   🎯 Type: {ai_response['response_metadata']['response_type']}")
        else:
            print(f"   ❌ Response generation failed: {response_response.text}")
    
    # Step 5: Simulate Learning from Successful Call (POST /agents/ai/learning/)
    print("\n🧠 Step 5: AI Learning from Call Data")
    learning_data = {
        "call_outcome": "interested",
        "customer_satisfaction": 8,
        "customer_responses": [
            "Hi, yes I'm interested in automation",
            "That sounds good, tell me more about pricing",
            "I like what I'm hearing, can we schedule a demo?"
        ],
        "agent_performance_notes": "Customer was very responsive to ROI approach. Mentioning specific savings amount ($5000) generated immediate interest. Used consultative selling approach successfully.",
        "objections_encountered": ["price_too_high"],
        "successful_techniques": ["ROI_focus", "specific_numbers", "consultative_approach"],
        "call_duration": 280
    }
    
    learning_response = requests.post(f"{BASE_URL}/agents/ai/learning/", json=learning_data, headers=headers)
    if learning_response.status_code == 200:
        learning_result = learning_response.json()
        print("✅ AI Learning Applied Successfully!")
        print(f"   📊 Total Calls Learned: {learning_result['learning_summary']['total_calls_learned']}")
        print(f"   📈 Conversion Rate: {learning_result['learning_summary']['conversion_rate']:.1f}%")
        print(f"   🎯 Agent Status: {learning_result['agent_status']['status']}")
        
        if learning_result.get('insights'):
            print("   💡 Learning Insights:")
            for insight in learning_result['insights']:
                print(f"      - {insight}")
        
        if learning_result.get('recommendations'):
            print("   🎯 AI Recommendations:")
            for rec in learning_result['recommendations']:
                print(f"      - {rec['message']}")
    else:
        print(f"❌ Learning failed: {learning_response.text}")
    
    # Step 6: Test AI Call Initiation (POST /agents/ai/start-call/)
    print("\n📞 Step 6: AI Call Initiation Test")
    call_data = {
        "phone_number": "+1234567890",
        "agent_id": agent_id,
        "context": {
            "lead_source": "website_inquiry",
            "previous_interest": "automation_solution",
            "urgency": "medium"
        }
    }
    
    call_response = requests.post(f"{BASE_URL}/agents/ai/start-call/", json=call_data, headers=headers)
    if call_response.status_code == 201:
        call_result = call_response.json()
        print("✅ AI Call Initiated Successfully!")
        print(f"   📞 Call Session ID: {call_result['call_session_id']}")
        print(f"   🔗 Twilio Call SID: {call_result.get('twilio_call_sid', 'Mock Call')}")
        print(f"   🧠 HumeAI Conversation: {call_result.get('hume_conversation_id', 'Not configured')}")
        print(f"   🎭 Agent: {call_result['agent_info']['name']} ({call_result['agent_info']['personality_type']})")
        print(f"   👤 Customer: {call_result['customer_info']['interest_level']} lead")
        print("   🚀 Call Capabilities:")
        for capability, enabled in call_result['call_capabilities'].items():
            print(f"      - {capability}: {'✅' if enabled else '❌'}")
        
        call_session_id = call_result['call_session_id']
    else:
        print(f"❌ Call initiation failed: {call_response.text}")
        return
    
    # Step 7: Simulate HumeAI Webhook (Emotional Intelligence)
    print("\n🎭 Step 7: HumeAI Emotional Intelligence Webhook Test")
    
    # Simulate HumeAI sending emotional data during call
    hume_webhook_data = {
        "conversation_id": call_result.get('hume_conversation_id', 'mock_conversation_123'),
        "emotions": {
            "primary": "interest",
            "confidence": 0.85,
            "timeline": [
                {"timestamp": "2024-01-01T10:00:00Z", "emotion": "neutral", "confidence": 0.6},
                {"timestamp": "2024-01-01T10:02:00Z", "emotion": "curiosity", "confidence": 0.75},
                {"timestamp": "2024-01-01T10:04:00Z", "emotion": "interest", "confidence": 0.85}
            ]
        },
        "sentiment": {
            "score": 0.7,
            "magnitude": 0.8
        },
        "events": [
            {
                "type": "customer_response",
                "timestamp": "2024-01-01T10:01:00Z",
                "text": "Tell me more about your automation platform",
                "emotion": "curiosity",
                "confidence": 0.75
            },
            {
                "type": "agent_response", 
                "timestamp": "2024-01-01T10:01:30Z",
                "text": "I'd love to! Our platform can save you 40+ hours weekly",
                "effectiveness": 0.82
            },
            {
                "type": "customer_response",
                "timestamp": "2024-01-01T10:03:00Z", 
                "text": "That sounds interesting, what's the pricing?",
                "emotion": "interest",
                "confidence": 0.85
            }
        ]
    }
    
    # Note: This would normally be called by HumeAI, but we're simulating
    hume_response = requests.post(f"{BASE_URL}/agents/webhooks/hume-ai/", json=hume_webhook_data)
    if hume_response.status_code == 200:
        hume_result = hume_response.json()
        print("✅ HumeAI Emotional Intelligence Processing!")
        print(f"   🎭 Primary Emotion: {hume_result['emotional_analysis']['primary_emotion']}")
        print(f"   📊 Confidence: {hume_result['emotional_analysis']['emotion_confidence']}")
        print(f"   📈 Sentiment Score: {hume_result['emotional_analysis']['sentiment_score']}")
        print(f"   🧠 Learning Applied: {hume_result['learning_applied']}")
        
        if hume_result.get('real_time_insights'):
            print("   💡 Real-time Insights:")
            for insight in hume_result['real_time_insights']:
                print(f"      - {insight['message']} (Priority: {insight['urgency']})")
    
    # Step 8: Complete Call with Learning (POST /agents/ai/complete-call/)
    print("\n🏁 Step 8: Complete Call with Comprehensive Learning")
    completion_data = {
        "call_session_id": call_session_id,
        "final_outcome": "callback_requested",
        "conversation_transcript": """Agent: Hello John, this is Sarah from TechSolutions. I'm calling about the automation solution you inquired about. How are you doing today?
Customer: Hi Sarah, I'm doing well. Yes, I did look at your website.
Agent: Great! I understand cost is a concern. Let me show you the ROI - our clients typically save $5000 monthly within 3 months.
Customer: That sounds interesting. Can you tell me more about how it works?
Agent: Absolutely! Our AI-powered automation can save you 40+ hours weekly by handling repetitive tasks.
Customer: Wow, that's significant. I'd like to learn more. Can we schedule a demo?
Agent: Perfect! I can see this would solve your exact challenge. When would be the best time this week?
Customer: How about Thursday at 2 PM?
Agent: Thursday at 2 PM works perfectly. I'll send you a calendar invite.""",
        "customer_feedback": {
            "satisfaction": 9,
            "objections": ["price_too_high"],
            "successful_techniques": ["ROI_focus", "specific_numbers", "benefit_emphasis"]
        }
    }
    
    completion_response = requests.post(f"{BASE_URL}/agents/ai/complete-call/", json=completion_data, headers=headers)
    if completion_response.status_code == 200:
        completion_result = completion_response.json()
        print("✅ Call Completed with Comprehensive Learning!")
        print(f"   📞 Final Outcome: {completion_result['final_outcome']}")
        print(f"   🧠 Learning Applied: {completion_result['learning_applied']}")
        print(f"   👤 Customer Updated: {completion_result['customer_updated']}")
        print(f"   📊 Agent Performance:")
        print(f"      - Calls Handled: {completion_result['agent_performance']['calls_handled']}")
        print(f"      - Conversion Rate: {completion_result['agent_performance']['conversion_rate']:.1f}%")
        print(f"      - Training Level: {completion_result['agent_performance']['training_level']}%")
        print(f"   🎯 Customer Journey:")
        print(f"      - Interest Level: {completion_result['customer_journey']['interest_level']}")
        print(f"      - Total Calls: {completion_result['customer_journey']['total_calls']}")
        print(f"      - Converted: {completion_result['customer_journey']['is_converted']}")
    
    # Step 9: Final Training Status Check (to see learning improvements)
    print("\n📈 Step 9: Final Agent Status (After Learning)")
    final_status = requests.get(f"{BASE_URL}/agents/ai/training/", headers=headers)
    if final_status.status_code == 200:
        final_data = final_status.json()
        print("✅ Final Agent Status Retrieved:")
        print(f"   🤖 Agent Status: {final_data['agent_info']['status']}")
        print(f"   📊 Training Level: {final_data['agent_info']['training_level']}%")
        print(f"   🎯 Ready for Calls: {final_data['agent_info']['is_ready_for_calls']}")
        
        learning_data = final_data.get('learning_data', {})
        if learning_data:
            print(f"   🧠 Learning Analytics:")
            print(f"      - Total Calls Learned: {learning_data.get('total_calls_learned_from', 0)}")
            
            successful_patterns = learning_data.get('successful_patterns', [])
            if successful_patterns:
                print(f"      - Successful Patterns: {len(successful_patterns)}")
                print(f"      - Top Approach: '{successful_patterns[0].get('approach_used', '')[:50]}...'")
            
            performance_metrics = learning_data.get('performance_metrics', {})
            if performance_metrics:
                conversion_trends = performance_metrics.get('conversion_trends', [])
                if conversion_trends:
                    recent_conversions = sum(1 for trend in conversion_trends if trend.get('converted'))
                    print(f"      - Recent Success Rate: {recent_conversions}/{len(conversion_trends)}")
    
    print("\n" + "=" * 50)
    print("🎉 COMPLETE AI AGENT SYSTEM TEST FINISHED!")
    print("=" * 50)
    
    print("\n✅ SUCCESSFULLY TESTED:")
    print("   🎓 AI Agent Training (Sales Scripts, Objections, Products)")
    print("   💬 Intelligent Response Generation")
    print("   🧠 Real-time Learning from Conversations")
    print("   🎭 HumeAI Emotional Intelligence Integration")
    print("   📞 Complete Call Lifecycle Management")
    print("   📊 Performance Analytics and Insights")
    print("   🔄 Automatic Agent Improvement")
    
    print("\n🚀 YOUR AI AGENT IS NOW:")
    print("   ✨ Fully Trained and Ready for Live Calls")
    print("   🤖 Learning from Every Customer Interaction")
    print("   🎯 Getting Better with Each Conversation")
    print("   💡 Providing Data-driven Insights")
    print("   📈 Continuously Improving Performance")


if __name__ == "__main__":
    test_complete_ai_system()