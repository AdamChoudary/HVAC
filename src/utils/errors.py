from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class GHLAPIError(APIError):
    """GoHighLevel API error"""
    pass


class VapiAPIError(APIError):
    """Vapi API error"""
    pass


class TwilioAPIError(APIError):
    """Twilio API error"""
    pass


def handle_api_error(error: Exception) -> HTTPException:
    """Convert API errors to HTTP exceptions"""
    if isinstance(error, APIError):
        logger.error(f"API Error: {error.message}", extra=error.details)
        return HTTPException(
            status_code=error.status_code,
            detail={
                "error": error.message,
                "details": error.details
            }
        )
    
    logger.exception("Unexpected error occurred")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "Internal server error",
            "message": str(error)
        }
    )

