# User Dashboard API Documentation

## Overview
Ye comprehensive user dashboard hai jahan user apni sab cheezein configure kar sakta hai. User ko complete control milta hai apne account, settings, calls, aur subscription ke upar.

## User Dashboard Features

### 🏠 Main Dashboard (`/api/dashboard/user/`)
**Main dashboard jahan user ko sabse important information milti hai:**

- **Personal Stats**: Call statistics, subscription status, usage metrics
- **Recent Calls**: Last 5 calls with details
- **Subscription Info**: Current plan, remaining days, billing info
- **Quick Stats**: Important metrics at a glance

**Sample Response:**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "avatar": "/media/avatars/user.jpg"
  },
  "subscription": {
    "plan": {
      "name": "Professional",
      "price": 29.99,
      "features": ["Unlimited calls", "AI assistance", "Call recording"]
    },
    "status": "active",
    "days_remaining": 15
  },
  "call_statistics": {
    "total_calls": 45,
    "this_month_calls": 12,
    "successful_calls": 42,
    "success_rate": 93.33
  },
  "recent_calls": [...]
}
```

### 👤 Profile Configuration (`/api/dashboard/user/profile/`)
**User apni personal information manage kar sakta hai:**

- **Personal Info**: Name, phone, email update
- **Avatar**: Profile picture upload/delete
- **Account Settings**: Notifications, privacy settings

**Update Profile:**
```bash
PATCH /api/dashboard/user/profile/
{
  "first_name": "Ahmad",
  "last_name": "Khan",
  "phone": "+92300000000"
}
```

### 📞 Call History (`/api/dashboard/user/calls/`)
**Complete call history with filtering:**

- **Filters**: Status, date range pagination
- **Details**: Duration, agent info, satisfaction rating
- **Search**: Phone number ya status ke basis pe

**Parameters:**
- `page`: Page number
- `status`: completed, failed, missed
- `date_from`: YYYY-MM-DD format
- `date_to`: YYYY-MM-DD format

### 💳 Subscription Management (`/api/dashboard/user/subscription/`)
**Complete subscription control:**

- **Current Plan**: Details aur features
- **Available Plans**: Upgrade/downgrade options
- **Billing History**: Past payments
- **Usage Metrics**: Current period usage

**Sample Response:**
```json
{
  "current_subscription": {
    "plan": {
      "name": "Professional",
      "price": 29.99,
      "features": ["Unlimited calls", "AI assistance"]
    },
    "days_remaining": 15,
    "cancel_at_period_end": false
  },
  "available_plans": [...],
  "billing_history": [...],
  "current_usage": {
    "calls_made": 25,
    "call_minutes": 180,
    "agents_used": 3
  }
}
```

### ⚙️ Account Settings (`/api/dashboard/user/settings/`)
**Complete account configuration:**

- **Notification Preferences**: Email, SMS, marketing emails
- **Privacy Settings**: Profile visibility, call recording consent
- **Call Preferences**: Auto-record, AI assistance, quality settings

**Update Settings:**
```bash
PATCH /api/dashboard/user/settings/
{
  "notification_preferences": {
    "email_notifications": true,
    "sms_notifications": false,
    "marketing_emails": true
  },
  "call_preferences": {
    "auto_record_calls": true,
    "ai_assistance_enabled": true,
    "call_quality": "high"
  }
}
```

### 🔐 Security Features

#### Change Password (`/api/dashboard/user/change-password/`)
```bash
POST /api/dashboard/user/change-password/
{
  "current_password": "old_password",
  "new_password": "new_secure_password",
  "confirm_password": "new_secure_password"
}
```

#### Delete Account (`/api/dashboard/user/delete-account/`)
```bash
POST /api/dashboard/user/delete-account/
{
  "password": "current_password",
  "confirmation": "DELETE"
}
```

#### Export Data (`/api/dashboard/user/export-data/`)
**GDPR compliance - user ka complete data export:**
- Personal information
- Call history
- Billing history
- Subscription data

### 📷 Avatar Management (`/api/dashboard/user/avatar/`)

#### Upload Avatar:
```bash
POST /api/dashboard/user/avatar/
Content-Type: multipart/form-data

avatar: [image file]
```

#### Delete Avatar:
```bash
DELETE /api/dashboard/user/avatar/
```

**Restrictions:**
- File types: JPG, PNG only
- Max size: 5MB
- Auto-resize to 300x300px

### 🔔 Notifications (`/api/dashboard/user/notifications/`)
**User notifications management:**

- **Get Notifications**: All ya sirf unread
- **Mark as Read**: Single ya all notifications

**Parameters:**
- `unread_only`: true/false
- `page`: Page number

**Mark as Read:**
```bash
PATCH /api/dashboard/user/notifications/
{
  "notification_id": "notification-id"
}
// OR
{
  "mark_all_read": true
}
```

### 🎨 Dashboard Preferences (`/api/dashboard/user/preferences/`)
**Complete dashboard customization:**

- **Layout**: Default, compact, detailed
- **Theme**: Light, dark, auto
- **Language**: EN, UR, AR
- **Timezone**: User timezone
- **Widgets**: Customize dashboard widgets

**Update Preferences:**
```bash
PATCH /api/dashboard/user/preferences/
{
  "theme": "dark",
  "language": "ur",
  "dashboard_layout": "compact",
  "dashboard_widgets": [
    "subscription_status",
    "recent_calls",
    "call_statistics"
  ]
}
```

## Sample Frontend Usage

### Dashboard Component
```javascript
// Get main dashboard data
const dashboard = await fetch('/api/dashboard/user/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Update profile
const updateProfile = await fetch('/api/dashboard/user/profile/', {
  method: 'PATCH',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    first_name: 'Ahmad',
    last_name: 'Khan'
  })
});

// Get call history with filters
const calls = await fetch('/api/dashboard/user/calls/?status=completed&page=1', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Settings Component
```javascript
// Get current settings
const settings = await fetch('/api/dashboard/user/settings/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Update settings
const updateSettings = await fetch('/api/dashboard/user/settings/', {
  method: 'PATCH',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    notification_preferences: {
      email_notifications: true,
      sms_notifications: false
    }
  })
});
```

## User Dashboard Sections

### 1. **Overview Section**
- Quick stats cards
- Recent activity
- Subscription status
- Urgent notifications

### 2. **Profile Section**
- Personal information form
- Avatar upload/change
- Contact details
- Account verification status

### 3. **Calls Section**
- Call history table with filters
- Call statistics charts
- Recent calls list
- Call recordings (if available)

### 4. **Subscription Section**
- Current plan details
- Usage meters/progress bars
- Billing history table
- Upgrade/downgrade options
- Payment method management

### 5. **Settings Section**
- **Account Settings**: Basic info, password
- **Notifications**: Email, SMS, push preferences
- **Privacy**: Data sharing, recording consent
- **Preferences**: Theme, language, timezone
- **Security**: 2FA, active sessions

### 6. **Support Section**
- Help articles
- Contact support
- Export data (GDPR)
- Account deletion

## Authentication
All APIs require JWT token:
```
Authorization: Bearer <your-jwt-token>
```

## Error Handling
Standard HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

## Usage Examples

### Complete User Onboarding Flow:
1. Register user
2. Get dashboard overview
3. Update profile information
4. Set preferences
5. Choose subscription plan
6. Configure notifications

### Daily User Tasks:
1. Check dashboard for new calls/notifications
2. Review call history
3. Check subscription usage
4. Update settings if needed

**Ye user dashboard complete hai aur user ko har cheez control karne ki facility deti hai!** 🚀
