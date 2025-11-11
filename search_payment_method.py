#!/usr/bin/env python
"""
Search for specific payment method ID in database
"""
import sqlite3

def search_payment_method(pm_id):
    """Search for specific payment method ID"""
    db_path = 'db.sqlite3'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔍 Searching for payment method: {pm_id}")
        print("-" * 60)
        
        # Search for exact match
        cursor.execute("""
            SELECT id, user_id, stripe_payment_method_id, card_type, 
                   last_four, exp_month, exp_year, is_default, is_active, created_at
            FROM subscriptions_paymentmethod 
            WHERE stripe_payment_method_id = ?
        """, (pm_id,))
        
        result = cursor.fetchone()
        
        if result:
            print("✅ Payment Method Found!")
            print(f"  ID: {result[0]}")
            print(f"  User ID: {result[1]}")
            print(f"  Stripe Payment Method ID: {result[2]}")
            print(f"  Card Type: {result[3]}")
            print(f"  Last Four: {result[4]}")
            print(f"  Expiry: {result[5]}/{result[6]}")
            print(f"  Is Default: {result[7]}")
            print(f"  Is Active: {result[8]}")
            print(f"  Created: {result[9]}")
        else:
            print("❌ Payment Method NOT FOUND!")
            
            # Search for similar IDs (partial match)
            print(f"\n🔍 Searching for similar payment methods...")
            cursor.execute("""
                SELECT stripe_payment_method_id
                FROM subscriptions_paymentmethod 
                WHERE stripe_payment_method_id LIKE ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (f"%{pm_id[-10:]}%",))  # Search last 10 characters
            
            similar = cursor.fetchall()
            if similar:
                print("📋 Similar payment methods found:")
                for sim in similar:
                    print(f"  - {sim[0]}")
            else:
                print("No similar payment methods found")
        
        # Show latest 5 payment methods for reference
        print(f"\n📋 Latest 5 Payment Methods for reference:")
        cursor.execute("""
            SELECT user_id, stripe_payment_method_id, created_at
            FROM subscriptions_paymentmethod 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        latest = cursor.fetchall()
        for i, pm in enumerate(latest, 1):
            print(f"  {i}. User {pm[0]}: {pm[1]} ({pm[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error searching database: {e}")

if __name__ == '__main__':
    # Search for the specific payment method
    search_payment_method("pm_1SFeDqAMrH3m7b2GgNylG2pc")
    print("\n✅ Search completed!")