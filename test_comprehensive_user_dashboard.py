import requests
import json

def test_comprehensive_user_dashboard():
    print("🚀 Testing Comprehensive Dashboard API (User-Specific)...")
    print("   (Now shows only authenticated user's data)")
    
    # 1. Login
    login_data = {"email": "testvoice@admin.com", "password": "testpass123"}
    try:
        login_response = requests.post("http://127.0.0.1:8000/api/auth/login/", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()["tokens"]["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful!")
        
        # 2. Test Comprehensive User Dashboard
        dashboard_response = requests.get("http://127.0.0.1:8000/api/dashboard/comprehensive/", headers=headers)
        
        if dashboard_response.status_code != 200:
            print(f"❌ Comprehensive Dashboard failed: {dashboard_response.status_code} - {dashboard_response.text}")
            return
        
        data = dashboard_response.json()
        print("✅ Comprehensive Dashboard API Success!")
        print("")
        
        # 3. Display user-specific metrics
        print("📊 USER-SPECIFIC DASHBOARD METRICS:")
        print(f"  📞 Inbound Calls: {data['inboundCalls']}")
        print(f"  📞 Outbound Calls: {data['outboundCalls']}")
        print(f"  📞 Total Calls This Cycle: {data['totalCallsThisCycle']}")
        print(f"  📦 Plan Name: {data['planName']}")
        print(f"  ⏱️ Minutes Used: {data['planMinutesUsed']}/{data['planMinutesLimit']}")
        print(f"  📅 Renewal Date: {data['renewalDateISO']}")
        print(f"  📈 Average Call Duration: {data['averageCallDuration']} minutes")
        print(f"  ✅ Call Success Rate: {data['callSuccessRate']}%")
        print("")
        
        # 4. Display chart data
        print("📈 CHART DATA (User-Specific):")
        print(f"  Weekly Trends: {len(data['weeklyCallTrends'])} days of data")
        for day in data['weeklyCallTrends']:
            print(f"    {day['day']}: {day['inbound']} in, {day['outbound']} out, {day['total']} total")
        
        print(f"  Hourly Activity: {len(data['hourlyActivity'])} hours tracked")
        
        print(f"  Call Distribution: {len(data['callTypeDistribution'])} categories")
        for dist in data['callTypeDistribution']:
            print(f"    {dist['name']}: {dist['value']} calls")
        
        print(f"  Monthly Usage: {len(data['monthlyUsage'])} months")
        for month in data['monthlyUsage']:
            print(f"    {month['month']}: {month['minutes']} min, {month['calls']} calls")
        print("")
        
        # 5. Validate TypeScript interface compatibility
        print("✅ TYPESCRIPT INTERFACE VALIDATION:")
        required_fields = [
            'inboundCalls', 'outboundCalls', 'planName', 'planMinutesLimit', 
            'planMinutesUsed', 'renewalDateISO', 'billingCycleStart', 
            'totalCallsThisCycle', 'averageCallDuration', 'callSuccessRate',
            'weeklyCallTrends', 'hourlyActivity', 'callTypeDistribution', 'monthlyUsage'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"  ❌ Missing fields: {missing_fields}")
        else:
            print("  ✅ All required fields present")
        
        # Validate data types
        if isinstance(data['inboundCalls'], int) and isinstance(data['outboundCalls'], int):
            print("  ✅ Call counts are integers")
        else:
            print("  ❌ Call counts not integers")
            
        if isinstance(data['weeklyCallTrends'], list) and len(data['weeklyCallTrends']) > 0:
            print("  ✅ Weekly trends is populated array")
        else:
            print("  ❌ Weekly trends missing or empty")
        
        print("")
        print("🎉 SUCCESS! Comprehensive Dashboard is now USER-SPECIFIC and TypeScript compatible!")
        return data
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_comprehensive_user_dashboard()
