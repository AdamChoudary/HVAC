from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from src.integrations.vapi import VapiClient
from src.integrations.twilio import TwilioService
from src.config import settings
from src.utils.logging import logger
from src.utils.validation import validate_phone_number

router = APIRouter()

class DemoCallRequest(BaseModel):
    phone: str
    name: Optional[str] = None
    demo_type: Optional[str] = None # Added for smart routing
    # Allow other fields but ignore them
    class Config:
        extra = "ignore"

@router.post("/demo/handle")
async def handle_demo(request: DemoCallRequest):
    """Smart router: Handles both inbound and outbound based on demo_type"""
    # Log full request for debugging
    logger.info(f"🔀 Smart Router Request: {request.model_dump()}")
    
    # Normalize demo_type
    dtype = (request.demo_type or "").lower().strip()
    
    # Route to Inbound if demo_type contains "inbound", otherwise default to Outbound
    if "inbound" in dtype:
        logger.info(f"👈 Routing to Inbound Logic (Matched: '{dtype}')")
        return await inbound_demo(request)
    else:
        # Default to Outbound
        logger.info(f"👉 Routing to Outbound Logic (Default, received: '{dtype}')")
        return await outbound_demo(request)

@router.post("/demo/outbound")
async def outbound_demo(request: DemoCallRequest):
    """Trigger a simple outbound call for demo purposes"""
    logger.info(f"🚀 Demo Outbound Call requested for {request.phone}")
    
    try:
        phone_clean = validate_phone_number(request.phone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid phone number: {str(e)}")
        
    vapi = VapiClient()
    
    # Use configured outbound assistant or default
    assistant_id = settings.vapi_outbound_assistant_id or "d6c74f74-de2a-420d-ae59-aab8fa7cbabe"
    
    try:
        # Create call
        call_config = {
            "assistantId": assistant_id,
            "customer": {
                "number": phone_clean,
                "name": request.name or "Valued Customer"
            },
            "phoneNumberId": settings.vapi_phone_number_id
        }
        
        # If no phone number ID configured, try to get from assistant
        if not call_config.get("phoneNumberId"):
            try:
                assistant = await vapi.get_assistant(assistant_id)
                default_phone = assistant.get("phoneNumberId") or assistant.get("phoneNumber")
                if default_phone:
                    call_config["phoneNumberId"] = default_phone
                else:
                    logger.warning("No phone number configured for Vapi assistant, call might fail if Vapi doesn't have a default")
            except Exception as e:
                logger.warning(f"Could not fetch assistant details: {e}")
                
        result = await vapi.create_call(call_config)
        logger.info(f"✅ Demo call initiated: {result.get('id')}")
        return {"status": "success", "call_id": result.get("id")}
        
    except Exception as e:
        logger.error(f"❌ Demo call failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/demo/inbound")
async def inbound_demo(request: DemoCallRequest):
    """Trigger an inbound call simulation (AI calls user)"""
    logger.info(f"🚀 Demo Inbound Call requested for {request.phone}")
    
    try:
        phone_clean = validate_phone_number(request.phone)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid phone number: {str(e)}")
        
    vapi = VapiClient()
    
    # Use configured inbound assistant or specific ID provided by user
    assistant_id = settings.vapi_inbound_assistant_id or "d61d0517-4a65-496e-b97f-d3ad220f684e"
    
    try:
        # Create call
        call_config = {
            "assistantId": assistant_id,
            "customer": {
                "number": phone_clean,
                "name": request.name or "Valued Customer"
            },
            "phoneNumberId": settings.vapi_phone_number_id
        }
        
        # If no phone number ID configured, try to get from assistant
        if not call_config.get("phoneNumberId"):
            try:
                assistant = await vapi.get_assistant(assistant_id)
                default_phone = assistant.get("phoneNumberId") or assistant.get("phoneNumber")
                if default_phone:
                    call_config["phoneNumberId"] = default_phone
                else:
                    logger.warning("No phone number configured for Vapi assistant, call might fail if Vapi doesn't have a default")
            except Exception as e:
                logger.warning(f"Could not fetch assistant details: {e}")
                
        result = await vapi.create_call(call_config)
        logger.info(f"✅ Demo inbound call initiated: {result.get('id')}")
        return {"status": "success", "call_id": result.get("id")}
        
    except Exception as e:
        logger.error(f"❌ Demo inbound call failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
