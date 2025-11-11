# Subscription Management API - Parameter Guide

## Quick Answer

Aap ke sawaal ka jawab: **`/api/subscriptions/manage/` API ke parameters kahan se lengon ga?**

### Required Parameters for `/api/subscriptions/manage/`

```json
{
  "action": "subscribe",      // ❌ WRONG! Use: "upgrade", "downgrade", or "cancel"
  "package_id": "string",     // ❌ WRONG! Use: "new_plan_id" 
  "payment_method_id": "string" // ❌ WRONG! Not needed for manage API
}
```

**✅ CORRECT Parameters:**

```json
{
  "action": "upgrade",        // "upgrade", "downgrade", or "cancel" 
  "new_plan_id": "40ff1cbe-3a5a-449f-a898-923a7e5227a3"  // Only for upgrade/downgrade
}
```

---

## Complete Step-by-Step Guide

### Step 1: Get JWT Token

**Method 1 - Admin Token (Easiest):**
```bash
curl -X GET "http://localhost:8000/api/auth/admin-token/"
```

**Method 2 - User Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/quick-token/" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@testcenter.com", "password": "admin123"}'
```

### Step 2: Get Available Plan IDs

```bash
curl -X GET "http://localhost:8000/api/subscriptions/api/plans/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Available Plans:**
- **Starter**: `40ff1cbe-3a5a-449f-a898-923a7e5227a3` - $29/month - 1000 minutes, 1 agent
- **Pro**: `e9062b7b-199c-49f6-be95-338f12e6fbd5` - $99/month - 3000 minutes, 5 agents  
- **Enterprise**: `691027e9-3f54-4dc9-9a88-d754c13ad2ec` - $299/month - 10000 minutes, 25 agents

### Step 3: Call Subscription Management API

**Cancel Subscription:**
```bash
curl -X POST "http://localhost:8000/api/subscriptions/manage/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "cancel"}'
```

**Upgrade to Pro:**
```bash
curl -X POST "http://localhost:8000/api/subscriptions/manage/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "upgrade", "new_plan_id": "e9062b7b-199c-49f6-be95-338f12e6fbd5"}'
```

**Downgrade to Starter:**
```bash
curl -X POST "http://localhost:8000/api/subscriptions/manage/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "downgrade", "new_plan_id": "40ff1cbe-3a5a-449f-a898-923a7e5227a3"}'
```

---

## Real Example with Current Data

**Current JWT Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5NTA1OTI1LCJpYXQiOjE3NTk1MDIzMjUsImp0aSI6IjgzOTY3NWI3ZDUxNzQ3YTQ4M2IyZGI1YjY3MDUzNThkIiwidXNlcl9pZCI6MTZ9.K4vq_0Hgb8Ng6z7F3QQQn8QqS7_T3E2H1nJ4X5m9K0Y
```

**Working Example - Upgrade to Pro:**
```bash
curl -X POST "http://localhost:8000/api/subscriptions/manage/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5NTA1OTI1LCJpYXQiOjE3NTk1MDIzMjUsImp0aSI6IjgzOTY3NWI3ZDUxNzQ3YTQ4M2IyZGI1YjY3MDUzNThkIiwidXNlcl9pZCI6MTZ9.K4vq_0Hgb8Ng6z7F3QQQn8QqS7_T3E2H1nJ4X5m9K0Y" \
  -H "Content-Type: application/json" \
  -d '{"action": "upgrade", "new_plan_id": "e9062b7b-199c-49f6-be95-338f12e6fbd5"}'
```

---

## API Endpoint Differences

### `/api/subscriptions/manage/` - For EXISTING subscriptions
**Purpose:** Upgrade, downgrade, or cancel existing subscription

**Parameters:**
- `action`: "upgrade", "downgrade", "cancel"
- `new_plan_id`: Required for upgrade/downgrade only

### `/api/subscriptions/create/` - For NEW subscriptions  
**Purpose:** Create a brand new subscription

**Parameters:**
- `plan_id`: Plan ID from available plans
- `payment_method_id`: Stripe payment method (use "pm_card_visa" for testing)
- `billing_cycle`: "month" or "year" (optional)

---

## Common Mistakes to Avoid

❌ **Wrong action values:** `"subscribe"` 
✅ **Correct:** `"upgrade"`, `"downgrade"`, `"cancel"`

❌ **Wrong parameter name:** `"package_id"`
✅ **Correct:** `"new_plan_id"`

❌ **Using payment_method_id in manage API**
✅ **Only needed in create API**

❌ **Forgetting JWT token**
✅ **Always include:** `Authorization: Bearer YOUR_TOKEN`

---

## Quick Test Tools

1. **Interactive Tester:**
   ```bash
   python subscription_api_test.py
   ```

2. **Parameter Guide:**
   ```bash
   python subscription_parameter_guide.py
   ```

3. **Simple Example:**
   ```bash
   python simple_subscription_example.py
   ```

4. **Swagger UI:** http://localhost:8000/swagger/

---

## Summary - What You Need

### For `/api/subscriptions/manage/`:
1. **JWT Token** - Get from `/api/auth/admin-token/`
2. **action** - "upgrade", "downgrade", or "cancel"  
3. **new_plan_id** - Only for upgrade/downgrade (get from `/api/subscriptions/api/plans/`)

### Current Available Plan IDs:
- Starter: `40ff1cbe-3a5a-449f-a898-923a7e5227a3`
- Pro: `e9062b7b-199c-49f6-be95-338f12e6fbd5`  
- Enterprise: `691027e9-3f54-4dc9-9a88-d754c13ad2ec`

### Working JWT Token (expires in 1 hour):
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU5NTA1OTI1...
```

**You can now call the API with these exact parameters!**
