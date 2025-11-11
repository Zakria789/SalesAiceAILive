import requests
import json

def test_admin_dashboard():
    print("🚀 Testing Admin Dashboard API...")
    
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
        
        # 2. Test Admin Dashboard
        admin_response = requests.get("http://127.0.0.1:8000/api/accounts/admin/dashboard/", headers=headers)
        
        if admin_response.status_code != 200:
            print(f"❌ Admin Dashboard failed: {admin_response.status_code} - {admin_response.text}")
            return
        
        data = admin_response.json()
        print("✅ Admin Dashboard API Success!")
        print("")
        
        # 3. Validate TypeScript Interface
        print("📊 METRICS:")
        metrics = data["metrics"]
        print(f"  Total Users: {metrics['totalUsers']}")
        print(f"  Active Users: {metrics['activeUsers']}")
        print(f"  Total Packages: {metrics['totalPackages']}")
        print(f"  MRR USD: ${metrics['mrrUsd']}")
        print(f"  Calls Today: {metrics['callsToday']}")
        print(f"  Churn Rate: {metrics['churnRatePct']}%")
        print("")
        
        print("📈 TRENDS:")
        trends = data["trends"]
        print(f"  MRR Points: {len(trends['mrr'])}")
        print(f"  Calls Points: {len(trends['calls'])}")
        print(f"  Users Points: {len(trends['users'])}")
        print("")
        
        print(f"👥 RECENT USERS: {len(data['recentUsers'])} users")
        if data["recentUsers"]:
            user = data["recentUsers"][0]
            print(f"  Sample User: {user['name']} ({user['email']}) - {user['role']}")
        print("")
        
        print(f"📦 TOP PACKAGES: {len(data['topPackages'])} packages")
        if data["topPackages"]:
            package = data["topPackages"][0]
            print(f"  Sample Package: {package['name']} - ${package['price_monthly']}/month - {package['subscribers']} subscribers")
        print("")
        
        # 4. Validate TypeScript Interface Match
        print("✅ TypeScript Interface Validation:")
        required_fields = {
            "metrics": ["totalUsers", "activeUsers", "totalPackages", "mrrUsd", "callsToday", "churnRatePct"],
            "trends": ["mrr", "calls", "users"],
            "recentUsers": [],
            "topPackages": []
        }
        
        all_valid = True
        for section, fields in required_fields.items():
            if section not in data:
                print(f"  ❌ Missing section: {section}")
                all_valid = False
            else:
                if fields:  # Check fields in section
                    for field in fields:
                        if field not in data[section]:
                            print(f"  ❌ Missing field: {section}.{field}")
                            all_valid = False
                        else:
                            print(f"  ✓ {section}.{field}")
                else:  # Check if it's an array
                    if isinstance(data[section], list):
                        print(f"  ✓ {section} (array with {len(data[section])} items)")
                    else:
                        print(f"  ❌ {section} should be an array")
                        all_valid = False
        
        if all_valid:
            print("\n🎉 PERFECT! API response matches TypeScript interface exactly!")
        else:
            print("\n⚠️ Some fields don't match the TypeScript interface")
            
        return data
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_admin_dashboard()
