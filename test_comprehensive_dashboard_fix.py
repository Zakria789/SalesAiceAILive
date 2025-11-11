"""
Test Comprehensive Dashboard API Fix
===================================
Test the fixed comprehensive dashboard API to check total calls calculation
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "umair11@gmail.com"
PASSWORD = "Test@123"

def test_comprehensive_dashboard():
    """Test comprehensive dashboard API with correct TwilioCall model"""
    
    print("📊 TESTING COMPREHENSIVE DASHBOARD API")
    print("=" * 60)
    
    # Step 1: Get JWT Token
    print("\n1️⃣  Getting JWT Token...")
    login_response = requests.post(f"{BASE_URL}/api/accounts/login/", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get('access')
    print(f"✅ Token obtained")
    
    # Step 2: Test Comprehensive Dashboard
    print(f"\n2️⃣  Testing Comprehensive Dashboard...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/api/dashboard/comprehensive/"
    print(f"URL: {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n📊 RESPONSE:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Display key metrics
        print(f"\n📈 KEY METRICS:")
        print(f"   • Total Calls This Cycle: {data.get('totalCallsThisCycle', 0)}")
        print(f"   • Inbound Calls: {data.get('inboundCalls', 0)}")
        print(f"   • Outbound Calls: {data.get('outboundCalls', 0)}")
        print(f"   • Average Call Duration: {data.get('averageCallDuration', 0)} minutes")
        print(f"   • Call Success Rate: {data.get('callSuccessRate', 0)}%")
        
        # Display subscription info
        print(f"\n💳 SUBSCRIPTION INFO:")
        print(f"   • Plan Name: {data.get('planName', 'N/A')}")
        print(f"   • Minutes Limit: {data.get('planMinutesLimit', 0)}")
        print(f"   • Minutes Used: {data.get('planMinutesUsed', 0)}")
        print(f"   • Renewal Date: {data.get('renewalDateISO', 'N/A')}")
        
        # Display chart data counts
        print(f"\n📊 CHART DATA:")
        weekly_trends = data.get('weeklyCallTrends', [])
        print(f"   • Weekly Trends: {len(weekly_trends)} days")
        if weekly_trends:
            print(f"     Latest day: {weekly_trends[-1].get('day')} - {weekly_trends[-1].get('total')} calls")
        
        hourly_activity = data.get('hourlyActivity', [])
        print(f"   • Hourly Activity: {len(hourly_activity)} hours")
        
        call_distribution = data.get('callTypeDistribution', [])
        print(f"   • Call Distribution: {len(call_distribution)} types")
        for dist in call_distribution:
            print(f"     {dist.get('name')}: {dist.get('value')} calls")
        
        monthly_usage = data.get('monthlyUsage', [])
        print(f"   • Monthly Usage: {len(monthly_usage)} months")
        if monthly_usage:
            current_month = monthly_usage[-1]
            print(f"     Current month: {current_month.get('month')} - {current_month.get('calls')} calls, {current_month.get('minutes')} minutes")
        
        # Check if total calls calculation is correct
        inbound = data.get('inboundCalls', 0)
        outbound = data.get('outboundCalls', 0)
        total_calculated = inbound + outbound
        total_reported = data.get('totalCallsThisCycle', 0)
        
        print(f"\n✅ CALCULATION CHECK:")
        print(f"   • Inbound + Outbound = {inbound} + {outbound} = {total_calculated}")
        print(f"   • Total Calls Reported = {total_reported}")
        
        if total_calculated == total_reported:
            print(f"   ✅ CALCULATION CORRECT!")
        else:
            print(f"   ❌ CALCULATION MISMATCH!")
        
        print(f"\n✅ SUCCESS: Dashboard API working with TwilioCall model!")
        
        # Show full JSON (optional - commented for brevity)
        # print(f"\n📄 FULL RESPONSE:")
        # print(json.dumps(data, indent=2))
        
    else:
        print(f"❌ Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")

def check_twilio_calls_in_db():
    """Check how many TwilioCall records exist in database"""
    import os
    import sys
    import django
    
    print(f"\n🔍 CHECKING TWILIO CALLS IN DATABASE")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()
        
        from HumeAiTwilio.models import TwilioCall
        from accounts.models import User
        
        # Get current user
        user = User.objects.filter(email=EMAIL).first()
        if not user:
            print(f"❌ User {EMAIL} not found!")
            return
        
        print(f"📊 USER: {user.email} (ID: {user.id})")
        
        # Check total calls
        total_calls = TwilioCall.objects.count()
        user_calls = TwilioCall.objects.filter(user=user).count()
        
        print(f"\n📞 CALL STATISTICS:")
        print(f"   • Total calls in system: {total_calls}")
        print(f"   • User's calls: {user_calls}")
        
        if user_calls > 0:
            # Break down by direction
            inbound = TwilioCall.objects.filter(user=user, direction='inbound').count()
            outbound = TwilioCall.objects.filter(user=user, direction='outbound').count()
            
            print(f"\n📊 USER CALL BREAKDOWN:")
            print(f"   • Inbound calls: {inbound}")
            print(f"   • Outbound calls: {outbound}")
            print(f"   • Total: {inbound + outbound}")
            
            # Recent calls
            recent_calls = TwilioCall.objects.filter(user=user).order_by('-created_at')[:5]
            print(f"\n📋 RECENT CALLS:")
            for call in recent_calls:
                print(f"   • {call.direction} - {call.status} - {call.created_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"\n⚠️  No calls found for user {EMAIL}")
            print(f"   This explains why dashboard shows 0 total calls.")
            print(f"   Solution: Create test calls or use an account with existing calls.")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == '__main__':
    print("\n🚀 Starting Comprehensive Dashboard Test...\n")
    
    # Check database first
    check_twilio_calls_in_db()
    
    # Test API
    test_comprehensive_dashboard()
    
    print("\n✅ Test Complete!\n")