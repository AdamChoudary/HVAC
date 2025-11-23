# 🧪 Scott Valley HVAC - Customer Testing Protocol

**Version:** 1.0  
**Date:** November 2025  
**Purpose:** Step-by-step testing guide for customer acceptance testing

---

## 📋 Table of Contents

1. [Pre-Testing Setup](#pre-testing-setup)
2. [Inbound Call Testing](#inbound-call-testing)
3. [Outbound Call Testing](#outbound-call-testing)
4. [Automation Workflow Testing](#automation-workflow-testing)
5. [Data Capture & CRM Testing](#data-capture--crm-testing)
6. [Integration Testing](#integration-testing)
7. [Edge Cases & Error Handling](#edge-cases--error-handling)
8. [Performance & Reliability](#performance--reliability)
9. [Sign-Off Checklist](#sign-off-checklist)

---

## ✅ Pre-Testing Setup

### Required Access

- [ ] Vapi.ai Dashboard access
- [ ] GoHighLevel (GHL) Dashboard access
- [ ] Twilio Dashboard access (if needed)
- [ ] Test phone numbers (at least 2)
- [ ] GHL API credentials verified
- [ ] All webhooks configured in GHL

### System Configuration Checklist

- [ ] Inbound assistant configured in Vapi
- [ ] Outbound assistant configured in Vapi
- [ ] Phone number assigned to Vapi assistant
- [ ] GHL calendars created (Diagnostic, Proposal)
- [ ] GHL custom fields created (all 14 fields)
- [ ] GHL webhooks configured:
  - [ ] Contact Created → Outbound Call
  - [ ] Form Submitted → Outbound Call
  - [ ] Web Chat Converted → Outbound Call
  - [ ] Google/Meta Ad Lead → Outbound Call
- [ ] SMS fallback enabled in Twilio
- [ ] FastAPI server running and accessible

### Test Data Preparation

**Test Contacts to Create:**
- Contact 1: John Smith, +1-503-555-0101, john.smith@test.com, 123 Main St, Salem, OR 97301
- Contact 2: Sarah Johnson, +1-503-555-0102, sarah.j@test.com, 456 Oak Ave, Keizer, OR 97303
- Contact 3: Mike Davis, +1-503-555-0103, mike.d@test.com, 789 Pine St, Salem, OR 97302

**Test Scenarios:**
- Emergency call (no heat, baby in house)
- Regular service request
- Installation inquiry
- Out-of-service-area call
- Appointment reschedule

---

## 📞 Inbound Call Testing

### Test 1: Basic Service Request

**Objective:** Verify AI can handle a standard service call and book an appointment

**Steps:**
1. Call the Vapi phone number
2. When AI answers, say: "Hello, I need help with my heating system"
3. AI should greet you warmly and ask for your name
4. Provide: "My name is John Smith"
5. AI should ask for phone number
6. Provide: "503-555-0101"
7. AI should ask for address
8. Provide: "123 Main St, Salem, Oregon 97301"
9. AI should ask for email (optional)
10. Provide: "john.smith@test.com" or say "I don't have one"
11. AI should ask about SMS consent
12. Say: "Yes, I'd like text confirmations"
13. AI should check calendar and offer appointment times
14. Select a time: "Tomorrow at 2 PM works"
15. AI should confirm booking and send confirmation

**Expected Results:**
- [ ] Contact created in GHL with all information
- [ ] Appointment booked in Diagnostic calendar
- [ ] SMS confirmation sent (if consent given)
- [ ] Call summary logged in GHL timeline
- [ ] Custom fields populated:
  - [ ] `contact.ai_call_summary` - Contains summary
  - [ ] `contact.call_type` - Set to "service_repair"
  - [ ] `contact.call_outcome` - Set to "booked"
  - [ ] `contact.sms_consent` - Set to "true"
  - [ ] `contact.lead_quality_score` - Calculated score

**Pass Criteria:** ✅ All checkboxes must be checked

---

### Test 2: Emergency Call Handling

**Objective:** Verify AI prioritizes emergency situations

**Steps:**
1. Call the Vapi phone number
2. Say: "My heat is out and I have a 2-month-old baby, it's freezing!"
3. AI should recognize urgency immediately
4. AI should ask for essential info quickly (name, phone, address)
5. AI should offer same-day or next-day appointment
6. Complete the booking process

**Expected Results:**
- [ ] AI recognizes emergency immediately
- [ ] Urgency level set to "emergency"
- [ ] Same-day or next-day appointment offered
- [ ] Appointment booked with emergency priority
- [ ] Call summary notes health threat (baby)
- [ ] Lead quality score reflects urgency (85-100)

**Pass Criteria:** ✅ Emergency recognized and prioritized

---

### Test 3: Installation/Estimate Request

**Objective:** Verify AI routes to correct calendar and handles pricing questions

**Steps:**
1. Call the Vapi phone number
2. Say: "I'm looking to replace my old air conditioning system"
3. Provide contact information
4. When asked about pricing, say: "How much will it cost?"
5. AI should explain pricing ranges and push for on-site assessment
6. Say: "Can you just give me a quote over the phone?"
7. AI should politely decline and explain why on-site is needed
8. Complete booking for estimate appointment

**Expected Results:**
- [ ] Appointment booked in **Proposal** calendar (not Diagnostic)
- [ ] Call type classified as "installation_estimate"
- [ ] AI pushed back on phone quote request
- [ ] Appointment duration set to 30-60 minutes
- [ ] Call summary includes pricing discussion

**Pass Criteria:** ✅ Correct calendar used, pricing handled appropriately

---

### Test 4: Knowledge Base Accuracy

**Objective:** Verify AI provides accurate business information

**Test Questions (Ask each one):**

| Question | Expected Answer | Status |
|----------|----------------|--------|
| "Do you service Portland?" | Explains extended area (35-42 miles, case-by-case) | ⬜ |
| "What are your hours?" | 24/7 AI, 7 AM-8:30 PM human, 8 AM-4:30 PM field | ⬜ |
| "Do you work on boilers?" | No, but can fit ducted/ductless and sub out removal | ⬜ |
| "How much is a diagnostic?" | $190 residential, $240 commercial (may vary) | ⬜ |
| "Do you offer discounts for veterans?" | Yes, ~10% Veteran Appreciation program | ⬜ |
| "Do you service West Salem?" | Yes, full Salem coverage including West Salem | ⬜ |
| "Can you come on weekends?" | Case-by-case for emergencies affecting health | ⬜ |
| "What makes you different?" | Uses brand voice words (trusted, quality, professional) | ⬜ |

**Pass Criteria:** ✅ 90%+ accuracy on knowledge base questions

---

### Test 5: Warm Transfer

**Objective:** Verify AI can transfer calls to human staff

**Steps:**
1. Call the Vapi phone number
2. Complete basic information collection
3. Say: "I'd like to speak with the owner about pricing"
4. AI should offer warm transfer to Scott
5. Say: "Yes, please transfer me"
6. AI should initiate transfer

**Expected Results:**
- [ ] AI offers warm transfer appropriately
- [ ] Transfer initiated to correct number (971-712-6763)
- [ ] Call context maintained during transfer
- [ ] Transfer logged in GHL
- [ ] Call summary notes transfer occurred

**Pass Criteria:** ✅ Transfer successful, staff receives call

---

### Test 6: Out of Service Area

**Objective:** Verify AI handles out-of-area requests gracefully

**Steps:**
1. Call the Vapi phone number
2. Say: "I'm in Eugene, can you come out?"
3. Provide contact information
4. AI should explain extended area policy

**Expected Results:**
- [ ] Service area policy explained
- [ ] Case-by-case basis mentioned
- [ ] Lead still captured in GHL
- [ ] Contact created with address
- [ ] Call summary notes out-of-area request

**Pass Criteria:** ✅ Handles gracefully, explains policy

---

## 📲 Outbound Call Testing

### Test 7: New Lead from Form Submission

**Objective:** Verify outbound calling triggers automatically

**Steps:**
1. Create a new contact in GHL dashboard (or via form submission)
   - Name: Test Lead
   - Phone: +1-503-555-0199
   - Email: test.lead@example.com
   - Address: 321 Test St, Salem, OR 97301
2. Wait 1-2 minutes
3. Answer the call when it comes

**Expected Results:**
- [ ] Outbound call initiated within 1-2 minutes of lead creation
- [ ] AI introduces as "Sarah from Scott Valley HVAC"
- [ ] AI mentions they're calling because lead requested info
- [ ] AI asks if it's a good time to talk
- [ ] If you say "I'm busy", AI offers callback scheduling
- [ ] If you say "Yes", AI qualifies lead and offers appointment
- [ ] Call logged in GHL with lead source

**Pass Criteria:** ✅ Call triggered automatically, handled professionally

---

### Test 8: SMS Fallback (No Answer)

**Objective:** Verify SMS sent when call fails or not answered

**Steps:**
1. Create a new lead in GHL
2. Ensure phone number is valid but won't answer
3. Wait for call attempt
4. Don't answer the call (or let it fail)
5. Wait 30-60 seconds after call attempt
6. Check SMS inbox

**Expected Results:**
- [ ] Call attempted to lead
- [ ] After 30 seconds, system checks call status
- [ ] If call failed/no answer, SMS sent automatically
- [ ] SMS includes: "Hi [Name], this is Scott Valley HVAC. We tried calling you about your HVAC inquiry. When's a good time to reach you? Reply STOP to opt out."
- [ ] Custom fields updated:
  - [ ] `contact.sms_fallback_sent` - Set to "true"
  - [ ] `contact.sms_fallback_date` - Timestamp set
  - [ ] `contact.sms_fallback_reason` - Reason logged

**Pass Criteria:** ✅ SMS sent automatically on call failure

---

### Test 9: Web Chat Conversion Trigger

**Objective:** Verify web chat conversions trigger outbound calls

**Steps:**
1. In GHL dashboard, convert a web chat to a lead
2. Wait 1-2 minutes
3. Answer the call

**Expected Results:**
- [ ] Webhook received from GHL (`webchat.converted`)
- [ ] Outbound call initiated
- [ ] Lead source tagged as "web_chat"
- [ ] Call context includes chat information

**Pass Criteria:** ✅ Call triggered from web chat conversion

---

### Test 10: Google/Meta Ad Lead Trigger

**Objective:** Verify ad lead submissions trigger outbound calls

**Steps:**
1. Simulate ad lead submission in GHL (or use actual ad form)
2. Wait 1-2 minutes
3. Answer the call

**Expected Results:**
- [ ] Webhook received from GHL (`ad.submission` or `google.lead` or `meta.lead`)
- [ ] Outbound call initiated
- [ ] Lead source tagged correctly
- [ ] Ad campaign data captured

**Pass Criteria:** ✅ Call triggered from ad lead

---

## 🔄 Automation Workflow Testing

### Test 11: Complete Lead-to-Booking Flow

**Objective:** Verify end-to-end automation from lead to booked appointment

**Steps:**
1. Submit a lead form on your website (or create in GHL)
2. System should:
   - Create contact in GHL
   - Trigger outbound call
   - If call answered: Qualify and book appointment
   - If call not answered: Send SMS fallback
3. Verify all steps completed

**Expected Results:**
- [ ] Contact created in GHL
- [ ] Outbound call triggered
- [ ] Appointment booked (if call successful)
- [ ] OR SMS sent (if call failed)
- [ ] All custom fields populated
- [ ] Lead quality score calculated
- [ ] Timeline entries created

**Pass Criteria:** ✅ Complete flow works end-to-end

---

### Test 12: Appointment Confirmation Automation

**Objective:** Verify confirmation SMS/email sent after booking

**Steps:**
1. Complete an inbound call and book appointment
2. Provide SMS consent
3. Wait for confirmation

**Expected Results:**
- [ ] SMS confirmation sent immediately after booking
- [ ] SMS includes: Date, time, service type, address
- [ ] Email confirmation sent (if email provided and no SMS consent)
- [ ] Confirmation logged in GHL timeline

**Pass Criteria:** ✅ Confirmation sent automatically

---

### Test 13: Call Summary Logging

**Objective:** Verify call summaries logged automatically

**Steps:**
1. Complete any call (inbound or outbound)
2. Check GHL contact timeline

**Expected Results:**
- [ ] Call summary logged in GHL timeline
- [ ] `contact.ai_call_summary` field populated
- [ ] `contact.call_transcript_url` field populated (if available)
- [ ] `contact.call_duration` field populated
- [ ] `contact.call_type` field populated
- [ ] `contact.call_outcome` field populated
- [ ] Summary includes: Customer need, service type, outcome, next steps

**Pass Criteria:** ✅ All call data logged correctly

---

## 💾 Data Capture & CRM Testing

### Test 14: Contact Data Accuracy

**Objective:** Verify all contact information captured correctly

**Steps:**
1. Complete a call providing:
   - Name: "Jane Doe"
   - Phone: "503-555-9876"
   - Email: "jane.doe@example.com"
   - Address: "789 Elm Street, Salem, OR 97302"
   - ZIP: "97302"
2. Check contact in GHL dashboard

**Expected Results:**
- [ ] First name: "Jane"
- [ ] Last name: "Doe"
- [ ] Phone: "+15035559876" (E.164 format)
- [ ] Email: "jane.doe@example.com"
- [ ] Address: "789 Elm Street"
- [ ] ZIP: "97302"
- [ ] All data accurate and formatted correctly

**Pass Criteria:** ✅ 100% data accuracy

---

### Test 15: Custom Fields Population

**Objective:** Verify all 14 custom fields populated when applicable

**Checklist:**
- [ ] `contact.ai_call_summary` - AI-generated summary
- [ ] `contact.call_transcript_url` - URL to transcript
- [ ] `contact.sms_consent` - Boolean value
- [ ] `contact.lead_quality_score` - Numeric score (0-100)
- [ ] `contact.equipment_type_tags` - Array of tags
- [ ] `contact.call_duration` - Duration in seconds
- [ ] `contact.call_type` - Classification
- [ ] `contact.call_outcome` - Outcome (booked, transferred, etc.)
- [ ] `contact.vapi_called` - Boolean
- [ ] `contact.vapi_call_id` - Call ID from Vapi
- [ ] `contact.lead_source` - Source (inbound, form, ad, etc.)
- [ ] `contact.sms_fallback_sent` - Boolean
- [ ] `contact.sms_fallback_date` - Date timestamp
- [ ] `contact.sms_fallback_reason` - Reason text

**Pass Criteria:** ✅ All applicable fields populated

---

### Test 16: Lead Quality Scoring

**Objective:** Verify lead quality scores calculated correctly

**Test Cases:**

| Scenario | Expected Score Range | Actual | Status |
|----------|---------------------|--------|--------|
| Emergency with health threat | 85-100 | ⬜ | ⬜ |
| Complete info + appointment booked | 70-85 | ⬜ | ⬜ |
| Partial info, no booking | 40-60 | ⬜ | ⬜ |
| Out of service area | 20-40 | ⬜ | ⬜ |
| No answer, no contact | 0-20 | ⬜ | ⬜ |

**Pass Criteria:** ✅ Scores reflect lead quality accurately

---

## 🔗 Integration Testing

### Test 17: GHL Webhook Reception

**Objective:** Verify webhooks received and processed correctly

**Steps:**
1. Create a contact in GHL dashboard
2. Check FastAPI server logs
3. Verify webhook processed

**Expected Results:**
- [ ] Webhook received by FastAPI server
- [ ] Signature verified (if configured)
- [ ] Event processed correctly
- [ ] Appropriate action taken (call initiated, etc.)
- [ ] No errors in logs

**Pass Criteria:** ✅ Webhooks working correctly

---

### Test 18: Calendar Integration

**Objective:** Verify calendar availability and booking

**Steps:**
1. During a call, ask AI to check availability
2. AI should check Diagnostic or Proposal calendar
3. AI should offer available times
4. Book an appointment

**Expected Results:**
- [ ] Calendar availability checked correctly
- [ ] Available slots returned
- [ ] Appointment booked in correct calendar
- [ ] Appointment appears in GHL calendar
- [ ] Appointment details accurate

**Pass Criteria:** ✅ Calendar integration working

---

### Test 19: SMS Integration

**Objective:** Verify SMS sending works

**Steps:**
1. Complete a call with SMS consent
2. Book an appointment
3. Check SMS inbox

**Expected Results:**
- [ ] SMS sent successfully
- [ ] SMS content accurate
- [ ] SMS consent respected (no SMS if consent not given)
- [ ] SMS delivery confirmed

**Pass Criteria:** ✅ SMS integration working

---

## ⚠️ Edge Cases & Error Handling

### Test 20: Invalid Phone Number

**Objective:** Verify system handles invalid phone numbers

**Steps:**
1. During call, provide invalid phone: "123"
2. AI should ask for correct number

**Expected Results:**
- [ ] Error caught gracefully
- [ ] User-friendly message
- [ ] AI asks for correct number
- [ ] No system crash

**Pass Criteria:** ✅ Handles invalid data gracefully

---

### Test 21: Calendar Unavailable

**Objective:** Verify AI handles no availability

**Steps:**
1. During call, request appointment
2. If calendar shows no availability, observe AI response

**Expected Results:**
- [ ] AI handles gracefully
- [ ] Offers extended dates
- [ ] Suggests callback option
- [ ] Still captures lead information

**Pass Criteria:** ✅ Handles no availability appropriately

---

### Test 22: API Failure Recovery

**Objective:** Verify system recovers from API failures

**Steps:**
1. Simulate GHL API failure (temporarily disconnect)
2. Attempt to create contact or book appointment
3. Reconnect API
4. Retry operation

**Expected Results:**
- [ ] Error logged
- [ ] User informed appropriately
- [ ] System recovers when API reconnects
- [ ] Operation can be retried

**Pass Criteria:** ✅ System recovers from failures

---

## 📊 Performance & Reliability

### Test 23: Call Response Time

**Objective:** Verify system responds quickly

**Metrics to Check:**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Time to answer | < 3 seconds | ⬜ | ⬜ |
| Function call latency | < 2 seconds | ⬜ | ⬜ |
| GHL API response | < 1 second | ⬜ | ⬜ |
| Total call setup | < 5 seconds | ⬜ | ⬜ |

**Pass Criteria:** ✅ All metrics within targets

---

### Test 24: System Uptime

**Objective:** Verify system is available 24/7

**Steps:**
1. Test calls at different times:
   - [ ] Business hours (8 AM - 5 PM)
   - [ ] After hours (6 PM - 11 PM)
   - [ ] Late night (11 PM - 2 AM)
   - [ ] Early morning (2 AM - 8 AM)
   - [ ] Weekend

**Expected Results:**
- [ ] All calls answered
- [ ] No downtime during test period
- [ ] Consistent performance

**Pass Criteria:** ✅ 24/7 availability confirmed

---

### Test 25: Concurrent Calls

**Objective:** Verify system handles multiple calls simultaneously

**Steps:**
1. Have 2-3 people call simultaneously
2. Verify all calls handled

**Expected Results:**
- [ ] All calls answered
- [ ] No dropped calls
- [ ] Performance maintained
- [ ] No errors

**Pass Criteria:** ✅ Handles concurrent calls

---

## ✅ Sign-Off Checklist

### Functional Requirements

- [ ] Inbound calls answered 24/7
- [ ] Outbound calls triggered automatically
- [ ] Appointments booked correctly
- [ ] SMS fallback working
- [ ] Warm transfers functional
- [ ] Knowledge base accurate
- [ ] Data capture complete
- [ ] Custom fields populated
- [ ] Lead scoring working

### Technical Requirements

- [ ] All integrations working (Vapi, GHL, Twilio)
- [ ] Webhooks configured and functional
- [ ] Error handling robust
- [ ] Performance acceptable
- [ ] System reliable (24/7 uptime)

### Business Requirements

- [ ] Brand voice maintained
- [ ] Customer experience positive
- [ ] Data accuracy 100%
- [ ] Automation reduces manual work
- [ ] System meets business goals

---

## 📝 Test Execution Log

**Date:** _______________  
**Tester:** _______________  
**Environment:** Production / Staging

### Results Summary

| Category | Tests | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
| Inbound Calls | 6 | ⬜ | ⬜ | ⬜ |
| Outbound Calls | 4 | ⬜ | ⬜ | ⬜ |
| Automations | 3 | ⬜ | ⬜ | ⬜ |
| Data Capture | 3 | ⬜ | ⬜ | ⬜ |
| Integrations | 3 | ⬜ | ⬜ | ⬜ |
| Edge Cases | 3 | ⬜ | ⬜ | ⬜ |
| Performance | 3 | ⬜ | ⬜ | ⬜ |
| **TOTAL** | **25** | ⬜ | ⬜ | ⬜ |

### Issues Found

| Issue # | Test ID | Severity | Description | Resolution |
|---------|---------|----------|-------------|------------|
| | | | | |

### Sign-Off

**Tested By:** _______________  
**Date:** _______________  
**Approved By:** _______________  
**Date:** _______________

**Status:** ⬜ Approved  ⬜ Needs Revision  ⬜ Rejected

---

## 📞 Support & Questions

If you encounter issues during testing:

1. **Check Logs:**
   - Vapi Dashboard: Call logs and transcripts
   - GHL Dashboard: Contact timeline and custom fields
   - FastAPI Server: Application logs

2. **Common Issues:**
   - **No outbound call:** Check webhook configuration in GHL
   - **SMS not sent:** Verify Twilio credentials and SMS consent
   - **Appointment not booked:** Check calendar availability and GHL API status
   - **Data missing:** Verify custom fields exist in GHL

3. **Contact Support:**
   - Technical issues: [Your support contact]
   - Configuration questions: [Your support contact]

---

**End of Customer Testing Protocol**

