import requests
import json

def test_comprehensive_dashboard():
    print("🚀 Testing Comprehensive Dashboard API...")
    print("   (All dashboard data in one API)")
    
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
        
        # 2. Test Comprehensive Dashboard
        dashboard_response = requests.get("http://127.0.0.1:8000/api/dashboard/comprehensive/", headers=headers)
        
        if dashboard_response.status_code != 200:
            print(f"❌ Comprehensive Dashboard failed: {dashboard_response.status_code} - {dashboard_response.text}")
            return
        
        data = dashboard_response.json()
        print("✅ Comprehensive Dashboard API Success!")
        print("")
        
        # 3. Display available sections
        print("📊 COMPREHENSIVE DASHBOARD SECTIONS:")
        for section_key in data.keys():
            section_data = data[section_key]
            if isinstance(section_data, dict):
                print(f"  📁 {section_key.upper().replace('_', ' ')}: {len(section_data)} items")
            elif isinstance(section_data, list):
                print(f"  📁 {section_key.upper().replace('_', ' ')}: {len(section_data)} items")
            else:
                print(f"  📁 {section_key.upper().replace('_', ' ')}: {section_data}")
        print("")
        
        # 4. Show key metrics if available
        if 'dashboard_summary' in data:
            summary = data['dashboard_summary']
            print("🎯 DASHBOARD SUMMARY:")
            for key, value in summary.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print("")
        
        print("🎉 COMPREHENSIVE DASHBOARD: All sections loaded successfully!")
        print(f"📊 Total API Response Size: ~{len(json.dumps(data))} characters")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_comprehensive_dashboard()
