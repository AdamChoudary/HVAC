from src.models import ClassifyCallTypeRequest, ClassifyCallTypeResponse, CallType
import re


async def classify_call_type(request: ClassifyCallTypeRequest) -> ClassifyCallTypeResponse:
    """
    Analyze conversation to determine call type.
    Uses keyword matching and pattern recognition.
    """
    transcript_lower = request.transcript.lower()
    summary_lower = (request.conversation_summary or "").lower()
    combined_text = f"{transcript_lower} {summary_lower}"
    
    # Keywords for each call type
    service_repair_keywords = [
        "broken", "not working", "repair", "fix", "broken down",
        "not cooling", "not heating", "leak", "emergency", "urgent",
        "stopped working", "malfunction", "issue", "problem"
    ]
    
    install_estimate_keywords = [
        "install", "installation", "new system", "replace", "upgrade",
        "estimate", "quote", "pricing", "cost", "price", "how much",
        "new unit", "new equipment"
    ]
    
    maintenance_keywords = [
        "maintenance", "tune-up", "service", "check-up", "inspection",
        "preventive", "annual", "regular service", "maintenance plan"
    ]
    
    appointment_change_keywords = [
        "reschedule", "cancel", "change", "move", "postpone",
        "different time", "different date", "appointment"
    ]
    
    # Score each type
    scores = {
        CallType.SERVICE_REPAIR: sum(1 for kw in service_repair_keywords if kw in combined_text),
        CallType.INSTALL_ESTIMATE: sum(1 for kw in install_estimate_keywords if kw in combined_text),
        CallType.MAINTENANCE: sum(1 for kw in maintenance_keywords if kw in combined_text),
        CallType.APPOINTMENT_CHANGE: sum(1 for kw in appointment_change_keywords if kw in combined_text),
    }
    
    # Determine call type
    max_score = max(scores.values())
    if max_score == 0:
        call_type = CallType.OTHER
        confidence = 0.5
    else:
        call_type = max(scores, key=scores.get)
        confidence = min(0.95, 0.5 + (max_score * 0.1))
    
    reasoning = f"Detected {max_score} matching keywords for {call_type.value}"
    
    return ClassifyCallTypeResponse(
        call_type=call_type,
        confidence=confidence,
        reasoning=reasoning
    )


