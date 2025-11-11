"""
Payment Methods API Test Script
Test the newly implemented payment methods management APIs
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/subscriptions"
TOKEN = "your_jwt_token_here"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_list_payment_methods():
    """Test GET /api/payment-methods/"""
    print("\n🔍 Testing: List Payment Methods")
    
    response = requests.get(f"{BASE_URL}/api/payment-methods/", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_add_payment_method():
    """Test POST /api/payment-methods/"""
    print("\n➕ Testing: Add Payment Method")
    
    # This would come from Stripe Elements in real frontend
    test_data = {
        "payment_method_id": "pm_test_123456789",  # Mock Stripe payment method ID
        "set_as_default": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/payment-methods/", 
        headers=headers,
        json=test_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_update_payment_method(payment_method_id):
    """Test PUT /api/payment-methods/{id}/"""
    print(f"\n✏️ Testing: Update Payment Method {payment_method_id}")
    
    test_data = {
        "set_as_default": True
    }
    
    response = requests.put(
        f"{BASE_URL}/api/payment-methods/{payment_method_id}/", 
        headers=headers,
        json=test_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_delete_payment_method(payment_method_id):
    """Test DELETE /api/payment-methods/{id}/"""
    print(f"\n🗑️ Testing: Delete Payment Method {payment_method_id}")
    
    response = requests.delete(
        f"{BASE_URL}/api/payment-methods/{payment_method_id}/", 
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def main():
    """Run all tests"""
    print("🚀 Payment Methods API Testing Started")
    print("=" * 50)
    
    # Test 1: List payment methods
    result = test_list_payment_methods()
    
    # Test 2: Add payment method (will fail without real Stripe token)
    # test_add_payment_method()
    
    print("\n✅ Testing completed!")
    print("\nℹ️ Note: Add payment method test requires real Stripe payment method ID from frontend")
    print("ℹ️ Update and delete tests require existing payment method IDs")

if __name__ == "__main__":
    main()

# Frontend Integration Example
frontend_example = """
// Frontend Integration Example
const PaymentMethodsManager = () => {
    const [paymentMethods, setPaymentMethods] = useState([]);
    const [loading, setLoading] = useState(false);
    
    // List payment methods
    const fetchPaymentMethods = async () => {
        try {
            const response = await fetch('/api/subscriptions/api/payment-methods/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                }
            });
            const data = await response.json();
            
            if (data.success) {
                setPaymentMethods(data.payment_methods);
            }
        } catch (error) {
            console.error('Error fetching payment methods:', error);
        }
    };
    
    // Add new payment method
    const addPaymentMethod = async () => {
        setLoading(true);
        
        // Step 1: Create payment method with Stripe Elements
        const {error, paymentMethod} = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
            billing_details: {
                name: customerName,
            },
        });
        
        if (error) {
            console.error('Stripe error:', error);
            setLoading(false);
            return;
        }
        
        // Step 2: Save to your backend
        try {
            const response = await fetch('/api/subscriptions/api/payment-methods/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    payment_method_id: paymentMethod.id,
                    set_as_default: false
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Payment method added:', result.payment_method);
                fetchPaymentMethods(); // Refresh list
            } else {
                console.error('Error:', result.error);
            }
        } catch (error) {
            console.error('Network error:', error);
        }
        
        setLoading(false);
    };
    
    // Set as default
    const setAsDefault = async (pmId) => {
        try {
            const response = await fetch(`/api/subscriptions/api/payment-methods/${pmId}/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    set_as_default: true
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                fetchPaymentMethods(); // Refresh list
            }
        } catch (error) {
            console.error('Error setting default:', error);
        }
    };
    
    // Remove payment method
    const removePaymentMethod = async (pmId) => {
        if (!confirm('Are you sure you want to remove this payment method?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/subscriptions/api/payment-methods/${pmId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                fetchPaymentMethods(); // Refresh list
            } else {
                alert(result.error);
            }
        } catch (error) {
            console.error('Error removing payment method:', error);
        }
    };
    
    useEffect(() => {
        fetchPaymentMethods();
    }, []);
    
    return (
        <div className="payment-methods-manager">
            <h3>Payment Methods</h3>
            
            {paymentMethods.length === 0 ? (
                <p>No payment methods found. Add your first payment method.</p>
            ) : (
                <div className="payment-methods-list">
                    {paymentMethods.map(pm => (
                        <div key={pm.id} className="payment-method-card">
                            <div className="card-info">
                                <span className="card-display">{pm.display_name}</span>
                                <span className="card-expiry">Expires {pm.expires}</span>
                                {pm.is_default && (
                                    <span className="default-badge">Default</span>
                                )}
                            </div>
                            <div className="card-actions">
                                {!pm.is_default && (
                                    <button 
                                        onClick={() => setAsDefault(pm.id)}
                                        className="btn-secondary"
                                    >
                                        Set as Default
                                    </button>
                                )}
                                <button 
                                    onClick={() => removePaymentMethod(pm.id)}
                                    className="btn-danger"
                                    disabled={pm.is_default}
                                >
                                    Remove
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
            
            <div className="add-payment-method">
                <h4>Add New Payment Method</h4>
                <div id="card-element">
                    {/* Stripe Elements will mount here */}
                </div>
                <button 
                    onClick={addPaymentMethod}
                    disabled={loading}
                    className="btn-primary"
                >
                    {loading ? 'Adding...' : 'Add Payment Method'}
                </button>
            </div>
        </div>
    );
};
"""

print("\n" + "="*50)
print("Frontend Integration Example:")
print("="*50)
print(frontend_example)
