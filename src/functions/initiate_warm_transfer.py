from src.models import InitiateWarmTransferRequest, InitiateWarmTransferResponse
from src.integrations.twilio import TwilioService
from src.utils.logging import logger


async def initiate_warm_transfer(request: InitiateWarmTransferRequest) -> InitiateWarmTransferResponse:
    """
    Transfer call to human staff member.
    Uses Twilio to perform warm transfer.
    """
    twilio = TwilioService()
    result = twilio.initiate_warm_transfer(
        call_sid=request.call_sid,
        to=request.staff_phone
    )
    
    return InitiateWarmTransferResponse(
        success=True,
        transfer_sid=result.get("call_sid"),
        message=f"Transferring call to {request.staff_phone}"
    )


