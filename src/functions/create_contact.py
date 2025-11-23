from src.models import CreateContactRequest, CreateContactResponse
from src.integrations.ghl import GHLClient
from src.utils.validation import validate_phone_number, validate_email, validate_zip_code
from src.utils.ghl_fields import build_custom_fields_array, normalize_ghl_field_key
from src.utils.logging import logger


async def create_contact(request: CreateContactRequest) -> CreateContactResponse:
    """
    Create or update contact in GHL.
    Checks if contact exists first (by phone/email).
    """
    ghl = GHLClient()
    
    # Validate inputs
    phone = validate_phone_number(request.phone)
    email = validate_email(request.email) if request.email else None
    zip_code = validate_zip_code(request.zip_code) if request.zip_code else None
    
    # Check if contact exists (search by phone first, then email)
    existing_contact = None
    if phone:
        existing_contact = await ghl.get_contact(phone=phone)
    if not existing_contact and email:
        existing_contact = await ghl.get_contact(email=email)
    
    # Prepare contact data
    name_parts = request.name.split(maxsplit=1)
    
    # Build custom fields array (GHL API format)
    # GHL uses "contact.{key}" format for field keys
    custom_fields_dict = {}
    if request.custom_fields:
        custom_fields_dict.update(request.custom_fields)
    
    # Add SMS consent to custom fields
    if request.sms_consent:
        custom_fields_dict["sms_consent"] = "true"
    
    custom_fields_array = build_custom_fields_array(custom_fields_dict)
    
    # Build contact data - only include email if it's valid
    contact_data = {
        "firstName": name_parts[0] if name_parts else "",
        "lastName": name_parts[1] if len(name_parts) > 1 else "",
        "phone": phone,
        "address1": request.address or "",
        "postalCode": zip_code or "",
        "customFields": custom_fields_array if custom_fields_array else []
    }
    
    # Only include email if it's valid (GHL requires valid email format or omit the field)
    if email:
        contact_data["email"] = email
    
    if existing_contact:
        # Update existing contact
        contact_id = existing_contact.get("id")
        logger.info(f"Updating existing contact: {contact_id}")
        await ghl.update_contact(contact_id, contact_data)
        is_new = False
    else:
        # Create new contact
        logger.info(f"Creating new contact: {phone}")
        try:
            result = await ghl.create_contact(contact_data)
            # GHL returns contact in different formats - extract ID
            if isinstance(result, dict):
                contact_id = result.get("id") or result.get("contact", {}).get("id", "")
            else:
                contact_id = ""
            if not contact_id:
                logger.error(f"Failed to extract contact ID from response: {result}")
            is_new = True
        except Exception as e:
            # Handle duplicate contact error - GHL returns contact ID in error
            from src.utils.errors import GHLAPIError
            import re
            import json
            
            error_str = str(e)
            error_message = error_str.lower()
            
            # Get the actual GHL error response text for duplicate detection
            ghl_error_text = ""
            if isinstance(e, GHLAPIError) and e.details:
                ghl_error_text = e.details.get("response", "")
            
            # Combine error string and GHL response for duplicate detection
            full_error_text = (error_str + " " + ghl_error_text).lower()
            
            # Check for duplicate indicators in error message
            is_duplicate = (
                "duplicated contacts" in full_error_text or 
                "duplicate" in full_error_text or
                "does not allow duplicated" in full_error_text or
                "duplicate contact" in full_error_text
            )
            
            # Also check status code for 400 (Bad Request) which often indicates duplicates
            is_400_error = False
            if isinstance(e, GHLAPIError):
                is_400_error = e.status_code == 400
            
            if is_duplicate or (is_400_error and ("contact" in full_error_text or "duplicate" in full_error_text)):
                logger.warning(f"⚠️ Duplicate contact detected (status: {is_400_error}, message: {is_duplicate}), extracting contact ID...")
                contact_id = None
                
                # Try to extract from GHLAPIError details (response text contains JSON)
                if isinstance(e, GHLAPIError) and e.details:
                    response_text = e.details.get("response", "")
                    logger.info(f"📋 Error response text: {response_text}")
                    try:
                        # Parse the JSON response from GHL
                        error_data = json.loads(response_text)
                        logger.info(f"📦 Parsed error data: {error_data}")
                        if isinstance(error_data, dict):
                            # Try meta.contactId first (most common format)
                            if "meta" in error_data and isinstance(error_data["meta"], dict):
                                contact_id = error_data["meta"].get("contactId")
                                if contact_id:
                                    logger.info(f"✅ Extracted contact ID from error meta: {contact_id}")
                            # Also try direct access
                            if not contact_id and "contactId" in error_data:
                                contact_id = error_data.get("contactId")
                                if contact_id:
                                    logger.info(f"✅ Extracted contact ID directly: {contact_id}")
                    except json.JSONDecodeError as je:
                        logger.warning(f"⚠️ Failed to parse error JSON: {je}, response: {response_text}")
                    except Exception as parse_err:
                        logger.warning(f"⚠️ Error extracting contact ID: {parse_err}")
                
                # Try regex extraction from error string as fallback
                if not contact_id:
                    # Try multiple regex patterns
                    patterns = [
                        r'"contactId"\s*:\s*"([^"]+)"',
                        r'contactId["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
                        r'contactId["\']?\s*:\s*["\']?([a-zA-Z0-9]+)'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, error_str)
                        if match:
                            contact_id = match.group(1)
                            logger.info(f"✅ Extracted contact ID via regex ({pattern}): {contact_id}")
                            break
                
                if contact_id:
                    logger.info(f"🔄 Updating existing duplicate contact: {contact_id}")
                    try:
                        await ghl.update_contact(contact_id, contact_data)
                        logger.info(f"✅ Successfully updated duplicate contact: {contact_id}")
                        is_new = False
                    except Exception as update_err:
                        logger.error(f"❌ Failed to update duplicate contact {contact_id}: {update_err}")
                        raise e  # Re-raise original error if update fails
                else:
                    logger.error(f"❌ Could not extract contact ID from duplicate error")
                    logger.error(f"   Error string: {error_str[:200]}")
                    logger.error(f"   Error details: {e.details if isinstance(e, GHLAPIError) else 'N/A'}")
                    # Re-raise original error
                    raise e
            else:
                # Re-raise other errors
                logger.error(f"❌ Non-duplicate error: {error_str}")
                raise
    
    return CreateContactResponse(
        contact_id=contact_id,
        success=True,
        is_new=is_new
    )


