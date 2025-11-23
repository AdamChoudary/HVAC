"""
Webhook signature verification utilities for GHL webhooks.
GHL uses HMAC SHA256 for webhook signature verification.
"""
import hmac
import hashlib
from typing import Optional
from src.utils.logging import logger
from src.config import settings


def verify_ghl_webhook_signature(
    payload: bytes,
    signature: Optional[str],
    secret: Optional[str] = None
) -> bool:
    """
    Verify GHL webhook signature using HMAC SHA256.
    
    Args:
        payload: Raw request body as bytes
        signature: X-GHL-Signature header value
        secret: Webhook secret (from settings if not provided)
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        logger.warning("No webhook signature provided")
        return False
    
    secret = secret or settings.webhook_secret
    if not secret:
        logger.warning("Webhook secret not configured - skipping signature verification")
        return False
    
    try:
        # GHL typically sends signature as: sha256=<hash>
        # Extract the hash if it's in that format
        if "sha256=" in signature:
            received_hash = signature.split("sha256=")[1]
        else:
            received_hash = signature
        
        # Compute expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, received_hash)
        
        if not is_valid:
            logger.warning(f"Webhook signature verification failed. Expected: {expected_signature[:16]}..., Received: {received_hash[:16]}...")
        
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

