"""
Test /api/agents/create/ API Endpoint
Mimics exact frontend API call
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8002"
API_ENDPOINT = f"{BASE_URL}/api/agents/create/"

# Get JWT token first (replace with your actual token or login)
def get_jwt_token():
    """Get JWT token from quick-token endpoint"""
    login_url = f"{BASE_URL}/api/auth/quick-token/"
    
    # Use your actual credentials
    credentials = {
        "email": "admin@gmail.com",  # Change this to your email
        "password": "admin123"  # Change this to your password
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_create_agent_api():
    """Test agent creation via API"""
    
    print("\n" + "="*80)
    print("🧪 TESTING /api/agents/create/ API ENDPOINT")
    print("="*80)
    
    # Step 1: Get JWT token
    print(f"\n🔹 STEP 1: Getting JWT token...")
    token = get_jwt_token()
    
    if not token:
        print("❌ Cannot proceed without token")
        print("\n💡 Please update credentials in the script:")
        print("   Line 19: email")
        print("   Line 20: password")
        return
    
    print(f"✅ Token received: {token[:50]}...")
    
    # Step 2: Prepare payload (exact frontend format)
    print(f"\n🔹 STEP 2: Preparing payload...")
    
    payload = {
        "name": "Live Test Agent",
        "agent_type": "outbound",
        "status": "active",
        "voice_tone": "enthusiastic",
        "api_key_source": "account_default",
        "hume_ai_config": {
            "enable_emotion_detection": True,
            "response_to_emotions": True,
            "sentiment_analysis": True,
            "emotion_models": ["prosody", "language"]
        },
        "sales_script_text": """STEP 1: Warm Introduction
Hello! This is [Your Name] calling from Coding The Brains. How are you doing today?

We specialize in AI and automation solutions that help businesses streamline operations and boost efficiency.

STEP 2: Value Proposition
Our AI automation services are designed to help businesses like yours:
• Reduce manual work by 70%
• Improve customer response time
• Scale operations without hiring more staff
• Get real-time insights from your data

STEP 3: Discovery Question
What's your biggest challenge right now when it comes to managing customer interactions?

STEP 4: Solution Presentation
Based on what you've shared, our AI chatbots and automation tools can specifically help you by:
• Handling customer queries 24/7
• Automating repetitive tasks
• Providing detailed analytics

STEP 5: Call to Action
I'd love to show you a quick 15-minute demo. Are you available this Thursday or Friday afternoon?""",
        "business_info": {
            "company_name": "Coding The Brains",
            "company_website": "https://www.codingthebrains.com/",
            "industry": "AI and Automation Services",
            "business_description": "We deliver cutting-edge AI and Machine Learning solutions to help businesses automate processes, predict trends, and make data-driven decisions.",
            "product_features": [
                "AI Chatbot Development",
                "Machine Learning Solutions",
                "Data Science & Analytics",
                "Computer Vision Systems",
                "IoT Integration",
                "Deep Learning Models"
            ],
            "pricing_info": "Custom pricing based on business needs. Packages start from $2,000/month.",
            "target_customers": "SMBs and enterprises looking to leverage AI for business growth"
        },
        "operating_hours": {
            "start": "09:00",
            "end": "17:00",
            "timezone": "UTC",
            "working_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        },
        "auto_answer_enabled": False,
        "website_url": "https://www.codingthebrains.com/",
        "campaign_schedule": {
            "name": "Test Campaign",
            "type": "immediate",
            "start_date": "",
            "max_calls_per_day": 100
        }
    }
    
    print(f"✅ Payload prepared:")
    print(f"   Name: {payload['name']}")
    print(f"   Type: {payload['agent_type']}")
    print(f"   Sales Script: {len(payload['sales_script_text'])} chars")
    print(f"   Business Info: {len(json.dumps(payload['business_info']))} chars")
    print(f"   Company: {payload['business_info']['company_name']}")
    
    # Step 3: Make API call
    print(f"\n🔹 STEP 3: Calling API...")
    print(f"   URL: {API_ENDPOINT}")
    print(f"   Method: POST")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response received:")
        print(f"   Status Code: {response.status_code}")
        
        # Parse response
        try:
            response_data = response.json()
            print(f"   Response JSON:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"   Response Text: {response.text}")
        
        # Check success
        if response.status_code == 201:
            print(f"\n✅ AGENT CREATED SUCCESSFULLY!")
            
            if 'agent' in response_data:
                agent_data = response_data['agent']
                print(f"\n📋 Agent Details:")
                print(f"   ID: {agent_data.get('id', 'N/A')}")
                print(f"   Name: {agent_data.get('name', 'N/A')}")
                print(f"   Type: {agent_data.get('agent_type', 'N/A')}")
                print(f"   Status: {agent_data.get('status', 'N/A')}")
                print(f"   HumeAI Config ID: {agent_data.get('hume_config_id', '❌ Not synced')}")
                print(f"   Sales Script Length: {len(agent_data.get('sales_script_text', ''))} chars")
                
                # Check if sales script was saved
                if agent_data.get('sales_script_text'):
                    print(f"\n✅ Sales Script SAVED in database!")
                    print(f"   Preview (first 150 chars):")
                    print(f"   {agent_data['sales_script_text'][:150]}...")
                else:
                    print(f"\n❌ Sales Script NOT saved!")
                
                # Check business info
                if agent_data.get('business_info'):
                    print(f"\n✅ Business Info SAVED in database!")
                    biz = agent_data['business_info']
                    if isinstance(biz, dict):
                        print(f"   Company: {biz.get('company_name', 'N/A')}")
                        print(f"   Website: {biz.get('company_website', 'N/A')}")
                        print(f"   Industry: {biz.get('industry', 'N/A')}")
                else:
                    print(f"\n❌ Business Info NOT saved!")
                
                # Check HumeAI sync status
                hume_synced = response_data.get('hume_synced')
                if hume_synced:
                    print(f"\n✅ HUMEAI SYNC SUCCESSFUL!")
                    print(f"   Config ID: {agent_data.get('hume_config_id')}")
                    print(f"\n🌐 View in HumeAI Dashboard:")
                    print(f"   https://platform.hume.ai/")
                else:
                    print(f"\n⚠️  HumeAI sync status: {hume_synced}")
                
        elif response.status_code == 400:
            print(f"\n❌ VALIDATION ERROR")
            if 'errors' in response_data:
                print(f"\n   Errors:")
                for field, errors in response_data.get('errors', {}).items():
                    print(f"   - {field}: {errors}")
        else:
            print(f"\n❌ API CALL FAILED")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout after 30 seconds")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the server running?")
        print(f"\n💡 Start the server with:")
        print(f"   daphne -b 0.0.0.0 -p 8002 core.asgi:application")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    print("🚀 Starting API Test...")
    print("\n⚠️  REQUIREMENTS:")
    print("   1. Django server must be running on port 8002")
    print("   2. Update credentials in script (lines 19-20)")
    print("   3. Ensure /api/token/ endpoint is working")
    
    input("\nPress Enter to continue...")
    
    test_create_agent_api()
