from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
from typing import Optional, Dict, Any
from src.config import settings
from src.utils.errors import TwilioAPIError
from src.utils.logging import logger


class TwilioService:
    def __init__(self):
        self.client = TwilioClient(
            settings.get_twilio_account_sid(),
            settings.twilio_auth_token
        )
        self.phone_number = settings.twilio_phone_number
    
    def send_sms(
        self, 
        to: str, 
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS message"""
        from_num = from_number or self.phone_number
        message_obj = self.client.messages.create(
            body=message,
            from_=from_num,
            to=to
        )
        logger.info(f"SMS sent to {to}, SID: {message_obj.sid}")
        return {
            "success": True,
            "message_sid": message_obj.sid,
            "status": message_obj.status
        }
    
    def initiate_warm_transfer(
        self,
        call_sid: str,
        to: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate warm transfer to staff member"""
        from_num = from_number or self.phone_number
        call = self.client.calls(call_sid).update(
            twiml=f'<Response><Dial><Number>{to}</Number></Dial></Response>'
        )
        logger.info(f"Warm transfer initiated: {call_sid} -> {to}")
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status
        }
    
    def get_call(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get call information"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "from": call.from_,
                "to": call.to,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None
            }
        except TwilioException as e:
            logger.error(f"Failed to get call {call_sid}: {str(e)}")
            return None


