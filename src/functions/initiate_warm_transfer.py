from src.models import InitiateWarmTransferRequest, InitiateWarmTransferResponse
from src.integrations.twilio import TwilioService
from src.config.business_data import STAFF_DIRECTORY
from src.utils.business_hours import check_business_hours
from src.utils.logging import logger


async def initiate_warm_transfer(request: InitiateWarmTransferRequest) -> InitiateWarmTransferResponse:
    """
    Transfer call to human staff member.
    Uses Twilio to perform warm transfer.
    """
    # 1. Check if we are within Office Hours (7am - 8:30pm)
    hours_status = check_business_hours(schedule_type="office")
    if not hours_status["isBusinessHours"]:
        return InitiateWarmTransferResponse(
            success=False,
            message="We are currently closed. Transfers are only available between 7:00 AM and 8:30 PM Pacific Time."
        )

    # 2. Determine target phone number
    target_phone = request.staff_phone
    target_name = "staff member"
    
    # If no specific phone provided, default to Scott (Main)
    if not target_phone:
        staff = STAFF_DIRECTORY.get("scott")
        if staff:
            target_phone = staff["phone"]
            target_name = staff["name"]
    
    # If still no phone, fail
    if not target_phone:
        return InitiateWarmTransferResponse(
            success=False,
            message="No staff phone number available for transfer."
        )

    twilio = TwilioService()
    try:
        result = twilio.initiate_warm_transfer(
            call_sid=request.call_sid,
            to=target_phone
        )
        
        return InitiateWarmTransferResponse(
            success=True,
            transfer_sid=result.get("call_sid"),
            message=f"Transferring call to {target_name}..."
        )
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        return InitiateWarmTransferResponse(
            success=False,
            message="Failed to initiate transfer due to technical error."
        )


