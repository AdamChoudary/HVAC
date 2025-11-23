"""
Lead quality scoring algorithm for HVAC leads.
Scores leads based on multiple factors to prioritize follow-up.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.logging import logger


def calculate_lead_quality_score(
    contact_data: Dict[str, Any],
    call_data: Optional[Dict[str, Any]] = None
) -> int:
    """
    Calculate lead quality score (0-100) based on multiple factors.
    
    Scoring factors:
    - Contact completeness (name, phone, email, address): 0-20 points
    - Service type urgency (emergency > urgent > standard): 0-25 points
    - Lead source quality (referral > form > ad > chat): 0-20 points
    - Response time (faster = better): 0-15 points
    - Call outcome (booked > interested > no answer): 0-20 points
    
    Args:
        contact_data: Contact information from GHL
        call_data: Optional call metadata (duration, outcome, etc.)
    
    Returns:
        Lead quality score (0-100)
    """
    score = 0
    
    # Factor 1: Contact Completeness (0-20 points)
    completeness_score = 0
    if contact_data.get("firstName") and contact_data.get("lastName"):
        completeness_score += 5
    if contact_data.get("phone"):
        completeness_score += 5
    if contact_data.get("email"):
        completeness_score += 5
    if contact_data.get("address1") or contact_data.get("address"):
        completeness_score += 5
    score += completeness_score
    
    # Factor 2: Service Type Urgency (0-25 points)
    urgency_score = 0
    custom_fields = contact_data.get("customFields", {})
    if isinstance(custom_fields, list):
        custom_fields = {f.get("key"): f.get("value") for f in custom_fields if isinstance(f, dict)}
    
    urgency = custom_fields.get("urgency", "").lower()
    if urgency == "emergency":
        urgency_score = 25
    elif urgency == "urgent":
        urgency_score = 18
    elif urgency == "standard":
        urgency_score = 10
    elif urgency == "low":
        urgency_score = 5
    else:
        # Check appointment notes or call type
        call_type = custom_fields.get("call_type", "").lower()
        if "emergency" in call_type or "urgent" in call_type:
            urgency_score = 20
        elif "maintenance" in call_type:
            urgency_score = 8
        else:
            urgency_score = 12  # Default for unknown
    score += urgency_score
    
    # Factor 3: Lead Source Quality (0-20 points)
    source_score = 0
    lead_source = custom_fields.get("lead_source", "").lower()
    if not lead_source:
        # Try to get from contact tags or source field
        tags = contact_data.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                tag_lower = str(tag).lower()
                if "referral" in tag_lower:
                    lead_source = "referral"
                    break
                elif "form" in tag_lower:
                    lead_source = "form"
                    break
    
    if "referral" in lead_source:
        source_score = 20
    elif "form" in lead_source or "website" in lead_source:
        source_score = 15
    elif "google" in lead_source or "meta" in lead_source or "facebook" in lead_source or "ad" in lead_source:
        source_score = 12
    elif "chat" in lead_source or "webchat" in lead_source:
        source_score = 8
    else:
        source_score = 10  # Default
    score += source_score
    
    # Factor 4: Response Time (0-15 points)
    # Faster response = higher score
    response_score = 0
    if call_data:
        # If call was made quickly after lead creation, higher score
        call_timestamp = call_data.get("call_timestamp")
        lead_timestamp = contact_data.get("dateAdded") or contact_data.get("createdAt")
        
        if call_timestamp and lead_timestamp:
            try:
                # Calculate time difference in minutes
                if isinstance(lead_timestamp, str):
                    lead_dt = datetime.fromisoformat(lead_timestamp.replace('Z', '+00:00'))
                else:
                    lead_dt = lead_timestamp
                
                if isinstance(call_timestamp, str):
                    call_dt = datetime.fromisoformat(call_timestamp.replace('Z', '+00:00'))
                else:
                    call_dt = call_timestamp
                
                minutes_diff = (call_dt - lead_dt).total_seconds() / 60
                
                if minutes_diff < 5:
                    response_score = 15
                elif minutes_diff < 15:
                    response_score = 12
                elif minutes_diff < 60:
                    response_score = 8
                elif minutes_diff < 240:  # 4 hours
                    response_score = 5
                else:
                    response_score = 2
            except Exception as e:
                logger.warning(f"Error calculating response time score: {e}")
                response_score = 5  # Default
    else:
        response_score = 5  # Default if no call data
    score += response_score
    
    # Factor 5: Call Outcome (0-20 points)
    outcome_score = 0
    if call_data:
        outcome = call_data.get("outcome", "").lower()
        if "booked" in outcome or "appointment" in outcome:
            outcome_score = 20
        elif "interested" in outcome or "callback" in outcome:
            outcome_score = 15
        elif "transferred" in outcome:
            outcome_score = 12
        elif "no_answer" in outcome or "voicemail" in outcome:
            outcome_score = 5
        elif "declined" in outcome or "not_interested" in outcome:
            outcome_score = 2
        else:
            outcome_score = 8  # Default
    else:
        # No call yet - check if contact has been called
        # Check both formats: "vapi_called" and "contact.vapi_called"
        vapi_called = (
            custom_fields.get("vapi_called") or 
            custom_fields.get("contact.vapi_called") or 
            "false"
        )
        vapi_called = str(vapi_called).lower() == "true"
        if vapi_called:
            outcome_score = 8  # Called but outcome unknown
        else:
            outcome_score = 5  # Not called yet
    score += outcome_score
    
    # Ensure score is between 0-100
    score = max(0, min(100, score))
    
    logger.info(f"Lead quality score calculated: {score}/100 for contact")
    return score

