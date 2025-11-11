# 📊 Scheduled/Bulk Calls API - Local Database Integration

## ✅ Answer: JI HAAN, YE API LOCAL DB SE DATA LETA HAI!

---

## 🎯 Endpoint Details

### URL
```
GET /api/hume-twilio/dashboard/outbound/scheduled/
```

### Authentication
```
Bearer Token Required (JWT)
```

---

## 💾 Data Source: LOCAL DATABASE

**Model:** `TwilioCall`  
**Database Table:** `twilio_calls`  
**Filter:** `direction='outbound'`

### Query Logic (Code):
```python
# File: HumeAiTwilio/api_views/dashboard_views.py
# Line: 663

calls = TwilioCall.objects.filter(
    direction='outbound'
).select_related('agent')
```

✅ **100% Local Database** - Koi external API call nahi!

---

## 📊 Response Structure

```json
{
  "success": true,
  "calls": {
    "pending": [
      {
        "call_id": "uuid",
        "call_sid": "CA1234567890",
        "to_number": "+15551234567",
        "customer_name": "John Doe",
        "status": "initiated",
        "agent": {
          "id": "agent-uuid",
          "name": "Sales Agent"
        },
        "created_at": "2025-10-24T10:00:00Z",
        "started_at": null,
        "duration": 0
      }
    ],
    "active": [
      {
        "call_id": "uuid",
        "status": "in_progress",
        "started_at": "2025-10-24T10:05:00Z",
        "duration": 120
      }
    ],
    "completed": [
      {
        "call_id": "uuid",
        "status": "completed",
        "duration": 300
      }
    ],
    "failed": [
      {
        "call_id": "uuid",
        "status": "failed"
      }
    ]
  },
  "summary": {
    "total_pending": 5,
    "total_active": 2,
    "total_completed": 10,
    "total_failed": 3
  }
}
```

---

## 🔍 Query Parameters

### Filter by Status
```bash
# Get only pending calls
GET /api/hume-twilio/dashboard/outbound/scheduled/?status=pending

# Get only active calls
GET /api/hume-twilio/dashboard/outbound/scheduled/?status=in_progress

# Get only completed calls
GET /api/hume-twilio/dashboard/outbound/scheduled/?status=completed

# Get only failed calls
GET /api/hume-twilio/dashboard/outbound/scheduled/?status=failed
```

---

## 📋 Status Categories

| Category | Database Status Values |
|----------|------------------------|
| **Pending** | `initiated` |
| **Active** | `in_progress` |
| **Completed** | `completed` |
| **Failed** | `failed`, `no_answer`, `busy` |

---

## 💾 Database Fields Used

```python
# From TwilioCall model
{
    'call_id': call.id,              # UUID (primary key)
    'call_sid': call.call_sid,       # Twilio Call SID
    'to_number': call.to_number,     # Customer phone number
    'customer_name': call.customer_name,  # Customer name
    'status': call.status,           # Current status
    'agent': {
        'id': call.agent.id,         # Agent UUID
        'name': call.agent.name      # Agent name
    },
    'created_at': call.created_at,   # When call was created
    'started_at': call.started_at,   # When call started
    'duration': call.duration        # Duration in seconds
}
```

---

## 🚀 Testing

### Option 1: Run Test Script
```powershell
.\venv\Scripts\Activate.ps1
python test_scheduled_calls_api.py
```

### Option 2: cURL Command
```bash
# Get JWT token first
curl -X POST "http://localhost:8002/api/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"umair11@gmail.com","password":"Test@123"}'

# Use token to get scheduled calls
curl -X GET "http://localhost:8002/api/hume-twilio/dashboard/outbound/scheduled/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Option 3: Python Requests
```python
import requests

# Login
response = requests.post('http://localhost:8002/api/accounts/login/', json={
    'email': 'umair11@gmail.com',
    'password': 'Test@123'
})
token = response.json()['access']

# Get scheduled calls
response = requests.get(
    'http://localhost:8002/api/hume-twilio/dashboard/outbound/scheduled/',
    headers={'Authorization': f'Bearer {token}'}
)

