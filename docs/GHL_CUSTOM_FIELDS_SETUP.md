# GHL Custom Fields Setup Guide

This document lists all custom fields that need to be created in GoHighLevel for the Scott Valley HVAC Voice Agent system.

## Required Custom Fields

### 1. AI Call Summary
- **Field Key**: `ai_call_summary`
- **Field Type**: Text (Long)
- **Purpose**: Stores AI-generated call summary
- **Used By**: `logCallSummary` function

### 2. Call Transcript URL
- **Field Key**: `call_transcript_url`
- **Field Type**: Text (URL)
- **Purpose**: URL to full call transcript (if stored externally)
- **Used By**: `logCallSummary` function

### 3. SMS Consent Status
- **Field Key**: `sms_consent`
- **Field Type**: Checkbox or Yes/No
- **Purpose**: Tracks whether contact has given SMS consent (TCPA compliance)
- **Used By**: `createContact`, `sendConfirmation`, SMS fallback automation

### 4. Lead Quality Score
- **Field Key**: `lead_quality_score`
- **Field Type**: Number (0-100)
- **Purpose**: Calculated lead quality score based on multiple factors
- **Used By**: `logCallSummary` function (auto-calculated)

### 5. Equipment Type Tags
- **Field Key**: `equipment_type_tags`
- **Field Type**: Text (can be comma-separated)
- **Purpose**: Stores detected equipment types from conversation (furnace, AC, heat pump, etc.)
- **Used By**: `logCallSummary` function (auto-extracted)

### 6. Call Duration
- **Field Key**: `call_duration`
- **Field Type**: Number (seconds)
- **Purpose**: Duration of the call in seconds
- **Used By**: `logCallSummary` function

### 7. Call Type
- **Field Key**: `call_type`
- **Field Type**: Dropdown or Text
- **Purpose**: Classified call type (service_repair, installation_estimate, maintenance, appointment_change, other)
- **Used By**: `logCallSummary` function

### 8. Call Outcome
- **Field Key**: `call_outcome`
- **Field Type**: Dropdown or Text
- **Purpose**: Outcome of the call (booked, transferred, no_booking, etc.)
- **Used By**: `logCallSummary` function

### 9. VAPI Called
- **Field Key**: `vapi_called`
- **Field Type**: Checkbox or Yes/No
- **Purpose**: Tracks if outbound call has been made to this contact
- **Used By**: Webhook handlers (prevents duplicate calls)

### 10. VAPI Call ID
- **Field Key**: `vapi_call_id`
- **Field Type**: Text
- **Purpose**: Stores Vapi call ID for tracking
- **Used By**: Webhook handlers

### 11. Lead Source
- **Field Key**: `lead_source`
- **Field Type**: Dropdown or Text
- **Purpose**: Source of the lead (form, webchat, google_ads, meta_ads, etc.)
- **Used By**: Webhook handlers

### 12. SMS Fallback Sent
- **Field Key**: `sms_fallback_sent`
- **Field Type**: Checkbox or Yes/No
- **Purpose**: Tracks if SMS fallback was sent after failed call
- **Used By**: SMS fallback automation

### 13. SMS Fallback Date
- **Field Key**: `sms_fallback_date`
- **Field Type**: Date/Time
- **Purpose**: Timestamp when SMS fallback was sent
- **Used By**: SMS fallback automation

### 14. SMS Fallback Reason
- **Field Key**: `sms_fallback_reason`
- **Field Type**: Text
- **Purpose**: Reason for SMS fallback (failed, no-answer, busy, etc.)
- **Used By**: SMS fallback automation

## Setup Instructions

1. **Go to GHL Dashboard** → Settings → Custom Fields
2. **Create each field** with the exact field key listed above
3. **Set appropriate field types** as specified
4. **Make fields visible** in contact views where needed
5. **Test field updates** by running a test call/contact creation

## Field Key Format

⚠️ **IMPORTANT**: Field keys must match exactly (case-sensitive). The system uses these keys to update custom fields via the GHL API.

## Optional Fields (For Future Use)

- `job_type`: Type of job (repair, installation, maintenance)
- `urgency_level`: Urgency level (emergency, urgent, standard, low)
- `preferred_appointment_window`: Customer's preferred time window
- `equipment_brand`: Brand of HVAC equipment
- `service_address_verified`: Whether service address has been verified

## Notes

- All fields are automatically created/updated by the system
- Fields can be created in any order
- If a field doesn't exist, the system will log a warning but continue
- Some fields are auto-populated (lead_quality_score, equipment_type_tags)
- Fields are updated in batches for efficiency

