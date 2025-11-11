"""
🎯 CLARIFIES System - Quick Verification Script
Verify all components are in place and working
"""

import os
import sys

def check_file(path, label):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {label}: {path}")
    return exists

def main():
    print("\n" + "="*70)
    print("🔍 CLARIFIES SYSTEM - VERIFICATION CHECK")
    print("="*70 + "\n")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(base_path, "sales_aice-main", "sales_aice-main")
    
    # Backend Files
    print("📦 BACKEND FILES:")
    print("-" * 70)
    backend_files = [
        ("HumeAiTwilio/services/__init__.py", "Services Package Init"),
        ("HumeAiTwilio/services/clarifies_processor.py", "CLARIFIES Processor"),
        ("HumeAiTwilio/services/risk_filter.py", "Risk Filter"),
        ("HumeAiTwilio/api_views/analytics_views.py", "Analytics APIs"),
        ("test_clarifies_system.py", "Test Script"),
    ]
    
    backend_count = 0
    for file_path, label in backend_files:
        full_path = os.path.join(base_path, file_path)
        if check_file(full_path, label):
            backend_count += 1
    
    # Frontend Files
    print("\n🎨 FRONTEND FILES:")
    print("-" * 70)
    frontend_files = [
        ("app/analytics/conversation/page.tsx", "Analytics Dashboard"),
        ("app/calls/[callId]/explainability/page.tsx", "Explainability Panel"),
        ("app/admin/risk-flags/page.tsx", "Risk Flags Admin"),
        ("components/Nav.tsx", "Navigation Component"),
    ]
    
    frontend_count = 0
    for file_path, label in frontend_files:
        full_path = os.path.join(frontend_path, file_path)
        if check_file(full_path, label):
            frontend_count += 1
    
    # Documentation Files
    print("\n📚 DOCUMENTATION:")
    print("-" * 70)
    doc_files = [
        ("CLARIFIES_SYSTEM_COMPLETE_GUIDE.md", "Backend Guide"),
        ("CLARIFIES_FRONTEND_COMPLETE.md", "Frontend Guide"),
        ("CLARIFIES_COMPLETE_SUMMARY.md", "Complete Summary"),
    ]
    
    doc_count = 0
    for file_path, label in doc_files:
        full_path = os.path.join(base_path, file_path)
        if check_file(full_path, label):
            doc_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    print(f"Backend Files:       {backend_count}/{len(backend_files)}")
    print(f"Frontend Files:      {frontend_count}/{len(frontend_files)}")
    print(f"Documentation:       {doc_count}/{len(doc_files)}")
    
    total_files = len(backend_files) + len(frontend_files) + len(doc_files)
    total_found = backend_count + frontend_count + doc_count
    percentage = (total_found / total_files) * 100
    
    print(f"\n{'='*70}")
    print(f"Overall Status:      {total_found}/{total_files} files ({percentage:.1f}%)")
    
    if percentage == 100:
        print("\n🎉 ✅ ALL FILES PRESENT - SYSTEM COMPLETE!")
        print("\n🚀 Ready to run:")
        print("   Backend:  python manage.py runserver")
        print("   Frontend: cd sales_aice-main/sales_aice-main && npm run dev")
    else:
        print("\n⚠️ Some files are missing. Check the output above.")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