data = response.json()
print(f"Pending: {data['summary']['total_pending']}")
print(f"Active: {data['summary']['total_active']}")
print(f"Completed: {data['summary']['total_completed']}")
```

---

## 📊 Code Implementation

### Full Function (Simplified)
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scheduled_bulk_calls(request):
    """Get scheduled/bulk outbound calls from LOCAL DATABASE"""
    
    # Query local database
    calls = TwilioCall.objects.filter(
        direction='outbound'
    ).select_related('agent')
    
    # Optional status filter
    status_filter = request.GET.get('status')
    if status_filter == 'pending':
        calls = calls.filter(status='initiated')
    elif status_filter == 'in_progress':
        calls = calls.filter(status='in_progress')
    elif status_filter == 'completed':
        calls = calls.filter(status='completed')
    elif status_filter == 'failed':
        calls = calls.filter(status__in=['failed', 'no_answer', 'busy'])
    
    # Group by status
    calls_data = {
        'pending': [],
        'active': [],
        'completed': [],
        'failed': []
    }
    
    for call in calls:
        call_info = {
            'call_id': str(call.id),
            'call_sid': call.call_sid,
            'to_number': call.to_number,
            'customer_name': call.customer_name,
            'status': call.status,
            'agent': {
                'id': str(call.agent.id) if call.agent else None,
                'name': call.agent.name if call.agent else 'No Agent'
            },
            'created_at': call.created_at.isoformat(),
            'started_at': call.started_at.isoformat() if call.started_at else None,
            'duration': call.duration
        }
        
        # Categorize
        if call.status == 'initiated':
            calls_data['pending'].append(call_info)
        elif call.status == 'in_progress':
            calls_data['active'].append(call_info)
        elif call.status == 'completed':
            calls_data['completed'].append(call_info)
        else:
            calls_data['failed'].append(call_info)
    
    return Response({
        'success': True,
        'calls': calls_data,
        'summary': {
            'total_pending': len(calls_data['pending']),
            'total_active': len(calls_data['active']),
            'total_completed': len(calls_data['completed']),
            'total_failed': len(calls_data['failed'])
        }
    })
```

---

## 🎯 Use Cases

### 1. Dashboard View
```javascript
// React/Vue/Angular example
fetch('/api/hume-twilio/dashboard/outbound/scheduled/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => {
  // Display pending calls in queue
  setPendingCalls(data.calls.pending);
  
  // Display active calls
  setActiveCalls(data.calls.active);
  
  // Show statistics
  setStats(data.summary);
});
```

### 2. Queue Management
```javascript
// Get only pending calls
fetch('/api/hume-twilio/dashboard/outbound/scheduled/?status=pending')
.then(res => res.json())
.then(data => {
  console.log(`Calls in queue: ${data.summary.total_pending}`);
});
```

### 3. Progress Monitoring
```javascript
// Get only active calls
fetch('/api/hume-twilio/dashboard/outbound/scheduled/?status=in_progress')
.then(res => res.json())
.then(data => {
  console.log(`Calls in progress: ${data.summary.total_active}`);
});
```

---

## ✅ Benefits of Local Database

### 1. **Fast Performance** ⚡
- No external API calls
- Direct database query
- Instant response

### 2. **No Rate Limits** 🚀
- Unlimited requests
- No API quotas
- No throttling

### 3. **Complete Data** 📊
- All call details available
- Historical data
- Custom fields

### 4. **Offline Capable** 🔌
- Works without internet
- No dependency on Twilio API
- Reliable

### 5. **Cost Effective** 💰
- No API call charges
- No bandwidth costs
- Free queries

---

## 🔄 Data Sync

### How Data Gets to Local DB:

```
1. Twilio Webhook → Call Status Updates
   └─ TwilioCall.status updated
   └─ TwilioCall.duration updated

2. WebSocket Consumer → Real-time Updates
   └─ Call progress tracked
   └─ Timestamps updated

3. Dashboard API → Always reads fresh data
   └─ No caching
   └─ Real-time accuracy
```

---

## 📝 Summary

| Question | Answer |
|----------|--------|
| **Data source?** | ✅ Local PostgreSQL Database |
| **External API calls?** | ❌ NO |
| **Real-time?** | ✅ YES (updated by webhooks) |
| **Authentication?** | ✅ JWT Required |
| **Filters available?** | ✅ By status |
| **Performance?** | ⚡ Fast (database query) |
| **Cost?** | 💰 Free (no API charges) |

---

## 🎉 Conclusion

**YES! Ye API 100% local database se data le raha hai.**

- ✅ Fast queries
- ✅ No external dependencies
- ✅ Real-time updates (via webhooks)
- ✅ Complete call history
- ✅ Filterable by status
- ✅ No rate limits
- ✅ Cost-effective

**Aap ise production me use kar sakte ho without any concerns!** 🚀
