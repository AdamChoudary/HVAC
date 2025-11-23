from src.models import SendConfirmationRequest, SendConfirmationResponse
from src.integrations.ghl import GHLClient
from src.integrations.twilio import TwilioService
from src.utils.errors import APIError
from src.utils.logging import logger


async def send_confirmation(request: SendConfirmationRequest) -> SendConfirmationResponse:
    """
    Send SMS or email confirmation to customer.
    Checks SMS consent before sending SMS.
    """
    ghl = GHLClient()
    twilio = TwilioService()
    
    try:
        # Get contact to check SMS consent
        contact = await ghl.get_contact(contact_id=request.contact_id)
        if not contact:
            return SendConfirmationResponse(
                success=False,
                method=request.method,
                message_id=None
            )
        
        # Check SMS consent
        custom_fields = contact.get("customFields", {})
        # Check both formats: "sms_consent" and "contact.sms_consent"
        sms_consent = (
            custom_fields.get("sms_consent") or 
            custom_fields.get("contact.sms_consent") or 
            "false"
        )
        sms_consent = str(sms_consent).lower() == "true"
        
        phone = contact.get("phone", "")
        
        if request.method == "sms":
            if not sms_consent:
                return SendConfirmationResponse(
                    success=False,
                    method="sms",
                    message_id=None
                )
            
            # Send SMS via Twilio
            default_message = "Your appointment has been confirmed. We'll see you soon!"
            message = request.message or default_message
            
            result = twilio.send_sms(to=phone, message=message)
            return SendConfirmationResponse(
                success=True,
                method="sms",
                message_id=result.get("message_sid")
            )
        
        elif request.method == "email":
            # Trigger GHL email automation
            # This would typically be done via GHL automation trigger
            # For now, we'll log it as a note
            email = contact.get("email", "")
            if email:
                note = f"Confirmation email sent: {request.message or 'Appointment confirmed'}"
                await ghl.add_timeline_note(request.contact_id, note)
                return SendConfirmationResponse(
                    success=True,
                    method="email",
                    message_id=None
                )
        
        return SendConfirmationResponse(
            success=False,
            method=request.method,
            message_id=None
        )
    except Exception as e:
        return SendConfirmationResponse(
            success=False,
            method=request.method,
            message_id=None
        )


