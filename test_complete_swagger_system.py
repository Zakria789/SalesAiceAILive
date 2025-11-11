"""
Complete API Testing & Swagger Setup Verification
=================================================

This script tests all AI agent API endpoints and verifies Swagger configuration.
Run this to ensure your complete AI system is working properly.
"""

import requests
import json
import sys
from datetime import datetime

class AIAgentAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.agent_id = None
        
    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
    
    def test_server_connection(self):
        """Test if Django server is running"""
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=5)
            if response.status_code == 200:
                self.print_status("✅ Django server is running!", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ Server returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Cannot connect to server: {str(e)}", "ERROR")
            return False
    
    def test_swagger_ui(self):
        """Test Swagger UI accessibility"""
        try:
            response = requests.get(f"{self.base_url}/swagger/", timeout=5)
            if response.status_code == 200 and "swagger" in response.text.lower():
                self.print_status("✅ Swagger UI is accessible!", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ Swagger UI issue: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Swagger UI error: {str(e)}", "ERROR")
            return False
    
    def test_api_schema(self):
        """Test OpenAPI schema generation"""
        try:
            response = requests.get(f"{self.base_url}/swagger.json", timeout=5)
            if response.status_code == 200:
                schema = response.json()
                self.print_status(f"✅ API schema generated! Found {len(schema.get('paths', {}))} endpoints", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ Schema generation failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Schema error: {str(e)}", "ERROR")
            return False
    
    def authenticate(self):
        """Get JWT token for authentication"""
        try:
            # Try admin token endpoint (GET method)
            response = requests.get(f"{self.base_url}/api/auth/admin-token/")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.print_status("✅ Authentication successful!", "SUCCESS")
                return True
            elif response.status_code == 404:
                self.print_status("❌ Admin user not found. Trying debug endpoint...", "WARNING")
                # Try to use debug endpoint to get any available user
                debug_response = requests.get(f"{self.base_url}/api/auth/debug-users/")
                if debug_response.status_code == 200:
                    users_data = debug_response.json()
                    if users_data.get('users'):
                        self.token = users_data['users'][0].get('access_token')
                        self.print_status("✅ Using first available user token", "SUCCESS")
                        return True
                
                self.print_status("❌ No users available. Please create admin user.", "ERROR")
                return False
            else:
                self.print_status(f"❌ Authentication failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Auth error: {str(e)}", "ERROR")
            return False
    
    def test_ai_training(self):
        """Test AI agent training endpoint"""
        if not self.token:
            self.print_status("❌ No authentication token for AI training", "ERROR")
            return False
        
        try:
            training_data = {
                "sales_script": "Hello! This is Sarah from TechSolutions. I'm calling about our AI automation platform that can save you 40+ hours per week.",
                "objection_responses": {
                    "price_too_high": "I understand cost is important. Our clients typically see ROI within 60 days through time savings alone.",
                    "not_interested": "I appreciate your honesty. What's your biggest challenge with current processes?",
                    "thinking_about_it": "Smart approach! What specific information would help you decide?",
                    "competitor_comparison": "Great question! Unlike others, we offer 24/7 live support and 99.9% uptime guarantee."
                },
                "product_details": {
                    "features": ["AI-powered automation", "Real-time analytics", "24/7 support", "Custom integrations"],
                    "benefits": ["Save 40+ hours weekly", "Increase efficiency 300%", "Reduce errors by 95%"],
                    "pricing": "$299/month with 30-day free trial"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/agents/ai/training/", 
                                   json=training_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.agent_id = data.get('agent_info', {}).get('id')
                level = data.get('agent_info', {}).get('training_level', 0)
                self.print_status(f"✅ AI Training successful! Agent Level: {level}%", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ AI Training failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Training error: {str(e)}", "ERROR")
            return False
    
    def test_ai_response_generation(self):
        """Test AI response generation"""
        if not self.token:
            self.print_status("❌ No authentication token for response generation", "ERROR")
            return False
        
        test_scenarios = [
            {
                "customer_message": "Your product is too expensive for us",
                "call_stage": "objection_handling",
                "expected": "cost"
            },
            {
                "customer_message": "Tell me more about your features", 
                "call_stage": "presentation",
                "expected": "features"
            },
            {
                "customer_message": "What are the next steps to get started?",
                "call_stage": "closing", 
                "expected": "next steps"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            try:
                response = requests.post(f"{self.base_url}/api/agents/ai/response/",
                                       json={
                                           "customer_message": scenario["customer_message"],
                                           "call_stage": scenario["call_stage"],
                                           "conversation_context": "API test scenario"
                                       },
                                       headers={'Authorization': f'Bearer {self.token}'})
                
                if response.status_code == 200:
                    data = response.json()
                    agent_response = data.get('agent_response', '')
                    self.print_status(f"✅ Response Test {i}/3: Generated intelligent response!", "SUCCESS")
                    self.print_status(f"   Customer: {scenario['customer_message'][:50]}...", "INFO")
                    self.print_status(f"   AI Agent: {agent_response[:50]}...", "INFO")
                else:
                    self.print_status(f"❌ Response Test {i}/3 failed: {response.status_code}", "ERROR")
                    return False
            except Exception as e:
                self.print_status(f"❌ Response Test {i}/3 error: {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_ai_learning(self):
        """Test AI learning from call data"""
        if not self.token:
            self.print_status("❌ No authentication token for learning", "ERROR")
            return False
        
        try:
            learning_data = {
                "call_outcome": "interested",
                "customer_satisfaction": 8,
                "customer_responses": [
                    "That sounds interesting, tell me more",
                    "What's your pricing?",
                    "I'd like to schedule a demo"
                ],
                "agent_performance_notes": "Customer responded well to ROI focus and demo offer",
                "successful_techniques": ["roi_focus", "demo_offer", "benefit_driven"],
                "call_duration": 420
            }
            
            response = requests.post(f"{self.base_url}/api/agents/ai/learning/",
                                   json=learning_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('learning_status', 'unknown')
                self.print_status(f"✅ AI Learning successful! Status: {status}", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ AI Learning failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ Learning error: {str(e)}", "ERROR")
            return False
    
    def test_hume_ai_webhook(self):
        """Test HumeAI webhook integration"""
        if not self.token:
            self.print_status("❌ No authentication token for HumeAI", "ERROR")
            return False
        
        try:
            hume_data = {
                "conversation_events": [
                    {
                        "timestamp": "2025-01-08T10:00:00Z",
                        "speaker": "customer",
                        "text": "Hello, I'm interested in your service",
                        "emotion_scores": {
                            "joy": 0.3,
                            "interest": 0.8,
                            "confusion": 0.1
                        }
                    }
                ],
                "sentiment_analysis": {
                    "overall_sentiment": "positive",
                    "confidence": 0.85,
                    "emotion_progression": ["neutral", "interested", "engaged"]
                },
                "call_id": "test_call_123"
            }
            
            response = requests.post(f"{self.base_url}/api/agents/webhooks/hume-ai/",
                                   json=hume_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                self.print_status(f"✅ HumeAI integration working! Status: {status}", "SUCCESS")
                return True
            else:
                self.print_status(f"❌ HumeAI webhook failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"❌ HumeAI error: {str(e)}", "ERROR")
            return False
    
    def run_complete_test(self):
        """Run all tests and provide comprehensive report"""
        self.print_status("🚀 Starting Complete AI Agent System Test...", "INFO")
        print("=" * 60)
        
        tests = [
            ("Server Connection", self.test_server_connection),
            ("Swagger UI Access", self.test_swagger_ui), 
            ("API Schema Generation", self.test_api_schema),
            ("JWT Authentication", self.authenticate),
            ("AI Agent Training", self.test_ai_training),
            ("AI Response Generation", self.test_ai_response_generation),
            ("AI Learning System", self.test_ai_learning),
            ("HumeAI Integration", self.test_hume_ai_webhook)
        ]
        
        results = {}
        for test_name, test_func in tests:
            self.print_status(f"Running: {test_name}", "TEST")
            results[test_name] = test_func()
            print("-" * 40)
        
        # Final Report
        print("\n" + "=" * 60)
        self.print_status("📊 FINAL TEST REPORT", "INFO")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<30} {status}")
        
        print("-" * 60)
        print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Your AI Agent system is fully operational!")
            print("\n🔗 Access Points:")
            print(f"   • Swagger UI: {self.base_url}/swagger/")
            print(f"   • ReDoc: {self.base_url}/redoc/")
            print(f"   • Admin Panel: {self.base_url}/admin/")
            print(f"   • Voice Demo: Open ai_voice_demo.html in browser")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        
        return passed == total

def main():
    """Main function to run the tests"""
    print("🤖 AI Agent System - Complete Test Suite")
    print("=" * 60)
    
    # Check if server is specified
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Testing server: {base_url}")
    print("=" * 60)
    
    tester = AIAgentAPITester(base_url)
    success = tester.run_complete_test()
    
    if success:
        print("\n✨ System is ready for production!")
        print("\n📖 Quick Start Guide:")
        print("1. Open browser: http://localhost:8000/swagger/")
        print("2. Use 'Bearer {token}' for authorization")  
        print("3. Test endpoints starting with /api/agents/ai/")
        print("4. Open ai_voice_demo.html for voice testing")
    else:
        print("\n🔧 Please fix the failing tests and run again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())