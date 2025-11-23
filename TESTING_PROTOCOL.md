# 🧪 Scott Valley HVAC - AI Voice Agent Testing Protocol

**Version:** 2.0  
**Last Updated:** November 2025  
**Project:** AI Voice Automation System (Vapi.ai + GoHighLevel)

---

## 📋 Table of Contents

1. [Pre-Testing Checklist](#pre-testing-checklist)
2. [Test Environment Setup](#test-environment-setup)
3. [Automated System Tests](#automated-system-tests)
4. [Inbound Call Scenarios](#inbound-call-scenarios)
5. [Outbound Call Scenarios](#outbound-call-scenarios)
6. [Integration Tests](#integration-tests)
7. [Knowledge Base Tests](#knowledge-base-tests)
8. [Data Capture & CRM Tests](#data-capture--crm-tests)
9. [Error Handling & Edge Cases](#error-handling--edge-cases)
10. [Performance & Monitoring](#performance--monitoring)
11. [Test Execution Log](#test-execution-log)

---

## ✅ Pre-Testing Checklist

### Environment Configuration

| Item | Status | Notes |
|------|--------|-------|
| Vapi API Key Configured | ⬜ | Key: `bee0337d-41cd-49c2-9038-98cd0e18c75b` |
| GHL API Key Configured | ⬜ | Location ID: `NHEXwG3xQVwKMO77jAuB` |
| Twilio Credentials Set | ⬜ | Account SID & Auth Token |
| Assistant IDs Configured | ⬜ | Inbound: `d61d0517-4a65-496e-b97f-d3ad220f684e`<br>Outbound: `d6c74f74-de2a-420d-ae59-aab8fa7cbabe` |
| Phone Number Configured | ⬜ | Vapi phone number ID set |
| Webhook URLs Active | ⬜ | GHL → FastAPI webhooks configured |
| Custom Fields Created | ⬜ | All 14 fields in GHL |

### System Health Check

| Component | Status | Last Checked | Notes |
|-----------|--------|--------------|-------|
| Vapi API Connection | ⬜ | - | Should return 200 OK |
| GHL API Connection | ⬜ | - | Should return calendars |
| FastAPI Server | ⬜ | - | Should be running on port 8000 |
| Database Connection | ⬜ | - | If applicable |
| Twilio Connection | ⬜ | - | Test SMS/voice |

---

## 🔧 Test Environment Setup

### Required Tools

- **Vapi Test Client**: `scripts/vapi_test_client.py`
- **Test Runner**: `scripts/run_test_scenarios.py`
- **Call Log Analyzer**: `scripts/check_call_logs.py`
- **Quick Test**: `scripts/quick_test.py`
- **Automated Tests**: `scripts/run_automated_tests.py`

### Test Phone Numbers

| Purpose | Number | Status | Notes |
|---------|--------|--------|-------|
| Primary Test Number | `+1XXX-XXX-XXXX` | ⬜ | For inbound/outbound testing |
| Warm Transfer Test | `+1XXX-XXX-XXXX` | ⬜ | For transfer testing |
| SMS Fallback Test | `+1XXX-XXX-XXXX` | ⬜ | For SMS testing |

### Running Automated Tests

```bash
# Run all automated system tests
export VAPI_API_KEY=bee0337d-41cd-49c2-9038-98cd0e18c75b
uv run python scripts/run_automated_tests.py

# Check recent calls
uv run python scripts/check_call_logs.py --limit 10

# Quick single test
uv run python scripts/quick_test.py "Test message" --phone +1XXX-XXX-XXXX
```

---

## 🤖 Automated System Tests

### Test Suite 1: API Connectivity

| Test ID | Test Name | Expected Result | Status | Notes |
|---------|-----------|------------------|--------|-------|
| AUTO-001 | Vapi API Connection | ✅ Successfully connected | ⬜ | Should return 200 OK |
| AUTO-002 | GHL API Connection | ✅ Successfully connected | ⬜ | Should return calendars |
| AUTO-003 | Twilio API Connection | ✅ Successfully connected | ⬜ | Test SMS/voice |
| AUTO-004 | FastAPI Health Check | ✅ Server responding | ⬜ | GET /health returns 200 |

### Test Suite 2: Assistant Configuration

| Test ID | Test Name | Expected Result | Status | Notes |
|---------|-----------|------------------|--------|-------|
| AUTO-005 | Inbound Assistant Exists | ✅ Assistant found | ⬜ | ID: `d61d0517-4a65-496e-b97f-d3ad220f684e` |
| AUTO-006 | Inbound Functions Count | ✅ 7 functions | ⬜ | All required functions present |
| AUTO-007 | Outbound Assistant Exists | ✅ Assistant found | ⬜ | ID: `d6c74f74-de2a-420d-ae59-aab8fa7cbabe` |
| AUTO-008 | Outbound Functions Count | ✅ 5 functions | ⬜ | All required functions present |
| AUTO-009 | Voice Profile Check | ✅ Female voice "hera" | ⬜ | Both assistants |
| AUTO-010 | Knowledge Base Integration | ✅ System prompt includes KB | ⬜ | Check assistant config |

### Test Suite 3: GHL Configuration

| Test ID | Test Name | Expected Result | Status | Notes |
|---------|-----------|------------------|--------|-------|
| AUTO-011 | Diagnostic Calendar Exists | ✅ Calendar found | ⬜ | For repair appointments |
| AUTO-012 | Proposal Calendar Exists | ✅ Calendar found | ⬜ | For estimate appointments |
| AUTO-013 | Custom Fields Check | ✅ 14/14 fields exist | ⬜ | All required fields present |
| AUTO-014 | Webhook Endpoints Active | ✅ Endpoints responding | ⬜ | POST /webhooks/ghl |

---

## 📞 Inbound Call Scenarios

### Scenario 1: Service/Repair Request

**Test ID:** INBOUND-001  
**Priority:** High  
**Assistant:** Inbound  
**Expected Duration:** 3-5 minutes

#### Test Steps

1. **Initiate Call**
   - Call the Vapi phone number
   - Wait for AI assistant greeting

2. **Conversation Flow**
   ```
   You: "Hello, I need help with my heating system"
   AI: [Should greet warmly and ask for details]
   
   You: "My furnace stopped working last night, it's really cold"
   AI: [Should express empathy and ask for contact info]
   
   You: "My name is John Smith, phone is 503-555-0101, email is john.smith@test.com"
   AI: [Should confirm and ask for address]
   
   You: "My address is 123 Main St, Salem, OR 97301"
   AI: [Should verify service area and ask for SMS consent]
   
   You: "Yes, I'd like to receive text confirmations"
   AI: [Should acknowledge and check calendar]
   
   You: "When can you come out to fix it?"
   AI: [Should offer available appointment times]
   
   You: "Yes, tomorrow at 2 PM works for me"
   AI: [Should book appointment and confirm details]
   
   You: "Yes, please send me a confirmation"
   AI: [Should send confirmation via SMS]
   ```

3. **Verification Steps**
   - [ ] Contact created in GHL with all details
   - [ ] Appointment booked in Diagnostic calendar
   - [ ] SMS consent set to `true`
   - [ ] Call summary logged in GHL
   - [ ] SMS confirmation sent (if consent given)
   - [ ] Call transcript available in Vapi dashboard

#### Expected Results

| Checkpoint | Expected | Actual | Status |
|------------|----------|--------|--------|
| Call Answered | ✅ Within 3 seconds | ⬜ | ⬜ |
| Contact Created | ✅ In GHL CRM | ⬜ | ⬜ |
| Appointment Booked | ✅ Correct calendar | ⬜ | ⬜ |
| SMS Consent Captured | ✅ `true` | ⬜ | ⬜ |
| Confirmation Sent | ✅ SMS delivered | ⬜ | ⬜ |
| Call Summary Logged | ✅ In GHL timeline | ⬜ | ⬜ |

#### Pass Criteria
- ✅ All verification steps pass
- ✅ Call duration < 5 minutes
- ✅ No errors in call logs
- ✅ Data accuracy 100%

---

### Scenario 2: Installation/Estimate Request

**Test ID:** INBOUND-002  
**Priority:** High  
**Assistant:** Inbound  
**Expected Duration:** 4-6 minutes

#### Test Steps

1. **Initiate Call**
   - Call the Vapi phone number
   - Wait for AI assistant greeting

2. **Conversation Flow**
   ```
   You: "I'm looking to replace my old air conditioning system"
   AI: [Should ask for details and explain process]
   
   You: "My name is Sarah Johnson, phone 503-555-0102, email sarah.j@test.com"
   AI: [Should confirm and ask for address]
   
   You: "My address is 456 Oak Ave, Keizer, OR 97303"
   AI: [Should verify service area]
   
   You: "How much will it cost?"
   AI: [Should explain pricing ranges and push for on-site assessment]
   
   You: "Can you just give me a quote over the phone?"
   AI: [Should politely decline and explain why on-site is needed]
   
   You: "When can someone come out for an estimate?"
   AI: [Should check Proposal calendar and offer times]
   
   You: "Next Tuesday at 10 AM works"
   AI: [Should book appointment and confirm]
   ```

3. **Verification Steps**
   - [ ] Contact created with all details
   - [ ] Appointment booked in **Proposal** calendar (not Diagnostic)
   - [ ] Call type classified as "installation_estimate"
   - [ ] AI pushed back on phone quote request
   - [ ] Call summary includes pricing discussion

#### Expected Results

| Checkpoint | Expected | Actual | Status |
|------------|----------|--------|--------|
| Correct Calendar | ✅ Proposal calendar | ⬜ | ⬜ |
| Call Type Classification | ✅ installation_estimate | ⬜ | ⬜ |
| Pricing Pushback | ✅ Explained on-site need | ⬜ | ⬜ |
| Appointment Duration | ✅ 30-60 minutes | ⬜ | ⬜ |

#### Pass Criteria
- ✅ Appointment in Proposal calendar
- ✅ AI correctly handled pricing question
- ✅ All data captured accurately

---

### Scenario 3: Maintenance Request

**Test ID:** INBOUND-003  
**Priority:** Medium  
**Assistant:** Inbound  
**Expected Duration:** 2-4 minutes

#### Test Steps

1. **Conversation Flow**
   ```
   You: "I need my HVAC system serviced, it's been a while"
   AI: [Should ask for contact info and schedule]
   
   You: "My name is Mike Davis, phone 503-555-0103"
   AI: [Should ask for address]
   
   You: "My address is 789 Pine St, Salem, OR 97302"
   AI: [Should check calendar and offer times]
   
   You: "When can you schedule maintenance?"
   AI: [Should offer available slots]
   ```

2. **Verification Steps**
   - [ ] Contact created
   - [ ] Appointment booked (Diagnostic or Maintenance calendar)
   - [ ] Service type: "maintenance"

#### Pass Criteria
- ✅ Appointment scheduled correctly
- ✅ Service type identified

---

### Scenario 4: Emergency Situation

**Test ID:** INBOUND-004  
**Priority:** Critical  
**Assistant:** Inbound  
**Expected Duration:** 2-3 minutes

#### Test Steps

1. **Conversation Flow**
   ```
   You: "My heat is out and I have a 2-month-old baby, it's freezing"
   AI: [Should recognize emergency and prioritize]
   
   You: "This is an emergency, I need someone today"
   AI: [Should offer same-day or next available]
   
   You: "My name is Emergency Test, phone 503-555-0104"
   AI: [Should quickly collect info]
   
   You: "My address is 321 Elm St, Salem, OR 97301"
   AI: [Should book urgent appointment]
   ```

2. **Verification Steps**
   - [ ] Urgency level set to "emergency"
   - [ ] Appointment scheduled same-day or next available
   - [ ] Call summary notes health threat (baby)
   - [ ] Lead quality score reflects urgency

#### Pass Criteria
- ✅ Emergency recognized and prioritized
- ✅ Same-day/next-day appointment offered
- ✅ Health threat noted in summary

---

### Scenario 5: Warm Transfer Request

**Test ID:** INBOUND-005  
**Priority:** High  
**Assistant:** Inbound  
**Expected Duration:** 1-2 minutes

#### Test Steps

1. **Conversation Flow**
   ```
   You: "I'd like to speak with the owner about pricing"
   AI: [Should offer warm transfer to Scott]
   
   You: "Yes, please transfer me"
   AI: [Should initiate warm transfer]
   ```

2. **Verification Steps**
   - [ ] Warm transfer function called
   - [ ] Call transferred to correct number (971-712-6763)
   - [ ] Transfer context provided
   - [ ] Call summary notes transfer

#### Pass Criteria
- ✅ Transfer initiated successfully
   - ✅ Correct staff member called
   - ✅ Context passed to staff

---

### Scenario 6: Knowledge Base Testing

**Test ID:** INBOUND-006  
**Priority:** High  
**Assistant:** Inbound  
**Expected Duration:** 5-7 minutes

#### Test Questions

| Question | Expected Response | Status | Notes |
|----------|-------------------|--------|-------|
| "Do you service Portland?" | ✅ Explains extended area (35-42 miles, case-by-case) | ⬜ | ⬜ |
| "What are your hours?" | ✅ 24/7 AI, 7 AM-8:30 PM human, 8 AM-4:30 PM field | ⬜ | ⬜ |
| "Do you work on boilers?" | ✅ No, but can fit ducted/ductless and sub out removal | ⬜ | ⬜ |
| "How much is a diagnostic?" | ✅ $190 residential, $240 commercial (may vary) | ⬜ | ⬜ |
| "Do you offer discounts for veterans?" | ✅ Yes, ~10% Veteran Appreciation program | ⬜ | ⬜ |
| "What makes you different?" | ✅ Uses brand voice words (trusted, quality, professional) | ⬜ | ⬜ |
| "Do you service West Salem?" | ✅ Yes, full Salem coverage including West Salem | ⬜ | ⬜ |
| "Can you come on weekends?" | ✅ Case-by-case for emergencies affecting health | ⬜ | ⬜ |

#### Pass Criteria
- ✅ All questions answered accurately
- ✅ Uses knowledge base information
- ✅ Maintains brand voice

---

### Scenario 7: Out of Service Area

**Test ID:** INBOUND-007  
**Priority:** Medium  
**Assistant:** Inbound  
**Expected Duration:** 2-3 minutes

#### Test Steps

1. **Conversation Flow**
   ```
   You: "I'm in Eugene, can you come out?"
   AI: [Should explain extended area policy, case-by-case]
   
   You: "It's a large installation project"
   AI: [Should offer to check availability]
   ```

2. **Verification Steps**
   - [ ] Service area policy explained
   - [ ] Case-by-case basis mentioned
   - [ ] Lead still captured in GHL

#### Pass Criteria
- ✅ Handles out-of-area gracefully
- ✅ Explains policy correctly

---

### Scenario 8: Appointment Change/Reschedule

**Test ID:** INBOUND-008  
**Priority:** Medium  
**Assistant:** Inbound  
**Expected Duration:** 2-3 minutes

#### Test Steps

1. **Conversation Flow**
   ```
   You: "I need to reschedule my appointment for tomorrow"
   AI: [Should ask for appointment details and new time]
   
   You: "Can we move it to next week instead?"
   AI: [Should check calendar and reschedule]
   ```

2. **Verification Steps**
   - [ ] Original appointment identified
   - [ ] New appointment scheduled
   - [ ] Old appointment cancelled/updated
   - [ ] Confirmation sent

#### Pass Criteria
- ✅ Reschedule handled correctly
- ✅ Calendar updated accurately

---

## 📲 Outbound Call Scenarios

### Scenario 1: New Lead from Form Submission

**Test ID:** OUTBOUND-001  
**Priority:** High  
**Assistant:** Outbound  
**Trigger:** GHL webhook - `contact.created`

#### Test Steps

1. **Trigger Lead Creation**
   - Create test contact in GHL via API or dashboard
   - Webhook should trigger outbound call

2. **Expected Call Flow**
   ```
   AI: "Hi, this is [name] from Scott Valley HVAC. I'm calling because you 
        recently requested information about our heating and cooling services. 
        Is now a good time to talk for a few minutes?"
   
   [If busy]
   You: "I'm busy right now"
   AI: [Should offer callback scheduling]
   
   [If available]
   You: "Yes, I have a few minutes"
   AI: [Should qualify lead and offer appointment]
   ```

3. **Verification Steps**
   - [ ] Outbound call initiated within 1 minute of lead creation
   - [ ] Contact information used correctly
   - [ ] Call logged in GHL
   - [ ] If no answer, SMS fallback triggered (after 30 seconds)

#### Pass Criteria
- ✅ Call initiated automatically
- ✅ Lead qualified correctly
- ✅ Appointment offered if interested

---

### Scenario 2: SMS Fallback (No Answer)

**Test ID:** OUTBOUND-002  
**Priority:** High  
**Assistant:** Outbound  
**Trigger:** Call not answered or failed

#### Test Steps

1. **Setup**
   - Create lead in GHL
   - Ensure phone number is valid but won't answer
   - Wait for call attempt

2. **Expected Behavior**
   - Call attempted
   - After 30 seconds, system checks call status
   - If failed/no answer, SMS sent automatically
   - SMS includes: "Hi [Name], this is Scott Valley HVAC. We tried calling you about your HVAC inquiry. When's a good time to reach you? Reply STOP to opt out."

3. **Verification Steps**
   - [ ] SMS fallback triggered after call failure
   - [ ] SMS consent checked before sending
   - [ ] Custom fields updated: `sms_fallback_sent`, `sms_fallback_date`, `sms_fallback_reason`
   - [ ] SMS delivered successfully

#### Pass Criteria
- ✅ SMS sent automatically on call failure
- ✅ Consent respected
- ✅ Fields updated correctly

---

### Scenario 3: Web Chat Conversion

**Test ID:** OUTBOUND-003  
**Priority:** Medium  
**Assistant:** Outbound  
**Trigger:** GHL webhook - `webchat.converted`

#### Test Steps

1. **Trigger**
   - Convert web chat to lead in GHL
   - Webhook should trigger outbound call

2. **Verification Steps**
   - [ ] Call initiated
   - [ ] Lead source tagged as "web_chat"
   - [ ] Context from chat available

#### Pass Criteria
- ✅ Call triggered correctly
- ✅ Lead source accurate

---

### Scenario 4: Google/Meta Ad Lead

**Test ID:** OUTBOUND-004  
**Priority:** Medium  
**Assistant:** Outbound  
**Trigger:** GHL webhook - `ad.submission` or `google.lead` or `meta.lead`

#### Test Steps

1. **Trigger**
   - Simulate ad lead submission
   - Webhook should trigger outbound call

2. **Verification Steps**
   - [ ] Call initiated
   - [ ] Lead source tagged correctly
   - [ ] Ad campaign data captured

#### Pass Criteria
- ✅ Call triggered
- ✅ Lead source accurate

---

## 🔗 Integration Tests

### Test 1: GHL Webhook Reception

**Test ID:** INT-001  
**Priority:** Critical

#### Test Steps

1. **Send Test Webhook**
   ```bash
   curl -X POST http://localhost:8000/webhooks/ghl \
     -H "Content-Type: application/json" \
     -H "X-GHL-Signature: [signature]" \
     -d '{
       "type": "contact.created",
       "contactId": "test123",
       "locationId": "NHEXwG3xQVwKMO77jAuB"
     }'
   ```

2. **Verification Steps**
   - [ ] Webhook received (200 OK)
   - [ ] Signature verified (if configured)
   - [ ] Event processed correctly
   - [ ] Appropriate action taken (call initiated, etc.)

#### Pass Criteria
- ✅ Webhook endpoint responds
- ✅ Signature verification works
- ✅ Events processed correctly

---

### Test 2: Vapi → GHL Data Sync

**Test ID:** INT-002  
**Priority:** Critical

#### Test Steps

1. **Make Test Call**
   - Complete an inbound call with appointment booking

2. **Verification Steps**
   - [ ] Contact created/updated in GHL
   - [ ] Appointment appears in GHL calendar
   - [ ] Custom fields populated:
     - `contact.ai_call_summary`
     - `contact.call_transcript_url`
     - `contact.call_duration`
     - `contact.call_type`
     - `contact.call_outcome`
     - `contact.lead_quality_score`
     - `contact.equipment_type_tags`
   - [ ] Timeline entry created

#### Pass Criteria
- ✅ All data synced correctly
- ✅ Custom fields populated
- ✅ Timeline updated

---

### Test 3: Twilio Warm Transfer

**Test ID:** INT-003  
**Priority:** High

#### Test Steps

1. **Initiate Transfer**
   - During call, request warm transfer

2. **Verification Steps**
   - [ ] Transfer initiated via Twilio
   - [ ] Staff member receives call
   - [ ] Call context maintained
   - [ ] Transfer logged in GHL

#### Pass Criteria
- ✅ Transfer successful
- ✅ Staff receives call
- ✅ Context passed

---

## 📚 Knowledge Base Tests

### Test Suite: Business Information Accuracy

| Question Category | Test Question | Expected Answer | Status | Notes |
|-------------------|---------------|-----------------|--------|-------|
| Service Area | "Do you service Keizer?" | ✅ Yes, full coverage | ⬜ | ⬜ |
| Service Area | "Do you work in Portland?" | ✅ Extended area, case-by-case | ⬜ | ⬜ |
| Service Types | "Do you fix boilers?" | ✅ No, but can sub out removal | ⬜ | ⬜ |
| Service Types | "Do you install ductless systems?" | ✅ Yes | ⬜ | ⬜ |
| Pricing | "How much for a diagnostic?" | ✅ $190 residential, $240 commercial | ⬜ | ⬜ |
| Pricing | "Can you quote over the phone?" | ✅ No, explains on-site need | ⬜ | ⬜ |
| Hours | "What are your hours?" | ✅ 24/7 AI, 7 AM-8:30 PM human | ⬜ | ⬜ |
| Discounts | "Veteran discount?" | ✅ Yes, ~10% Veteran Appreciation | ⬜ | ⬜ |
| Emergency | "Weekend service available?" | ✅ Case-by-case for health threats | ⬜ | ⬜ |

#### Pass Criteria
- ✅ 90%+ accuracy on knowledge base questions
- ✅ Uses brand voice consistently
- ✅ Avoids prohibited words (free, cheap, low cost)

---

## 💾 Data Capture & CRM Tests

### Test 1: Contact Creation Accuracy

**Test ID:** DATA-001  
**Priority:** Critical

#### Test Data

| Field | Test Value | Captured? | Accuracy |
|-------|------------|-----------|----------|
| Full Name | "John Smith" | ⬜ | ⬜ |
| Phone | "+15035550101" | ⬜ | ⬜ |
| Email | "john@test.com" | ⬜ | ⬜ |
| Address | "123 Main St, Salem, OR 97301" | ⬜ | ⬜ |
| ZIP Code | "97301" | ⬜ | ⬜ |
| SMS Consent | `true` | ⬜ | ⬜ |

#### Pass Criteria
- ✅ All fields captured accurately
- ✅ Phone in E.164 format
- ✅ Email validated
- ✅ ZIP code extracted

---

### Test 2: Custom Fields Population

**Test ID:** DATA-002  
**Priority:** High

#### Verification Checklist

- [ ] `contact.ai_call_summary` - Contains AI-generated summary
- [ ] `contact.call_transcript_url` - URL to transcript
- [ ] `contact.sms_consent` - Boolean value
- [ ] `contact.lead_quality_score` - Numeric score (0-100)
- [ ] `contact.equipment_type_tags` - Array of tags
- [ ] `contact.call_duration` - Duration in seconds
- [ ] `contact.call_type` - Classification (service_repair, etc.)
- [ ] `contact.call_outcome` - Outcome (booked, transferred, etc.)
- [ ] `contact.vapi_called` - Boolean
- [ ] `contact.vapi_call_id` - Call ID from Vapi
- [ ] `contact.lead_source` - Source (inbound, form, ad, etc.)
- [ ] `contact.sms_fallback_sent` - Boolean
- [ ] `contact.sms_fallback_date` - Date timestamp
- [ ] `contact.sms_fallback_reason` - Reason text

#### Pass Criteria
- ✅ All 14 custom fields populated when applicable
- ✅ Data types correct
- ✅ Values accurate

---

### Test 3: Lead Quality Scoring

**Test ID:** DATA-003  
**Priority:** Medium

#### Test Cases

| Scenario | Expected Score Range | Actual | Status |
|----------|---------------------|--------|--------|
| Emergency with health threat | 85-100 | ⬜ | ⬜ |
| Complete info + appointment booked | 70-85 | ⬜ | ⬜ |
| Partial info, no booking | 40-60 | ⬜ | ⬜ |
| Out of service area | 20-40 | ⬜ | ⬜ |
| No answer, no contact | 0-20 | ⬜ | ⬜ |

#### Pass Criteria
- ✅ Scores calculated correctly
- ✅ Reflects lead quality accurately

---

## ⚠️ Error Handling & Edge Cases

### Test 1: Invalid Phone Number

**Test ID:** EDGE-001  
**Priority:** Medium

#### Test Steps
- Attempt to create contact with invalid phone
- Expected: Error handled gracefully, user asked to provide correct number

#### Pass Criteria
- ✅ Error caught
- ✅ User-friendly message
- ✅ No system crash

---

### Test 2: Calendar Unavailable

**Test ID:** EDGE-002  
**Priority:** Medium

#### Test Steps
- Request appointment when calendar has no availability
- Expected: AI offers extended dates or callback option

#### Pass Criteria
- ✅ Handles gracefully
- ✅ Offers alternatives

---

### Test 3: API Failure

**Test ID:** EDGE-003  
**Priority:** High

#### Test Steps
- Simulate GHL API failure during appointment booking
- Expected: Error logged, user informed, retry option

#### Pass Criteria
- ✅ Error logged
- ✅ User informed
- ✅ System recovers

---

### Test 4: Webhook Signature Mismatch

**Test ID:** EDGE-004  
**Priority:** High

#### Test Steps
- Send webhook with invalid signature
- Expected: Request rejected (401/403)

#### Pass Criteria
- ✅ Invalid signature rejected
- ✅ Valid signature accepted

---

## 📊 Performance & Monitoring

### Test 1: Call Response Time

**Test ID:** PERF-001  
**Priority:** Medium

#### Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Time to answer | < 3 seconds | ⬜ | ⬜ |
| Function call latency | < 2 seconds | ⬜ | ⬜ |
| GHL API response | < 1 second | ⬜ | ⬜ |
| Total call setup | < 5 seconds | ⬜ | ⬜ |

#### Pass Criteria
- ✅ All metrics within targets

---

### Test 2: Monitoring Endpoints

**Test ID:** PERF-002  
**Priority:** Medium

#### Endpoints to Test

| Endpoint | Expected | Actual | Status |
|----------|----------|--------|--------|
| `/monitoring/health` | 200 OK | ⬜ | ⬜ |
| `/monitoring/metrics/overview` | JSON metrics | ⬜ | ⬜ |
| `/monitoring/metrics/calls` | Call statistics | ⬜ | ⬜ |
| `/monitoring/metrics/bookings` | Booking stats | ⬜ | ⬜ |
| `/monitoring/metrics/leads` | Lead metrics | ⬜ | ⬜ |

#### Pass Criteria
- ✅ All endpoints respond correctly
- ✅ Metrics accurate

---

## 📝 Test Execution Log

### Test Run Summary

**Date:** _______________  
**Tester:** _______________  
**Environment:** Production / Staging / Development

### Results Overview

| Category | Total Tests | Passed | Failed | Warnings | Pass Rate |
|----------|-------------|--------|--------|----------|-----------|
| Automated Tests | 14 | ⬜ | ⬜ | ⬜ | ⬜ |
| Inbound Calls | 8 | ⬜ | ⬜ | ⬜ | ⬜ |
| Outbound Calls | 4 | ⬜ | ⬜ | ⬜ | ⬜ |
| Integration Tests | 3 | ⬜ | ⬜ | ⬜ | ⬜ |
| Knowledge Base | 9 | ⬜ | ⬜ | ⬜ | ⬜ |
| Data Capture | 3 | ⬜ | ⬜ | ⬜ | ⬜ |
| Error Handling | 4 | ⬜ | ⬜ | ⬜ | ⬜ |
| Performance | 2 | ⬜ | ⬜ | ⬜ | ⬜ |
| **TOTAL** | **47** | ⬜ | ⬜ | ⬜ | ⬜ |

### Detailed Test Log

| Test ID | Test Name | Status | Notes | Date/Time |
|---------|-----------|--------|-------|-----------|
| AUTO-001 | Vapi API Connection | ⬜ | | |
| AUTO-002 | GHL API Connection | ⬜ | | |
| ... | ... | ⬜ | | |

### Issues Found

| Issue ID | Test ID | Severity | Description | Resolution |
|----------|---------|----------|-------------|------------|
| | | | | |

### Sign-Off

**Tested By:** _______________  
**Date:** _______________  
**Approved By:** _______________  
**Date:** _______________

---

## 🎯 Test Execution Commands

### Quick Reference

```bash
# Set environment
export VAPI_API_KEY=bee0337d-41cd-49c2-9038-98cd0e18c75b

# Run automated tests
uv run python scripts/run_automated_tests.py

# Test single scenario
uv run python scripts/quick_test.py "My furnace isn't working" --phone +1XXX-XXX-XXXX

# Run all scenarios
uv run python scripts/run_test_scenarios.py --phone +1XXX-XXX-XXXX

# Check call logs
uv run python scripts/check_call_logs.py --limit 10
uv run python scripts/check_call_logs.py --call-id [CALL_ID] --tools

# Test webhook
curl -X POST http://localhost:8000/webhooks/ghl \
  -H "Content-Type: application/json" \
  -d '{"type": "contact.created", "contactId": "test123"}'
```

---

## 📌 Notes

- Update status checkboxes (⬜) as tests are completed
- Use ✅ for pass, ❌ for fail, ⚠️ for warning
- Document all issues in the Issues Found section
- Re-test failed scenarios after fixes
- Keep this document updated with each test run

---

**End of Testing Protocol**

