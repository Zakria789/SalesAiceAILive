#!/bin/bash

# Change Password API Test
# ========================

echo "🔐 Testing Change Password API"
echo "=============================="

# Step 1: Get JWT Token
echo ""
echo "1️⃣  Getting JWT Token..."

TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8002/api/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "umair11@gmail.com",
    "password": "Test@123"
  }')

echo "Login Response: $TOKEN_RESPONSE"

# Extract token (you might need to parse JSON properly)
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token obtained: ${TOKEN:0:20}..."

# Step 2: Change Password
echo ""
echo "2️⃣  Changing Password..."
echo "URL: http://localhost:8002/api/accounts/user/change-password/"

RESPONSE=$(curl -s -X PUT "http://localhost:8002/api/accounts/user/change-password/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Test@123",
    "new_password": "Test@1234"
  }')

echo ""
echo "📊 RESPONSE:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "✅ Test Complete!"