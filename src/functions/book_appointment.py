from src.models import BookAppointmentRequest, BookAppointmentResponse
from src.integrations.ghl import GHLClient


async def book_appointment(request: BookAppointmentRequest) -> BookAppointmentResponse:
    """
    Book appointment in GHL calendar.
    
    Note: GHL API doesn't have a direct appointments endpoint.
    This function attempts to create the appointment, and if it fails,
    returns a response indicating manual creation is needed.
    """
    ghl = GHLClient()
    
    try:
        result = await ghl.book_appointment(
            calendar_id=request.calendar_id,
            contact_id=request.contact_id,
            start_time=request.start_time,
            end_time=request.end_time,
            title=request.title,
            notes=request.notes
        )
        
        appointment_id = result.get("id", "")
        status = result.get("status", "")
        
        # Check if this is a manual creation response
        if status == "pending_manual_creation" or appointment_id.startswith("manual-"):
            return BookAppointmentResponse(
                appointment_id=appointment_id,
                success=False,
                message=(
                    f"Appointment scheduling initiated. "
                    f"Note: GHL API doesn't support direct appointment creation. "
                    f"Please create the appointment manually in GHL dashboard: "
                    f"Contact ID: {request.contact_id}, "
                    f"Calendar ID: {request.calendar_id}, "
                    f"Time: {request.start_time}"
                )
            )
        
        return BookAppointmentResponse(
            appointment_id=appointment_id,
            success=True,
            message=f"Appointment booked successfully for {request.start_time}"
        )
    except Exception as e:
        # If booking fails, provide helpful error message
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            return BookAppointmentResponse(
                appointment_id="",
                success=False,
                message=(
                    f"GHL API doesn't support direct appointment creation via REST API. "
                    f"Please create appointment manually in GHL dashboard. "
                    f"Details: Contact {request.contact_id}, Calendar {request.calendar_id}, "
                    f"Time {request.start_time}. Error: {error_msg}"
                )
            )
        return BookAppointmentResponse(
            appointment_id="",
            success=False,
            message=f"Failed to book appointment: {error_msg}"
        )


