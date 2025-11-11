# User Subscription Flow - Simple Guide

## Step 1: User sees available packages (Plans)

**API Endpoint:** `GET /api/subscriptions/packages/`

### Response Example:
```json
{
  "user_needs_package_selection": true,
  "available_packages": [
    {
      "id": "uuid-starter",
      "package_name": "Starter",
      "monthly_price": 29.0,
      "call_minutes_limit": 500,
      "agents_allowed": 1,
      "analytics_access": false,
      "advanced_analytics": false,
      "recommended": false
    },
    {
      "id": "uuid-pro", 
      "package_name": "Pro",
      "monthly_price": 99.0,
      "call_minutes_limit": 2000,
      "agents_allowed": 3,
      "analytics_access": true,
      "advanced_analytics": false,
      "recommended": true
    },
    {
      "id": "uuid-enterprise",
      "package_name": "Enterprise", 
      "monthly_price": 299.0,
      "call_minutes_limit": 10000,
      "agents_allowed": 10,
      "analytics_access": true,
      "advanced_analytics": true,
      "recommended": false
    }
  ]
}
```

## Step 2: User selects a package and subscribes

**API Endpoint:** `POST /api/subscriptions/manage/`

### Request Body:
```json
{
  "action": "subscribe",
  "package_id": "uuid-pro",
  "payment_method_id": "pm_1234567890"
}
```

### Response Example:
```json
{
  "message": "Successfully subscribed to package",
  "subscription_id": "uuid-subscription",
  "package_name": "Pro",
  "status": "active"
}
```

## Step 3: User can view their subscription status

**API Endpoint:** `GET /api/subscriptions/manage/`

### Response Example:
```json
{
  "subscription": {
    "id": "uuid-subscription",
    "package_name": "Pro",
    "status": "active",
    "monthly_price": 99.0,
    "current_period_end": "2024-02-15T23:59:59Z",
    "days_remaining": 25,
    "cancel_at_period_end": false
  },
  "usage": {
    "minutes_used": 150,
    "minutes_limit": 2000,
    "minutes_remaining": 1850,
    "usage_percentage": 7.5
  },
  "features": {
    "agents_allowed": 3,
    "analytics_access": true,
    "advanced_analytics": false
  },
  "management_options": {
    "can_upgrade": true,
    "can_downgrade": false,
    "can_cancel": true
  }
}
```

## Frontend Implementation Example

### 1. Show Package Selection (React/Vue.js)
```javascript
// Fetch available packages
const fetchPackages = async () => {
  const response = await fetch('/api/subscriptions/packages/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  
  if (data.user_needs_package_selection) {
    showPackageSelection(data.available_packages);
  }
};

// Display packages to user
const showPackageSelection = (packages) => {
  packages.forEach(pkg => {
    console.log(`${pkg.package_name}: $${pkg.monthly_price}/month`);
    console.log(`- ${pkg.call_minutes_limit} minutes`);
    console.log(`- ${pkg.agents_allowed} agents`);
    console.log(`- Analytics: ${pkg.analytics_access ? 'Yes' : 'No'}`);
    console.log('---');
  });
};
```

### 2. Subscribe to Selected Package
```javascript
// When user clicks "Subscribe" button
const subscribeToPackage = async (packageId, paymentMethodId) => {
  try {
    const response = await fetch('/api/subscriptions/manage/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action: 'subscribe',
        package_id: packageId,
        payment_method_id: paymentMethodId
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      alert(`Successfully subscribed to ${result.package_name}!`);
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      alert(`Error: ${result.error}`);
    }
  } catch (error) {
    alert('Subscription failed. Please try again.');
  }
};
```

### 3. Payment Integration with Stripe
```javascript
// Initialize Stripe
const stripe = Stripe('pk_test_your_publishable_key');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

// Handle payment and subscription
const handleSubscription = async (packageId) => {
  // Create payment method
  const {error, paymentMethod} = await stripe.createPaymentMethod({
    type: 'card',
    card: cardElement,
    billing_details: {
      name: 'Customer Name',
      email: 'customer@example.com',
    },
  });

  if (error) {
    console.error('Payment method creation failed:', error);
    return;
  }

  // Subscribe with payment method
  await subscribeToPackage(packageId, paymentMethod.id);
};
```

## User Flow Summary:

1. **User Login** → Check if user has subscription
2. **No Subscription** → Show package selection page
3. **User Selects Package** → Show payment form
4. **Payment Success** → Create subscription + redirect to dashboard
5. **Dashboard** → Show subscription status and usage

## Package Features Comparison:

| Feature | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Monthly Price | $29 | $99 | $299 |
| Call Minutes | 500 | 2,000 | 10,000 |
| Agents Allowed | 1 | 3 | 10 |
| Basic Analytics | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |
| API Access | ❌ | ❌ | ✅ |

## Important Notes:

- **First Login**: User must select a package to continue
- **Package Selection**: User sees feature comparison table
- **Payment**: Stripe handles secure payment processing
- **Usage Tracking**: System tracks monthly minute usage
- **Alerts**: User gets alerts at 80% usage
- **Management**: User can upgrade/downgrade/cancel anytime

Yeh simple flow hai - user login karta hai, packages dekhta hai, select karta hai, payment karta hai, aur phir dashboard use kar sakta hai!
