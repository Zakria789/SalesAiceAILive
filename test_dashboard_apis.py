"""
Dashboard API Tests
===================

Quick test script to verify all dashboard endpoints work correctly.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/hume-twilio"
AUTH_TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def test_active_inbound_calls():
    """Test: Get active inbound calls"""
    print("\n" + "="*60)
    print("TEST 1: Get Active Inbound Calls")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/dashboard/inbound/active/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Active Calls: {data.get('summary', {}).get('total_active', 0)}")
        
        if data.get('active_calls'):
            print("\nFirst Call:")
            first_call = data['active_calls'][0]
            print(f"  - Call ID: {first_call.get('call_id')}")
            print(f"  - From: {first_call.get('from_number')}")
            print(f"  - Status: {first_call.get('status')}")
            print(f"  - Duration: {first_call.get('duration')}s")
            print(f"  - Agent: {first_call.get('agent', {}).get('name')}")
        else:
            print("No active calls at the moment")
    else:
        print(f"Error: {response.text}")


def test_inbound_history():
    """Test: Get inbound call history"""
    print("\n" + "="*60)
    print("TEST 2: Get Inbound Call History")
    print("="*60)
    
    # Last 30 days
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/dashboard/inbound/history/",
        params={
            'page': 1,
            'page_size': 10,
            'date_from': date_from
        },
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total Calls: {data.get('pagination', {}).get('total', 0)}")
        print(f"Page: {data.get('pagination', {}).get('page')}/{data.get('pagination', {}).get('total_pages')}")
        
        if data.get('calls'):
            print(f"\nShowing {len(data['calls'])} calls:")
            for call in data['calls'][:3]:  # Show first 3
                print(f"  - {call.get('customer_name')} ({call.get('from_number')})")
                print(f"    Status: {call.get('status')} | Duration: {call.get('duration')}s")
    else:
        print(f"Error: {response.text}")


def test_quick_call():
    """Test: Initiate quick outbound call"""
    print("\n" + "="*60)
    print("TEST 3: Quick Outbound Call")
    print("="*60)
    
    # You need to replace these with actual values
    test_data = {
        "phone_number": "+1234567890",  # Replace with test number
        "agent_id": "YOUR_AGENT_UUID",  # Replace with actual agent ID
        "customer_name": "Test Customer"
    }
    
    print(f"Calling: {test_data['phone_number']}")
    
    response = requests.post(
        f"{BASE_URL}/dashboard/outbound/quick-call/",
        json=test_data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"Call ID: {data.get('call', {}).get('call_id')}")
        print(f"Status: {data.get('call', {}).get('status')}")
    else:
        print(f"Error: {response.text}")


def test_scheduled_bulk_calls():
    """Test: Get scheduled/bulk calls"""
    print("\n" + "="*60)
    print("TEST 4: Get Scheduled/Bulk Calls")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/dashboard/outbound/scheduled/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        
        summary = data.get('summary', {})
        print("\nCall Status Summary:")
        print(f"  - Pending: {summary.get('total_pending', 0)}")
        print(f"  - Active: {summary.get('total_active', 0)}")
        print(f"  - Completed: {summary.get('total_completed', 0)}")
        print(f"  - Failed: {summary.get('total_failed', 0)}")
        
        calls_data = data.get('calls', {})
        if calls_data.get('pending'):
            print(f"\nPending calls: {len(calls_data['pending'])}")
    else:
        print(f"Error: {response.text}")


def test_outbound_history():
    """Test: Get outbound call history"""
    print("\n" + "="*60)
    print("TEST 5: Get Outbound Call History")
    print("="*60)
    
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/dashboard/outbound/history/",
        params={
            'page': 1,
            'page_size': 10,
            'date_from': date_from
        },
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total Calls: {data.get('pagination', {}).get('total', 0)}")
        
        if data.get('calls'):
            print(f"\nShowing {len(data['calls'])} calls:")
            for call in data['calls'][:3]:
                print(f"  - {call.get('customer_name')} ({call.get('to_number')})")
                print(f"    Status: {call.get('status')} | Duration: {call.get('duration')}s")
    else:
        print(f"Error: {response.text}")


def test_analytics_dashboard():
    """Test: Get analytics dashboard"""
    print("\n" + "="*60)
    print("TEST 6: Get Analytics Dashboard")
    print("="*60)
    
    date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    date_to = datetime.now().strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/dashboard/analytics/",
        params={
            'date_from': date_from,
            'date_to': date_to
        },
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        
        metrics = data.get('overall_metrics', {})
        print("\nOverall Metrics:")
        print(f"  - Total Calls: {metrics.get('total_calls', 0)}")
        print(f"  - Avg Positive Sentiment: {metrics.get('avg_positive_sentiment', 0):.2f}")
        print(f"  - Leads Qualified: {metrics.get('leads_qualified', 0)}")
        print(f"  - Appointments Booked: {metrics.get('appointments_booked', 0)}")
        print(f"  - Sales Made: {metrics.get('sales_made', 0)}")
        
        top_emotions = data.get('top_emotions', [])
        if top_emotions:
            print("\nTop 5 Emotions:")
            for emotion in top_emotions[:5]:
                print(f"  - {emotion['emotion']}: {emotion['avg_score']:.2f} ({emotion['occurrences']} times)")
        
        agent_performance = data.get('agent_performance', [])
        if agent_performance:
            print("\nAgent Performance:")
            for agent in agent_performance[:3]:
                print(f"  - {agent['agent_name']}: {agent['total_calls']} calls, {agent['sales_made']} sales")
    else:
        print(f"Error: {response.text}")


def test_bulk_csv_upload():
    """Test: Upload CSV for bulk calls"""
    print("\n" + "="*60)
    print("TEST 7: Upload Bulk Calls CSV")
    print("="*60)
    
    # Create a sample CSV content
    csv_content = """phone_number,customer_name,notes
