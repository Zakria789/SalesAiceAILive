#!/usr/bin/env python
"""
Test the new auto-call scheduling APIs
"""
import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000/agents"

def test_auto_call_apis():
    """Test all the new auto-call scheduling APIs"""
    
    print("🚀 Testing Auto-Call Scheduling APIs")
    print("=" * 50)
    
    # Test data
    headers = {
        'Content-Type': 'application/json',
        # Add JWT token here if authentication is enabled
        # 'Authorization': 'Bearer your_jwt_token'
    }
    
    # 1. Test Campaign Creation
    print("📝 1. Creating Auto-Call Campaign...")
    campaign_data = {
        "campaign_name": f"Test Auto-Schedule {datetime.now().strftime('%H:%M:%S')}",
        "campaign_type": "sales",
        "calls_per_hour": 6,
        "working_hours_start": "09:00",
        "working_hours_end": "18:00",
        "target_customers": 5,
        "immediate_calls": 1,
        "customer_filters": {
            "interest_levels": ["warm", "hot"],
            "max_customers": 5
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auto-calls/", 
                               json=campaign_data, 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code == 201:
            campaign_result = response.json()
            campaign_id = campaign_result.get('campaign_id')
            print(f"✅ Campaign created: {campaign_result['campaign_name']}")
            print(f"   ID: {campaign_id}")
            print(f"   Contacts: {campaign_result['contacts_added']}")
            
            # 2. Test Schedule Status
            print(f"\n📅 2. Getting Campaign Schedule...")
            schedule_response = requests.get(f"{BASE_URL}/schedule/{campaign_id}/", 
                                           headers=headers, timeout=10)
            
            if schedule_response.status_code == 200:
                schedule_data = schedule_response.json()
                print("✅ Schedule status retrieved")
                print(f"   Status: {schedule_data['campaign']['status']}")
                print(f"   Pending calls: {schedule_data['statistics']['pending_calls']}")
                print(f"   Auto-scheduling: {schedule_data['auto_scheduling_active']}")
            else:
                print(f"❌ Schedule status failed: {schedule_response.status_code}")
            
            # 3. Test Manual Schedule Control
            print(f"\n⚡ 3. Testing Manual Schedule Control...")
            control_data = {
                "action": "schedule_now",
                "campaign_id": campaign_id,
                "count": 2
            }
            
            control_response = requests.post(f"{BASE_URL}/schedule/control/", 
                                           json=control_data, 
                                           headers=headers, timeout=10)
            
            if control_response.status_code == 200:
                control_result = control_response.json()
                print("✅ Manual scheduling successful")
                print(f"   Scheduled calls: {len(control_result.get('scheduled_calls', []))}")
            else:
                print(f"❌ Manual scheduling failed: {control_response.status_code}")
            
            # 4. Test Real-time Auto Scheduler
            print(f"\n🔄 4. Testing Real-time Auto Scheduler...")
            auto_response = requests.post(f"{BASE_URL}/auto-scheduler/", 
                                        headers=headers, timeout=10)
            
            if auto_response.status_code == 200:
                auto_result = auto_response.json()
                print("✅ Auto-scheduler executed")
                print(f"   Campaigns processed: {auto_result['total_campaigns_processed']}")
            else:
                print(f"❌ Auto-scheduler failed: {auto_response.status_code}")
            
            # 5. Test Campaign Update
            print(f"\n🔧 5. Testing Campaign Update...")
            update_data = {
                "calls_per_hour": 10,
                "status": "active"
            }
            
            update_response = requests.put(f"{BASE_URL}/auto-calls/{campaign_id}/", 
                                         json=update_data, 
                                         headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                print("✅ Campaign updated successfully")
                print(f"   New calls per hour: 10")
            else:
                print(f"❌ Campaign update failed: {update_response.status_code}")
            
        else:
            print(f"❌ Campaign creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request failed: {e}")
        print("   Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Auto-Call API Testing Complete!")
    print("\nAvailable Endpoints:")
    print("  POST /agents/auto-calls/           - Create campaign")
    print("  GET  /agents/schedule/             - List all campaigns")  
    print("  GET  /agents/schedule/{id}/        - Get campaign details")
    print("  POST /agents/schedule/control/     - Manual schedule control")
    print("  POST /agents/auto-scheduler/       - Trigger auto-scheduling")
    print("  PUT  /agents/auto-calls/{id}/      - Update campaign")
    print("  DELETE /agents/auto-calls/{id}/    - Stop campaign")

if __name__ == "__main__":
    test_auto_call_apis()