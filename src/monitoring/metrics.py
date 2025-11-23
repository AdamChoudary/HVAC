"""
Advanced monitoring and metrics endpoints for tracking system performance.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.integrations.ghl import GHLClient
from src.integrations.vapi import VapiClient
from src.utils.logging import logger
from src.config import settings

router = APIRouter()


@router.get("/metrics/overview")
async def get_metrics_overview(
    days: int = 7
) -> Dict[str, Any]:
    """
    Get overview metrics for the last N days.
    
    Returns:
        - Total calls (inbound + outbound)
        - Booking conversion rate
        - Average call duration
        - Warm transfer success rate
        - Lead contact speed (outbound)
        - API error rates
    """
    try:
        ghl = GHLClient()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get contacts created in date range
        # Note: GHL API doesn't have direct date filtering, so we'll use a workaround
        # This is a simplified version - in production, you'd want to cache this data
        
        metrics = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "calls": {
                "total": 0,  # Would need to track this separately
                "inbound": 0,
                "outbound": 0,
                "successful": 0,
                "failed": 0
            },
            "bookings": {
                "total": 0,
                "conversion_rate": 0.0
            },
            "transfers": {
                "total": 0,
                "successful": 0,
                "success_rate": 0.0
            },
            "leads": {
                "total": 0,
                "contacted": 0,
                "contact_speed_minutes": 0.0,
                "average_quality_score": 0.0
            },
            "api_health": {
                "ghl_status": "unknown",
                "vapi_status": "unknown",
                "error_rate": 0.0
            }
        }
        
        # Check API health
        try:
            await ghl.get_calendars()
            metrics["api_health"]["ghl_status"] = "healthy"
        except Exception as e:
            metrics["api_health"]["ghl_status"] = "unhealthy"
            logger.error(f"GHL API health check failed: {e}")
        
        try:
            vapi = VapiClient()
            await vapi._request("GET", "assistant")
            metrics["api_health"]["vapi_status"] = "healthy"
        except Exception as e:
            metrics["api_health"]["vapi_status"] = "unhealthy"
            logger.error(f"Vapi API health check failed: {e}")
        
        return metrics
    except Exception as e:
        logger.exception(f"Error getting metrics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/calls")
async def get_call_metrics(
    days: int = 7
) -> Dict[str, Any]:
    """
    Get detailed call metrics.
    """
    # In production, this would query a database or analytics service
    # For now, return structure
    return {
        "period_days": days,
        "total_calls": 0,
        "by_type": {
            "inbound": 0,
            "outbound": 0
        },
        "by_outcome": {
            "booked": 0,
            "transferred": 0,
            "no_answer": 0,
            "declined": 0
        },
        "average_duration_seconds": 0,
        "success_rate": 0.0
    }


@router.get("/metrics/bookings")
async def get_booking_metrics(
    days: int = 7
) -> Dict[str, Any]:
    """
    Get booking conversion metrics.
    """
    return {
        "period_days": days,
        "total_bookings": 0,
        "by_service_type": {
            "repair": 0,
            "installation": 0,
            "maintenance": 0,
            "estimate": 0
        },
        "conversion_rate": 0.0,
        "average_time_to_booking_minutes": 0
    }


@router.get("/metrics/leads")
async def get_lead_metrics(
    days: int = 7
) -> Dict[str, Any]:
    """
    Get lead engagement metrics.
    """
    try:
        ghl = GHLClient()
        
        # This would need to query contacts and analyze custom fields
        # Simplified version for now
        return {
            "period_days": days,
            "total_leads": 0,
            "contacted": 0,
            "contact_rate": 0.0,
            "average_contact_speed_minutes": 0.0,
            "average_quality_score": 0.0,
            "by_source": {
                "form": 0,
                "webchat": 0,
                "google_ads": 0,
                "meta_ads": 0,
                "other": 0
            }
        }
    except Exception as e:
        logger.exception(f"Error getting lead metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for all integrations.
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check GHL
    try:
        ghl = GHLClient()
        await ghl.get_calendars()
        health["services"]["ghl"] = {"status": "healthy", "response_time_ms": 0}
    except Exception as e:
        health["services"]["ghl"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"
    
    # Check Vapi
    try:
        vapi = VapiClient()
        await vapi._request("GET", "assistant")
        health["services"]["vapi"] = {"status": "healthy", "response_time_ms": 0}
    except Exception as e:
        health["services"]["vapi"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"
    
    # Check Twilio (basic check)
    if settings.twilio_account_sid and settings.twilio_auth_token:
        health["services"]["twilio"] = {"status": "configured"}
    else:
        health["services"]["twilio"] = {"status": "not_configured"}
    
    return health

