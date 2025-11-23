import pytest
from src.functions.classify_call_type import classify_call_type
from src.functions.create_contact import create_contact
from src.models import (
    ClassifyCallTypeRequest,
    CreateContactRequest,
    CallType
)


@pytest.mark.asyncio
async def test_classify_call_type_service_repair():
    """Test call type classification for service/repair"""
    request = ClassifyCallTypeRequest(
        transcript="My AC is broken and not working. I need someone to fix it urgently."
    )
    response = await classify_call_type(request)
    assert response.call_type == CallType.SERVICE_REPAIR
    assert response.confidence > 0.5


@pytest.mark.asyncio
async def test_classify_call_type_install():
    """Test call type classification for installation"""
    request = ClassifyCallTypeRequest(
        transcript="I need a quote for a new HVAC system installation"
    )
    response = await classify_call_type(request)
    assert response.call_type == CallType.INSTALL_ESTIMATE
    assert response.confidence > 0.5


@pytest.mark.asyncio
async def test_classify_call_type_maintenance():
    """Test call type classification for maintenance"""
    request = ClassifyCallTypeRequest(
        transcript="I'd like to schedule a maintenance tune-up for my system"
    )
    response = await classify_call_type(request)
    assert response.call_type == CallType.MAINTENANCE
    assert response.confidence > 0.5

