import pyttsx3
import requests
import json
import time
import threading
from datetime import datetime

# Voice Demo System for AI Agent
# Test agent voice responses in real-time

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "admin@gmail.com"
TEST_USER_PASSWORD = "admin123"

class VoiceAIDemo:
    def __init__(self):
        # Initialize Text-to-Speech
        self.tts_engine = pyttsx3.init()
        
        # Configure voice settings
        voices = self.tts_engine.getProperty('voices')
        
        # Try to set female voice
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 160)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
        
        # Agent authentication
        self.headers = None
        self.agent_id = None
        
    def speak(self, text, prefix="🤖 AI Agent"):
        """Convert text to speech"""
        print(f"\n{prefix}: {text}")
        print("🔊 Playing voice...")
        
        # Speak in separate thread to avoid blocking
        def speak_text():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        speech_thread = threading.Thread(target=speak_text)
        speech_thread.start()
        speech_thread.join()  # Wait for speech to complete
        
    def authenticate(self):
        """Login and get authentication token"""
        print("🔐 Authenticating with AI system...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/accounts/login/", json=login_data)
            if response.status_code == 200:
                token = response.json().get('access_token')
                self.headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                print("✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def train_agent(self):
        """Train the AI agent with voice confirmation"""
        print("\n🎓 Training AI Agent...")
        
        training_data = {
            "sales_script": "Hello, this is Sarah from TechSolutions. I'm calling because you expressed interest in our AI automation platform. How are you doing today?",
            "objection_responses": {
                "price_too_high": "I understand cost is a concern. Let me show you the ROI - our clients typically save five thousand dollars monthly within three months.",
                "not_interested": "I appreciate your honesty. Can I ask what your main challenge is with current processes?",
                "thinking_about_it": "That's smart to consider carefully. What specific information would help you make the decision?",
                "need_more_time": "Absolutely, I understand this is an important decision. How about I follow up with you next week?"
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
                "pricing": "Two hundred ninety nine dollars per month with 30-day free trial"
            },
            "conversation_starters": [
                "Hi there! Hope you're having a great day! I'm calling about the automation solution you inquired about.",
                "Hello! This is Sarah from TechSolutions. Do you have 2 minutes to discuss how we can save you time?",
                "Hi! I noticed you downloaded our guide. I'd love to show you how it applies to your business."
            ]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/agents/ai/training/", json=training_data, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                self.agent_id = result['agent_info']['id']
                
                self.speak("Training completed successfully! I'm now ready to handle customer conversations.", "✅ AI Agent")
                print(f"📊 Training Level: {result['agent_info']['training_level']}%")
                print(f"🎯 Agent Status: {result['agent_info']['status']}")
                return True
            else:
                print(f"❌ Training failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Training error: {str(e)}")
            return False
    
    def get_ai_response(self, customer_message, call_stage="general"):
        """Get AI response and speak it"""
        print(f"\n👤 Customer: {customer_message}")
        
        request_data = {
            "customer_message": customer_message,
            "call_stage": call_stage,
            "conversation_context": "Customer inquiry about automation solution",
            "customer_phone": "+1234567890"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/agents/ai/response/", json=request_data, headers=self.headers)
            if response.status_code == 200:
                ai_data = response.json()
                agent_response = ai_data['agent_response']
                
                # Speak the response
                self.speak(agent_response)
                
                # Show metadata
                metadata = ai_data['response_metadata']
                print(f"📈 Confidence: {metadata['confidence_level']}")
                print(f"🎯 Response Type: {metadata['response_type']}")
                
                if ai_data.get('follow_up_suggestions'):
                    print("💡 Follow-up Suggestions:")
                    for suggestion in ai_data['follow_up_suggestions']:
                        print(f"   - {suggestion}")
                
                return agent_response
            else:
                print(f"❌ Response generation failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Response error: {str(e)}")
            return None
    
    def simulate_conversation(self):
        """Simulate a complete conversation with voice"""
        print("\n🎭 STARTING LIVE CONVERSATION DEMO")
        print("=" * 50)
        
        conversation_scenarios = [
            {
                "customer": "Hello, who is this?",
                "stage": "opening",
                "description": "Call Opening"
            },
            {
                "customer": "I'm interested but your price seems too high",
                "stage": "objection_handling", 
                "description": "Price Objection"
            },
            {
                "customer": "What are the main benefits of your platform?",
                "stage": "presentation",
                "description": "Product Benefits"
            },
            {
                "customer": "I need to think about it and discuss with my team",
                "stage": "objection_handling",
                "description": "Think It Over Objection"
            },
            {
                "customer": "This sounds good, what are the next steps?",
                "stage": "closing",
                "description": "Closing Opportunity"
            }
        ]
        
        for i, scenario in enumerate(conversation_scenarios, 1):
            print(f"\n🎬 Scenario {i}: {scenario['description']}")
            print("-" * 30)
            
            # Get and speak AI response
            response = self.get_ai_response(scenario["customer"], scenario["stage"])
            
            if response:
                # Pause between scenarios
                time.sleep(2)
                print("\n⏳ Moving to next scenario...\n")
                time.sleep(1)
    
    def interactive_demo(self):
        """Interactive voice demo where user can type customer messages"""
        print("\n🎙️ INTERACTIVE VOICE DEMO")
        print("=" * 50)
        print("💡 Type customer messages and hear AI agent responses!")
        print("💡 Type 'quit' to exit, 'help' for suggestions")
        
        self.speak("Hello! I'm your AI agent. I'm ready to demonstrate live conversations. What would you like the customer to say?", "🤖 Demo")
        
        while True:
            print("\n" + "-" * 50)
            customer_input = input("👤 Customer says: ").strip()
            
            if customer_input.lower() == 'quit':
                self.speak("Thank you for testing my capabilities! Goodbye!", "🤖 AI Agent")
                break
            elif customer_input.lower() == 'help':
                suggestions = [
                    "Hello, what do you offer?",
                    "Your price is too expensive",
                    "I'm not interested",
                    "Tell me more about benefits",
                    "I need to think about it",
                    "What's your best price?",
                    "How does this compare to competitors?"
                ]
                print("\n💡 Try these customer messages:")
                for suggestion in suggestions:
                    print(f"   - {suggestion}")
                continue
            elif not customer_input:
                print("💬 Please enter a customer message...")
                continue
            
            # Determine call stage based on message content
            message_lower = customer_input.lower()
            if any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap']):
                stage = "objection_handling"
            elif any(word in message_lower for word in ['benefits', 'features', 'tell me more']):
                stage = "presentation"  
            elif any(word in message_lower for word in ['not interested', 'no thanks', 'not now']):
                stage = "objection_handling"
            elif any(word in message_lower for word in ['ready', 'next steps', 'sign up', 'proceed']):
                stage = "closing"
            else:
                stage = "general"
            
            # Get AI response and speak it
            self.get_ai_response(customer_input, stage)
    
    def run_complete_demo(self):
        """Run complete voice demo"""
        print("🎤 VOICE AI AGENT DEMO SYSTEM")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return
        
        # Step 2: Train agent
        if not self.train_agent():
            return
        
        # Step 3: Voice capabilities demo
        self.speak("Welcome to the AI Agent voice demonstration! I can now handle live conversations with customers.", "🎉 System")
        
        while True:
            print("\n🎯 DEMO OPTIONS:")
            print("1. 🎬 Simulated Conversation (Pre-scripted scenarios)")
            print("2. 🎙️ Interactive Demo (Type your own customer messages)")
            print("3. 🔊 Voice Settings Test")
            print("4. ❌ Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.simulate_conversation()
            elif choice == "2":
                self.interactive_demo()
            elif choice == "3":
                self.test_voice_settings()
            elif choice == "4":
                self.speak("Thank you for testing the AI Agent voice system! Goodbye!", "🤖 System")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def test_voice_settings(self):
        """Test different voice settings"""
        print("\n🔊 VOICE SETTINGS TEST")
        
        test_phrases = [
            "Hello! This is your AI sales agent speaking.",
            "I understand cost is a concern. Let me explain the return on investment.",
            "Our platform can save you five thousand dollars monthly within three months.",
            "Thank you for your time. I look forward to helping your business grow."
        ]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n🎵 Test Phrase {i}:")
            self.speak(phrase, "🔊 Voice Test")
            time.sleep(1)


if __name__ == "__main__":
    # Install required package if not available
    try:
        import pyttsx3
    except ImportError:
        print("❌ pyttsx3 not found. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "pyttsx3"])
        import pyttsx3
    
    demo = VoiceAIDemo()
    demo.run_complete_demo()