#!/bin/bash

SERVER_URL="https://scott-valley-hvac-api.fly.dev"
WEBHOOK_URL="${SERVER_URL}/webhooks/ghl"
LOCATION_ID="NHEXwG3xQVwKMO77jAuB"

echo "======================================================================"
echo "🧪 TESTING DEPLOYED WEBHOOKS"
echo "======================================================================"
echo "Server URL: ${SERVER_URL}"
echo "Webhook URL: ${WEBHOOK_URL}"
echo "Location ID: ${LOCATION_ID}"
echo ""

# Test 1: Contact Created
echo "======================================================================"
echo "1️⃣  TESTING: Contact Created Webhook"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"contact.created\",
    \"locationId\": \"${LOCATION_ID}\",
    \"contactId\": \"TEST_CONTACT_CREATED_$(date +%s)\"
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test 2: Contact Updated
echo "======================================================================"
echo "2️⃣  TESTING: Contact Updated Webhook"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"contact.updated\",
    \"locationId\": \"${LOCATION_ID}\",
    \"contactId\": \"TEST_CONTACT_UPDATED_$(date +%s)\"
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test 3: Appointment Created
echo "======================================================================"
echo "3️⃣  TESTING: Appointment Created Webhook"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"appointment.created\",
    \"locationId\": \"${LOCATION_ID}\",
    \"contactId\": \"TEST_CONTACT_APPT_$(date +%s)\",
    \"data\": {
      \"appointment\": {
        \"id\": \"TEST_APPT_$(date +%s)\",
        \"title\": \"Test Appointment\",
        \"startTime\": \"2024-11-21T14:00:00Z\",
        \"endTime\": \"2024-11-21T14:30:00Z\"
      }
    }
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test 4: Form Submitted
echo "======================================================================"
echo "4️⃣  TESTING: Form Submitted Webhook"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"form.submitted\",
    \"locationId\": \"${LOCATION_ID}\",
    \"data\": {
      \"contact\": {
        \"id\": \"TEST_CONTACT_FORM_$(date +%s)\",
        \"phone\": \"+15551234567\",
        \"email\": \"test@example.com\"
      },
      \"form\": {
        \"id\": \"TEST_FORM_$(date +%s)\",
        \"name\": \"Test Form\"
      }
    }
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test 5: Location ID Mismatch (should be ignored)
echo "======================================================================"
echo "5️⃣  TESTING: Location ID Mismatch (Should be Ignored)"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"contact.created\",
    \"locationId\": \"WRONG_LOCATION_ID\",
    \"contactId\": \"TEST_CONTACT_WRONG\"
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

# Test 6: Invalid Event Type
echo "======================================================================"
echo "6️⃣  TESTING: Invalid Event Type (Should Handle Gracefully)"
echo "======================================================================"
curl -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"unknown.event\",
    \"locationId\": \"${LOCATION_ID}\",
    \"contactId\": \"TEST_CONTACT_UNKNOWN\"
  }" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | python3 -m json.tool

echo ""
echo ""

echo "======================================================================"
echo "✅ ALL WEBHOOK TESTS COMPLETED"
echo "======================================================================"
