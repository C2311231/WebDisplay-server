"""
Webdisplay Server
Onboarding Endpoints
License: MIT license

Author: C2311231

Notes:
"""
from fastapi import APIRouter
from pydantic import BaseModel
import src.controlers.device_manager as device_manager

router = APIRouter(tags=["Onboarding"], prefix="/onboarding")

deviceManager = device_manager.DeviceManager()

class PairingRequest(BaseModel):
    device_id: str
    platform: str
    capabilities: list[str]
    encrypted_data: dict

@router.post("/request_pairing")
async def request_pairing(pairing_request: PairingRequest):
    """
    Endpoint to request pairing with a device.
    """

    deviceManager.add_awaiting_device(pairing_request.device_id, pairing_request.encrypted_data, pairing_request.platform, pairing_request.capabilities)
    return {"message": "Pairing request received."}

@router.get("/check_pairing_status")
async def check_pairing_status(device_id: str):
    """
    Endpoint to check the status of a pairing request.
    """
    status, pairing_code = deviceManager.get_pairing_status(device_id)
    return {"device_id": device_id, "status": status, "pairing_code": pairing_code}