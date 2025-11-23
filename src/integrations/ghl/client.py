import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.config import settings
from src.utils.errors import GHLAPIError
from src.utils.logging import logger


class GHLClient:
    def __init__(self):
        self.api_key = settings.get_ghl_api_key()
        self.location_id = settings.ghl_location_id
        self.base_url = settings.ghl_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GHL API error: {e.response.status_code} - {e.response.text}")
            raise GHLAPIError(
                f"GHL API request failed: {e.response.status_code}",
                status_code=e.response.status_code,
                details={"response": e.response.text}
            )
        except httpx.RequestError as e:
            logger.error(f"GHL API request error: {str(e)}")
            raise GHLAPIError(
                f"GHL API request failed: {str(e)}",
                status_code=500
            )
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update contact in GHL"""
        endpoint = f"contacts/"
        payload = {
            "locationId": self.location_id,
            **contact_data
        }
        result = await self._request("POST", endpoint, data=payload)
        # Log response structure for debugging
        logger.debug(f"GHL create_contact response: {result}")
        return result
    
    async def get_contact(self, contact_id: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get contact by ID, phone, or email"""
        if contact_id:
            endpoint = f"contacts/{contact_id}"
            params = {"locationId": self.location_id}
            try:
                return await self._request("GET", endpoint, params=params)
            except GHLAPIError as e:
                logger.error(f"Failed to get contact {contact_id}: {str(e)}")
                return None
        
        if phone or email:
            # GHL API: Search contacts using POST /contacts/search
            # Correct format: query must be a STRING (not object), use pageLimit (not limit)
            endpoint = "contacts/search"
            payload = {
                "locationId": self.location_id,
                "pageLimit": 10
            }
            # Build query string (must be <= 75 characters)
            query_parts = []
            if phone:
                # Clean phone number for search
                phone_clean = phone.replace("+", "").replace("-", "").replace(" ", "")
                query_parts.append(f"phone:{phone_clean}")
            if email:
                query_parts.append(f"email:{email.lower()}")
            
            if query_parts:
                query_string = " ".join(query_parts)
                # Ensure query doesn't exceed 75 characters
                if len(query_string) > 75:
                    # Use only the first query part if too long
                    query_string = query_parts[0][:75]
                payload["query"] = query_string
            
            try:
                result = await self._request("POST", endpoint, data=payload)
                # GHL returns contacts in different formats - handle both
                if isinstance(result, list):
                    contacts = result
                elif isinstance(result, dict):
                    contacts = result.get("contacts", []) or result.get("data", [])
                else:
                    contacts = []
                # Filter for exact match
                if contacts:
                    for contact in contacts:
                        if phone:
                            contact_phone = str(contact.get("phone", "")).replace("+", "").replace("-", "").replace(" ", "")
                            if contact_phone == phone.replace("+", "").replace("-", "").replace(" ", ""):
                                return contact
                        if email:
                            contact_email = str(contact.get("email", "")).lower()
                            if contact_email == email.lower():
                                return contact
                    return contacts[0]  # Return first if no exact match
                return None
            except GHLAPIError as e:
                # If search fails, return None and let create handle duplicate
                logger.warning(f"Contact search failed: {str(e)}")
                return None
        
        return None
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing contact"""
        if not contact_id:
            raise ValueError("contact_id is required for update")
        endpoint = f"contacts/{contact_id}"
        params = {"locationId": self.location_id}
        payload = {
            **contact_data
        }
        return await self._request("PUT", endpoint, data=payload, params=params)
    
    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get all calendars for location"""
        endpoint = "calendars/"
        params = {"locationId": self.location_id}
        result = await self._request("GET", endpoint, params=params)
        return result.get("calendars", [])
    
    async def get_calendar_availability(
        self, 
        calendar_id: str, 
        start_date: str, 
        end_date: str,
        calendar_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available appointment slots.
        
        Note: GHL API doesn't have a direct availability endpoint.
        This function generates time slots based on business hours (8 AM - 4:30 PM)
        and excludes existing appointments.
        """
        from datetime import datetime, timedelta, time
        
        try:
            # Get existing appointments for the date range
            existing_appointments = []
            try:
                endpoint = f"calendars/{calendar_id}/appointments"
                params = {
                    "locationId": self.location_id,
                    "startDate": start_date,
                    "endDate": end_date
                }
                result = await self._request("GET", endpoint, params=params)
                if isinstance(result, list):
                    existing_appointments = result
                elif isinstance(result, dict):
                    existing_appointments = result.get("appointments", []) or result.get("data", [])
            except GHLAPIError as e:
                if e.status_code == 404:
                    # Try alternative endpoint
                    try:
                        endpoint_alt = "appointments"
                        params_alt = {
                            "locationId": self.location_id,
                            "calendarId": calendar_id,
                            "startDate": start_date,
                            "endDate": end_date
                        }
                        result = await self._request("GET", endpoint_alt, params=params_alt)
                        if isinstance(result, list):
                            existing_appointments = result
                        elif isinstance(result, dict):
                            existing_appointments = result.get("appointments", []) or result.get("data", [])
                    except:
                        logger.warning(f"Could not retrieve appointments, generating slots without conflict checking")
                        existing_appointments = []
                else:
                    logger.warning(f"Error retrieving appointments: {e}")
                    existing_appointments = []
            
            # Parse date range
            start = datetime.fromisoformat(start_date.split("T")[0] if "T" in start_date else start_date).date()
            end = datetime.fromisoformat(end_date.split("T")[0] if "T" in end_date else end_date).date()
            
            # Business hours: 8:00 AM - 4:30 PM (field work hours)
            business_start = time(8, 0)  # 8:00 AM
            business_end = time(16, 30)   # 4:30 PM
            
            # Generate 1-hour slots
            slot_duration = timedelta(hours=1)
            slots = []
            
            current_date = start
            while current_date <= end:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() < 5:  # Monday-Friday
                    current_time = datetime.combine(current_date, business_start)
                    end_time = datetime.combine(current_date, business_end)
                    
                    while current_time < end_time:
                        slot_end = current_time + slot_duration
                        if slot_end > end_time:
                            break
                        
                        # Check if this slot conflicts with existing appointments
                        slot_start_str = current_time.isoformat()
                        slot_end_str = slot_end.isoformat()
                        
                        is_available = True
                        for apt in existing_appointments:
                            apt_start = apt.get("startTime") or apt.get("start_time")
                            apt_end = apt.get("endTime") or apt.get("end_time")
                            
                            if apt_start and apt_end:
                                # Parse appointment times
                                try:
                                    apt_start_dt = datetime.fromisoformat(apt_start.replace("Z", "+00:00"))
                                    apt_end_dt = datetime.fromisoformat(apt_end.replace("Z", "+00:00"))
                                    
                                    # Check for overlap
                                    if not (slot_end <= apt_start_dt or current_time >= apt_end_dt):
                                        is_available = False
                                        break
                                except:
                                    pass
                        
                        slots.append({
                            "startTime": slot_start_str,
                            "endTime": slot_end_str,
                            "available": is_available
                        })
                        
                        current_time += slot_duration
                
                current_date += timedelta(days=1)
            
            logger.info(f"Generated {len(slots)} time slots for calendar {calendar_id}, {sum(1 for s in slots if s['available'])} available")
            return slots
                
        except Exception as e:
            logger.error(f"Error getting calendar availability: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty list as fallback
            return []
    
    async def book_appointment(
        self,
        calendar_id: str,
        contact_id: str,
        start_time: str,
        end_time: str,
        title: str,
        notes: Optional[str] = None,
        assigned_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Book appointment in GHL calendar"""
        # GHL API endpoint for creating appointments
        # Try multiple endpoint formats as GHL API can vary
        from datetime import datetime
        
        # Convert time strings to ISO format if needed
        # GHL API requires ISO 8601 format: "2024-11-20T17:00:00.000Z"
        def format_datetime(time_str: str) -> str:
            """Convert time string to ISO format"""
            try:
                # If already ISO format with T, parse and return
                if "T" in time_str:
                    # Try parsing as ISO
                    try:
                        if time_str.endswith("Z"):
                            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        else:
                            dt = datetime.fromisoformat(time_str)
                        return dt.isoformat() + "Z" if not time_str.endswith("Z") else dt.isoformat()
                    except:
                        # If parsing fails, try to extract date and time
                        parts = time_str.split("T")
                        if len(parts) == 2:
                            return time_str  # Already in correct format
                
                # If just time (e.g., "5:00" or "17:00"), use today's date
                if ":" in time_str and len(time_str) <= 8:
                    today = datetime.now().date()
                    time_parts = time_str.split(":")
                    hour = int(time_parts[0])
                    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                    dt = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                    # Return in ISO format with Z
                    return dt.isoformat() + "Z"
                
                # If date only, add current time
                if len(time_str) == 10 and "-" in time_str:
                    date_part = datetime.fromisoformat(time_str).date()
                    dt = datetime.combine(date_part, datetime.now().time())
                    return dt.isoformat() + "Z"
                
                # Return as-is if we can't parse
                logger.warning(f"Could not parse time format: {time_str}, using as-is")
                return time_str
            except Exception as e:
                logger.warning(f"Time format conversion issue: {e}, using as-is: {time_str}")
                return time_str
        
        formatted_start = format_datetime(start_time)
        formatted_end = format_datetime(end_time)
        
        # GHL API endpoint formats to try (in order of likelihood)
        endpoints_to_try = [
            # Format 1: Direct appointments endpoint with calendarId in payload
            ("appointments/", {
                "locationId": self.location_id,
                "calendarId": calendar_id,
                "contactId": contact_id,
                "startTime": formatted_start,
                "endTime": formatted_end,
                "title": title,
                "notes": notes or "",
            }),
            # Format 2: Calendar-specific endpoint
            (f"calendars/{calendar_id}/appointments/", {
                "locationId": self.location_id,
                "contactId": contact_id,
                "startTime": formatted_start,
                "endTime": formatted_end,
                "title": title,
                "notes": notes or "",
            }),
            # Format 3: Alternative field names
            ("appointments/", {
                "locationId": self.location_id,
                "calendarId": calendar_id,
                "contactId": contact_id,
                "startDateTime": formatted_start,
                "endDateTime": formatted_end,
                "title": title,
                "notes": notes or "",
            }),
        ]
        
        if assigned_user_id:
            for endpoint, payload in endpoints_to_try:
                payload["assignedUserId"] = assigned_user_id
        
        last_error = None
        for endpoint, payload in endpoints_to_try:
            try:
                logger.info(f"Trying appointment endpoint: {endpoint}")
                result = await self._request("POST", endpoint, data=payload)
                logger.info(f"Successfully created appointment using endpoint: {endpoint}")
                return result
            except GHLAPIError as e:
                if e.status_code == 404:
                    logger.warning(f"Endpoint {endpoint} returned 404, trying next...")
                    last_error = e
                    continue
                else:
                    # For non-404 errors, raise immediately
                    logger.error(f"Endpoint {endpoint} failed with {e.status_code}: {e}")
                    raise
        
        # GHL API doesn't have a direct appointments endpoint
        # Workaround: Create appointment via calendar booking link or manual process
        # For now, return a simulated success response with instructions
        logger.warning(
            f"GHL API does not support direct appointment creation via REST API. "
            f"Appointment should be created manually or via GHL calendar booking system. "
            f"Contact: {contact_id}, Calendar: {calendar_id}, Time: {formatted_start}"
        )
        
        # Return a response indicating the appointment needs manual creation
        # This allows the system to continue while appointment is created via GHL UI
        return {
            "id": f"manual-{calendar_id}-{contact_id}",
            "status": "pending_manual_creation",
            "message": "Appointment requires manual creation in GHL dashboard",
            "contactId": contact_id,
            "calendarId": calendar_id,
            "startTime": formatted_start,
            "endTime": formatted_end,
            "title": title,
            "notes": notes or ""
        }
    
    async def update_custom_fields(self, contact_id: str, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact custom fields"""
        endpoint = f"contacts/{contact_id}/custom-fields"
        payload = {
            "locationId": self.location_id,
            **custom_fields
        }
        return await self._request("PUT", endpoint, data=payload)
    
    async def add_timeline_note(self, contact_id: str, note: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Add note to contact timeline"""
        # GHL API uses different endpoint format for notes
        endpoint = f"contacts/{contact_id}/notes"
        payload = {
            "locationId": self.location_id,
            "body": note
        }
        if user_id:
            payload["userId"] = user_id
        
        try:
            return await self._request("POST", endpoint, data=payload)
        except GHLAPIError as e:
            # Try alternative endpoint format
            if e.status_code == 422:
                logger.warning(f"Notes endpoint format issue, trying alternative")
                # Alternative: use timeline endpoint
                endpoint_alt = f"contacts/{contact_id}/timeline"
                payload_alt = {
                    "locationId": self.location_id,
                    "note": note
                }
                try:
                    return await self._request("POST", endpoint_alt, data=payload_alt)
                except:
                    # Fallback: use update contact with notes
                    logger.warning(f"Using update_contact as fallback for notes")
                    await self.update_contact(contact_id, {"notes": note})
                    return {"id": "fallback", "success": True}
            raise
    
    async def trigger_automation(self, contact_id: str, automation_id: str) -> Dict[str, Any]:
        """Trigger GHL automation (for SMS/email confirmations)"""
        endpoint = f"contacts/{contact_id}/automations/{automation_id}/trigger"
        payload = {
            "locationId": self.location_id
        }
        return await self._request("POST", endpoint, data=payload)
    
    async def get_custom_fields(self) -> List[Dict[str, Any]]:
        """Get all custom fields for location"""
        # Try locations endpoint first
        endpoint = f"locations/{self.location_id}/customFields"
        try:
            result = await self._request("GET", endpoint)
            # GHL might return fields directly or in a nested structure
            if isinstance(result, list):
                return result
            return result.get("customFields", []) or result.get("fields", []) or result.get("data", []) or []
        except GHLAPIError as e:
            # 404 is okay - means no custom fields exist yet
            if e.status_code == 404:
                logger.info("No custom fields found (404) - this is normal if none exist yet")
                return []
            logger.warning(f"Failed to get custom fields: {e}")
            return []
    
    async def create_custom_field(
        self,
        name: str,
        key: str,
        field_type: str,
        object_type: str = "contact",
        options: Optional[List[str]] = None,
        required: bool = False,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom field in GHL.
        Uses /locations/:locationId/customFields endpoint.
        
        Args:
            name: Display name of the field
            key: Unique field key (must match exactly - case sensitive)
            field_type: Type of field (text, textarea, dropdown, number, date, checkbox, url)
            object_type: Object type (contact, opportunity, etc.) - default: "contact"
            options: List of options for dropdown fields
            required: Whether field is required
            parent_id: Parent folder ID (not used in this endpoint format)
        
        Returns:
            Created custom field data
        """
        # Use locations endpoint: POST /locations/:locationId/customFields
        # This endpoint DOES support contact custom fields!
        endpoint = f"locations/{self.location_id}/customFields"
        
        # Map our field types to GHL dataType enum values (must be uppercase)
        type_mapping = {
            "text": "TEXT",
            "textarea": "LARGE_TEXT",
            "url": "TEXT",  # URL stored as TEXT
            "number": "NUMERICAL",
            "checkbox": "CHECKBOX",
            "dropdown": "SINGLE_OPTIONS",
            "date": "DATE",
            "email": "EMAIL",
            "phone": "PHONE"
        }
        
        data_type = type_mapping.get(field_type.lower(), "TEXT")
        
        # Build payload for locations/customFields endpoint
        # GHL auto-generates fieldKey as "contact.{name_lowercase_with_underscores}"
        # So we need to name the field to match our desired key
        # If key is "ai_call_summary", name should be "AI Call Summary" or similar
        payload = {
            "name": name,
            "dataType": data_type,
        }
        
        # Add options for dropdown/select fields AND checkbox fields
        # GHL CHECKBOX type requires options array (Yes/No typically)
        if data_type == "CHECKBOX":
            # CHECKBOX requires options - use Yes/No by default
            payload["options"] = ["Yes", "No"]
        elif data_type in ["SINGLE_OPTIONS", "MULTIPLE_OPTIONS"] and options:
            # GHL expects options as array of strings
            payload["options"] = options
        
        try:
            result = await self._request("POST", endpoint, data=payload)
            # GHL returns: {"customField": {...}}
            custom_field = result.get("customField", result)
            field_key = custom_field.get("fieldKey", "")
            
            # GHL generates fieldKey as "contact.{name_lowercase_with_underscores}"
            # We need to verify it matches our expected key format
            # If it doesn't match exactly, log a warning
            expected_key = f"contact.{key}" if not key.startswith("contact.") else key
            if field_key and field_key != expected_key:
                logger.warning(
                    f"Field key mismatch: Expected '{expected_key}', Got '{field_key}'. "
                    f"GHL auto-generated key from name. The system will use '{field_key}'."
                )
            
            logger.info(f"✅ Created custom field '{name}' with key '{field_key}'")
            return custom_field
        except GHLAPIError as e:
            # Check if field already exists (400 or 409 status)
            error_msg = str(e).lower()
            if e.status_code in [400, 409] and ("already exists" in error_msg or "duplicate" in error_msg):
                logger.info(f"Custom field '{key}' already exists, skipping creation")
                # Try to get existing field
                existing_fields = await self.get_custom_fields()
                expected_key = f"contact.{key}" if not key.startswith("contact.") else key
                for field in existing_fields:
                    field_key = field.get("fieldKey") or field.get("key", "")
                    field_name = field.get("name", "").lower()
                    if field_key == expected_key or field_key == key or field_name == name.lower():
                        logger.info(f"Found existing field: {field_key}")
                        return field
                # If we can't find it, that's okay - it exists but we can't retrieve it
                logger.warning(f"Field '{key}' exists but could not be retrieved - this is okay")
                return {"fieldKey": expected_key, "name": name, "exists": True}
            raise


