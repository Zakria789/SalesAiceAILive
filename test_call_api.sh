#!/bin/bash
# CURL test for Call Initiation API
# Copy and run this command to test the API

URL="https://uncontortioned-na-ponderously.ngrok-free.dev/api/hume-twilio/initiate-call/"
PHONE="923403471112"
AGENT_ID="1"

echo "================================================================================"
echo "TESTING CALL INITIATION API WITH CURL"
echo "================================================================================"
echo ""
echo "📋 REQUEST DETAILS:"
echo "   URL: $URL"
echo "   Phone: $PHONE"
echo "   Agent ID: $AGENT_ID"
echo ""
echo "📤 SENDING REQUEST..."
echo ""

curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"phone_no\": \"$PHONE\",
    \"agent_id\": $AGENT_ID
  }" \
  -v

echo ""
echo "================================================================================"
echo ""
echo "✅ If you see success: true → CALL INITIATED!"
echo "❌ If error → Check Django server is running"
echo ""
