# Scott Valley HVAC — AI Voice Agent Technical Requirements

## Project Overview
Deploy AI voice automation system using Vapi.ai integrated with GoHighLevel (GHL) for inbound call handling and outbound lead engagement for HVAC business operations.

---

## 1. Voice Agent Configuration (Vapi.ai)

### Inbound Assistant
- **Voice Profile**: Female voice, professional HVAC service tone
- **Call Handling**: 24/7 availability (business hours + after-hours modes)
- **Core Functions**:
  - Call type classification (service/repair, install/estimate, maintenance, appointment changes)
  - Customer intake and qualification
  - Calendar booking with appointment type routing
  - Warm transfer capability to human staff
  - Call summary and transcript generation

### Outbound Assistant
- **Trigger Events**: New lead entry in GHL from multiple sources
- **Call Behavior**: Immediate outreach attempts with SMS fallback
- **Functions**:
  - Lead qualification
  - Appointment scheduling
  - Confirmation delivery

---

## 2. Data Capture Requirements

### Required Contact Fields
- Full name
- Mobile phone (with SMS consent flag)
- Email address
- Service address with ZIP code
- Job type and equipment details
- Urgency level
- Preferred appointment windows

### Call Metadata
- Call duration and timestamp
- Caller type classification
- Transcript and AI summary
- Disposition/outcome status
- Lead source attribution

---

## 3. Vapi.ai Assistant Functions

### Function: `classifyCallType`
Analyze caller intent and route to appropriate handling flow

### Function: `checkCalendarAvailability`
Query GHL calendar API for available appointment slots by service type

### Function: `bookAppointment`
Create calendar event in GHL with customer details and service type

### Function: `createContact`
Create or update contact record in GHL with captured information

### Function: `sendConfirmation`
Trigger SMS/email confirmation via GHL automation

### Function: `initiateWarmTransfer`
Connect caller to appropriate staff member via Twilio transfer

### Function: `logCallSummary`
Attach transcript and AI notes to GHL contact timeline

---

## 4. Integration Architecture

### Vapi → GHL Integration
- **Method**: REST API + Webhooks
- **Authentication**: GHL API OAuth/API Key
- **Real-time Events**:
  - Call started/ended
  - Appointment booked
  - Contact created/updated
  - Call summary attached

### GHL Webhook Endpoints (to trigger Vapi)
- New lead created (for outbound calling)
- Form submission events
- Web chat conversions
- Google/Meta lead ad submissions

### Twilio Integration
- **Phone Number**: Client-provided or new provisioning
- **Inbound**: Route to Vapi assistant
- **Outbound**: Vapi-initiated calls to leads
- **Warm Transfer**: SIP transfer to staff phone numbers
- **SMS Fallback**: Programmable SMS for unanswered outbound calls

---

## 5. GoHighLevel Configuration

### Pipelines
- **Service Pipeline**: Stages for service/repair/maintenance requests
- **Sales Pipeline**: Stages for install/estimate opportunities

### Calendars
- **Service Calendar**: Repair and maintenance bookings
- **Sales/Estimate Calendar**: Installation consultation slots
- **Settings**: Appointment buffers, blackout times, business hours

### Automations
- SMS/email appointment confirmations
- Team notifications for new bookings
- Follow-up sequences for unbooked leads
- Reminder workflows

### Custom Fields
- AI call summary
- Call transcript URL
- SMS consent status
- Lead quality score
- Equipment type tags

---

## 6. Knowledge Base Structure

### Business Information
- Company hours (regular + emergency)
- Service areas and ZIP codes
- Emergency service policy
- Maintenance plan offerings

### Service Catalog
- Repair services and typical timeframes
- Installation options and equipment brands
- Maintenance packages and pricing structure
- Emergency vs. scheduled service definitions

### Scheduling Rules
- Appointment duration by service type
- Cancellation policy
- No-show handling
- Same-day vs. scheduled booking criteria

### Transfer Directory
- Staff names and extensions
- Transfer triggers and scenarios
- Escalation protocols

### FAQ Responses
- Common customer questions
- Pricing guidance scripts
- Warranty and guarantee information

---

## 7. Podium Data Migration

### Export Requirements
- Contact list with phone/email/address
- Message thread history (if exportable)
- Call logs and recordings (if accessible)
- Review links and reputation data
- Lead source tags and notes
- SMS consent records

### Import Mapping
- Podium contacts → GHL contacts
- Custom field mapping for notes/tags
- Phone number normalization (E.164 format)
- Email validation and cleanup
- Lead source attribution preservation

---

## 8. Security & Compliance

### Data Handling
- PII encryption in transit and at rest
- SMS consent tracking (TCPA compliance)
- Call recording consent notifications
- Data retention policies

### API Security
- Secure credential storage (environment variables)
- Webhook signature verification
- Rate limiting and error handling
- API key rotation procedures

---

## 9. Testing & Quality Assurance

### Test Scenarios
- Inbound calls for each service type
- After-hours call handling
- Calendar booking conflicts
- Warm transfer functionality
- Outbound call attempts and SMS fallback
- GHL data synchronization accuracy
- Knowledge base query accuracy

### Monitoring
- Call success/failure rates
- Booking conversion metrics
- Warm transfer completion rates
- API error logging
- Response time tracking

---

## 10. Required Access & Credentials

### Client to Provide
- **Vapi.ai**: Account access or API key
- **Twilio**: Account SID and Auth Token (or provision new)
- **GoHighLevel**: Admin API access, Location ID
- **Podium**: Export access or admin credentials
- **Phone Numbers**: Primary business line, warm transfer destinations
- **Service Details**: ZIP code coverage, appointment types, staff directory

### Configuration Details Needed
- Marketing lead sources (form URLs, webhook endpoints)
- Business hours and holiday schedule
- Appointment duration standards
- Pricing guidance boundaries
- Brand voice and tone guidelines

---

## 11. Success Metrics

### Performance KPIs
- Call answer rate (target: 95%+)
- Booking conversion rate
- Average call duration
- Warm transfer success rate
- Lead contact speed (outbound)
- Customer satisfaction scores

### Technical Metrics
- API uptime and latency
- Error rates and failed transactions
- Data sync accuracy
- System response times

---

## Implementation Notes

### Phase 1: Inbound Voice Agent (Weeks 1-2)
Core assistant with booking and warm transfer capabilities

### Phase 2: Outbound Lead Engine (Weeks 2-3)
Automated outreach for new marketing leads

### Phase 3: Optimization (Weeks 3-4)
Script refinement, knowledge base expansion, performance tuning

### Ongoing
Continuous monitoring, knowledge base updates, conversation flow improvements