+1234567890,John Doe,Test lead 1
+0987654321,Jane Smith,Test lead 2
+1122334455,Bob Johnson,Test lead 3"""
    
    # Save to temp file
    with open('test_bulk_calls.csv', 'w') as f:
        f.write(csv_content)
    
    # Upload
    with open('test_bulk_calls.csv', 'rb') as f:
        files = {'csv_file': f}
        data = {
            'agent_id': 'YOUR_AGENT_UUID'  # Replace with actual agent ID
        }
        
        response = requests.post(
            f"{BASE_URL}/dashboard/bulk-calls/upload/",
            files=files,
            data=data,
            headers={'Authorization': f"Bearer {AUTH_TOKEN}"}
        )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Created: {data.get('created_count')} calls")
        print(f"Errors: {data.get('error_count')}")
        
        if data.get('errors'):
            print("\nErrors:")
            for error in data['errors']:
                print(f"  - Row {error['row']}: {error['error']}")
    else:
        print(f"Error: {response.text}")
    
    # Clean up
    import os
    os.remove('test_bulk_calls.csv')


def run_all_tests():
    """Run all dashboard API tests"""
    print("\n" + "="*60)
    print("DASHBOARD API TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_active_inbound_calls,
        test_inbound_history,
        # test_quick_call,  # Commented out to avoid actual calls during testing
        test_scheduled_bulk_calls,
        test_outbound_history,
        test_analytics_dashboard,
        # test_bulk_csv_upload,  # Commented out - needs agent ID
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         Dashboard API Test Script                       ║
    ║         HumeAI + Twilio Integration                      ║
    ╚══════════════════════════════════════════════════════════╝
    
    SETUP INSTRUCTIONS:
    1. Replace AUTH_TOKEN with your actual JWT token
    2. Replace agent_id placeholders with real agent UUIDs
    3. Make sure Django server is running (python manage.py runserver)
    4. Run: python test_dashboard_apis.py
    
    """)
    
    # Ask user if ready
    ready = input("Have you updated the configuration? (y/n): ")
    if ready.lower() == 'y':
        run_all_tests()
    else:
        print("\n⚠️  Please update the configuration first:")
        print("   - AUTH_TOKEN")
        print("   - agent_id (in test_quick_call and test_bulk_csv_upload)")
        print("\nThen run the script again.")
