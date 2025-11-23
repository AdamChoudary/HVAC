from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional, Dict, Any
import json
import asyncio
from datetime import datetime
from src.models import GHLWebhookEvent
from src.integrations.vapi import VapiClient
from src.integrations.ghl import GHLClient
from src.integrations.twilio import TwilioService
from src.utils.logging import logger
from src.utils.validation import validate_phone_number
from src.utils.webhook_security import verify_ghl_webhook_signature
from src.utils.ghl_fields import build_custom_fields_array
from src.config import settings

router = APIRouter()


@router.post("/ghl")
async def ghl_webhook(
    request: Request,
    x_ghl_signature: Optional[str] = Header(None, alias="X-GHL-Signature")
):
    """
    Handle webhooks from GoHighLevel.
    Triggers outbound calls when new leads are created.
    
    Verifies webhook signature for security if WEBHOOK_SECRET is configured.
    """
    try:
        # Get raw body for signature verification
        body_bytes = await request.body()
        
        # Verify webhook signature if secret is configured
        if settings.webhook_secret:
            if not verify_ghl_webhook_signature(body_bytes, x_ghl_signature):
                logger.warning("Webhook signature verification failed - rejecting request")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid webhook signature"
                )
            logger.info("✅ Webhook signature verified successfully")
        else:
            logger.warning("⚠️  WEBHOOK_SECRET not configured - skipping signature verification")
        
        # Parse JSON body
        body = json.loads(body_bytes.decode('utf-8'))
        # GHL webhooks can use either "event" or "type" field
        # Check both, prioritizing "type" as it's more common in GHL custom data
        event_type = body.get("type") or body.get("event", "")
        location_id = body.get("locationId", "")
        data = body.get("data", {})
        # Extract contact_id from various possible locations
        contact_id = (
            body.get("contactId") or 
            body.get("contact", {}).get("id") or
            data.get("contact", {}).get("id")
        )
        
        # Log full webhook payload for debugging
        logger.info(f"📥 Webhook received - Full payload: {body}")
        logger.info(f"📥 Webhook event_type: '{event_type}'")
        logger.info(f"📥 Webhook location_id: '{location_id}'")
        logger.info(f"📥 Webhook contact_id: '{contact_id}'")
        
        # Verify location ID matches
        # Log received location ID for debugging
        logger.info(f"Received location_id: '{location_id}', Expected: '{settings.ghl_location_id}'")
        
        # If location_id is empty, try to get it from data or allow it
        if not location_id:
            logger.warning("Location ID not provided in webhook, attempting to extract...")
            # Try to extract from data if available
            if data.get("locationId"):
                location_id = data.get("locationId")
                logger.info(f"Using location_id from data: {location_id}")
            else:
                # For now, allow webhooks without location ID (may be from different GHL setup)
                logger.warning("No location ID found in webhook, allowing to proceed (using configured location)")
                location_id = settings.ghl_location_id  # Use configured location ID
        
        # Verify location ID matches (only if we have one)
        if location_id and location_id != settings.ghl_location_id:
            logger.warning(f"Webhook from different location: received '{location_id}', expected '{settings.ghl_location_id}'")
            return {"status": "ignored", "reason": "location_mismatch"}
        
        logger.info(f"Received GHL webhook: {event_type} for contact {contact_id}")
        
        # Handle different event types
        if event_type in ["contact.created", "contact.updated"]:
            await handle_new_lead(contact_id, data)
        elif event_type == "appointment.created":
            await handle_appointment_created(contact_id, data)
        elif event_type == "form.submitted":
            await handle_form_submission(data)
        elif event_type in ["conversation.created", "chat.converted", "webchat.converted"]:
            await handle_chat_conversion(data)
        elif event_type in ["lead.created", "ad.submission", "google.lead", "meta.lead", "facebook.lead"]:
            await handle_ad_lead(data)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return {"status": "ok", "event": event_type}
    except Exception as e:
        logger.exception(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_new_lead(contact_id: Optional[str], data: Dict[str, Any]):
    """Trigger outbound call for new lead"""
    if not contact_id:
        logger.warning("No contact ID in webhook data")
        return
    
    ghl = GHLClient()
    vapi = VapiClient()
    
    try:
        # Get contact details
        contact_response = await ghl.get_contact(contact_id=contact_id)
        if not contact_response:
            logger.warning(f"Contact {contact_id} not found")
            return
        
        # GHL API can return contact nested in "contact" key or directly
        contact = contact_response.get("contact", contact_response) if isinstance(contact_response, dict) else contact_response
        
        # GHL API can return phone in different fields
        phone = (
            contact.get("phone") or 
            contact.get("phoneNumber") or
            contact.get("phoneNumbers", [{}])[0].get("number", "") if isinstance(contact.get("phoneNumbers"), list) else ""
        )
        
        if not phone:
            logger.warning(f"No phone number for contact {contact_id}")
            logger.warning(f"Contact keys: {list(contact.keys())[:20] if isinstance(contact, dict) else 'Not a dict'}")
            logger.warning(f"Contact phone fields: {[k for k in contact.keys() if 'phone' in k.lower()] if isinstance(contact, dict) else []}")
            return
        
        # Normalize phone number to E.164 format for Vapi
        try:
            phone_clean = validate_phone_number(phone)
            logger.info(f"📞 Found phone number for contact {contact_id}: {phone} -> normalized: {phone_clean}")
        except Exception as e:
            logger.warning(f"Invalid phone number format for contact {contact_id}: {phone} - {str(e)}")
            return
        
        # Check if already called (prevent duplicate calls)
        # GHL customFields can be list or dict
        custom_fields_raw = contact.get("customFields", {})
        if isinstance(custom_fields_raw, list):
            # Convert list to dict for easier access
            custom_fields = {}
            for field in custom_fields_raw:
                if isinstance(field, dict):
                    key = field.get("key") or field.get("name")
                    value = field.get("value") or field.get("field_value")
                    if key:
                        custom_fields[key] = value
        else:
            custom_fields = custom_fields_raw
        
        # Check both formats: "vapi_called" and "contact.vapi_called"
        vapi_called = (
            custom_fields.get("vapi_called") or 
            custom_fields.get("contact.vapi_called")
        )
        if vapi_called == "true" or str(vapi_called).lower() == "true":
            logger.info(f"Contact {contact_id} already called, skipping")
            return
        
        # Get outbound assistant ID from environment or data
        # Default to the outbound assistant we created
        assistant_id = (
            data.get("assistantId") or 
            settings.vapi_outbound_assistant_id or 
            "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"  # Default outbound assistant ID (newly created)
        )
        
        if not assistant_id:
            logger.warning("No assistant ID configured for outbound calls")
            return
        
        # Get phone number ID (Vapi phone number)
        # If not set, Vapi will use the default phone number from assistant
        phone_number_id = data.get("phoneNumberId") or settings.vapi_phone_number_id
        
        # Create outbound call via Vapi
        call_config = {
            "assistantId": assistant_id,
            "customer": {
                "number": phone_clean  # Use normalized phone number
            }
        }
        
        # Only add phoneNumberId if it's set
        if phone_number_id:
            call_config["phoneNumberId"] = phone_number_id
        
        call_result = await vapi.create_call(call_config)
        call_id = call_result.get("id", "")
        
        # Mark contact as called
        # GHL API expects customFields array format with "contact.{key}" format
        custom_fields_dict = {
            "vapi_called": "true",
            "vapi_call_id": call_id
        }
        
        # Add lead source if available
        if data.get("leadSource"):
            custom_fields_dict["lead_source"] = data.get("leadSource")
        
        custom_fields_update = build_custom_fields_array(custom_fields_dict)
        
        await ghl.update_contact(
            contact_id=contact_id,
            contact_data={
                "customFields": custom_fields_update
            }
        )
        
        logger.info(f"Outbound call initiated for contact {contact_id}, call ID: {call_id}")
        
        # Set up SMS fallback check (check call status after delay)
        asyncio.create_task(check_call_and_send_sms_fallback(call_id, contact_id, phone_clean))
    except Exception as e:
        logger.exception(f"Error handling new lead: {str(e)}")


async def check_call_and_send_sms_fallback(call_id: str, contact_id: str, phone: str):
    """
    Check call status after delay and send SMS if call failed/unanswered.
    Waits 30 seconds, then checks Vapi call status.
    """
    # Wait 30 seconds for call to complete or fail
    await asyncio.sleep(30)
    
    vapi = VapiClient()
    ghl = GHLClient()
    twilio = TwilioService()
    
    try:
        # Get call status from Vapi
        call_info = await vapi.get_call(call_id)
        call_status = call_info.get("status", "").lower()
        
        # Check if call was unsuccessful
        failed_statuses = ["failed", "no-answer", "busy", "canceled", "no-answer", "busy"]
        if call_status in failed_statuses:
            logger.info(f"Call {call_id} failed with status: {call_status}, checking SMS fallback eligibility")
            
            # Get contact to check SMS consent
            contact_response = await ghl.get_contact(contact_id=contact_id)
            if not contact_response:
                logger.warning(f"Contact {contact_id} not found for SMS fallback")
                return
            
            contact = contact_response.get("contact", contact_response) if isinstance(contact_response, dict) else contact_response
            custom_fields_raw = contact.get("customFields", {})
            
            # Handle customFields format (list or dict)
            if isinstance(custom_fields_raw, list):
                custom_fields = {}
                for field in custom_fields_raw:
                    if isinstance(field, dict):
                        key = field.get("key") or field.get("name")
                        value = field.get("value") or field.get("field_value")
                        if key:
                            custom_fields[key] = value
            else:
                custom_fields = custom_fields_raw
            
            # Check both formats: "sms_consent" and "contact.sms_consent"
            sms_consent = (
                custom_fields.get("sms_consent") or 
                custom_fields.get("contact.sms_consent") or 
                "false"
            )
            sms_consent = str(sms_consent).lower() == "true"
            
            sms_fallback_sent = (
                custom_fields.get("sms_fallback_sent") or 
                custom_fields.get("contact.sms_fallback_sent") or 
                "false"
            )
            sms_fallback_sent = str(sms_fallback_sent).lower() == "true"
            
            # Send SMS fallback if consent given and not already sent
            if sms_consent and not sms_fallback_sent:
                sms_message = (
                    "Hi! This is Scott Valley HVAC. We tried to reach you but couldn't connect. "
                    "Would you like to schedule an appointment? Reply YES or call us at 971-712-6763. "
                    "Thank you!"
                )
                
                try:
                    result = twilio.send_sms(to=phone, message=sms_message)
                    logger.info(f"✅ SMS fallback sent to {phone} for failed call {call_id}, SMS SID: {result.get('message_sid')}")
                    
                    # Mark SMS sent in GHL
                    sms_fallback_fields = {
                        "sms_fallback_sent": "true",
                        "sms_fallback_date": datetime.now().isoformat(),
                        "sms_fallback_reason": call_status
                    }
                    await ghl.update_contact(
                        contact_id=contact_id,
                        contact_data={
                            "customFields": build_custom_fields_array(sms_fallback_fields)
                        }
                    )
                except Exception as sms_error:
                    logger.error(f"Failed to send SMS fallback to {phone}: {str(sms_error)}")
            elif not sms_consent:
                logger.info(f"SMS consent not given for contact {contact_id}, skipping SMS fallback")
            elif sms_fallback_sent:
                logger.info(f"SMS fallback already sent for contact {contact_id}, skipping")
        else:
            logger.info(f"Call {call_id} succeeded with status: {call_status}, no SMS fallback needed")
    except Exception as e:
        logger.exception(f"Error in SMS fallback check for call {call_id}: {str(e)}")


async def handle_appointment_created(contact_id: Optional[str], data: Dict[str, Any]):
    """Handle appointment creation event"""
    logger.info(f"Appointment created for contact {contact_id}")
    # Could trigger confirmation SMS/email here if needed


async def handle_form_submission(data: Dict[str, Any]):
    """Handle form submission event"""
    logger.info("Form submission received")
    # Extract contact_id from form submission data
    contact_id = (
        data.get("contactId") or
        data.get("contact", {}).get("id") or
        data.get("form", {}).get("contactId")
    )
    
    if contact_id:
        # Trigger outbound call for form submissions
        logger.info(f"Form submission for contact {contact_id}, triggering outbound call")
        await handle_new_lead(contact_id, data)
    else:
        logger.warning("No contact ID found in form submission data")


async def handle_chat_conversion(data: Dict[str, Any]):
    """Handle web chat conversion event"""
    logger.info("Chat conversion received")
    # Extract contact_id from chat conversion data
    contact_id = (
        data.get("contactId") or
        data.get("contact", {}).get("id") or
        data.get("conversation", {}).get("contactId") or
        data.get("chat", {}).get("contactId")
    )
    
    if contact_id:
        logger.info(f"Chat conversion for contact {contact_id}, triggering outbound call")
        await handle_new_lead(contact_id, data)
    else:
        logger.warning("No contact ID found in chat conversion data")


async def handle_ad_lead(data: Dict[str, Any]):
    """Handle Google/Meta ad lead submission"""
    logger.info("Ad lead submission received")
    # Extract contact_id from ad lead data
    contact_id = (
        data.get("contactId") or
        data.get("contact", {}).get("id") or
        data.get("lead", {}).get("contactId") or
        data.get("ad", {}).get("contactId")
    )
    
    # Extract lead source for tracking
    lead_source = (
        data.get("source") or
        data.get("leadSource") or
        data.get("ad", {}).get("platform") or
        "unknown"
    )
    
    if contact_id:
        logger.info(f"Ad lead from {lead_source} for contact {contact_id}, triggering outbound call")
        # Add lead source to data for tracking
        if "leadSource" not in data:
            data["leadSource"] = lead_source
        await handle_new_lead(contact_id, data)
    else:
        logger.warning("No contact ID found in ad lead data")


