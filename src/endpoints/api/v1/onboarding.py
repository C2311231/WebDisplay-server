"""
Webdisplay Server
Onboarding Endpoints
License: MIT license

Author: C2311231

Notes:
"""
import asyncio

from fastapi import APIRouter
from src.controllers.device_manager import DeviceManager
from src.schemas.onboarding import *

router = APIRouter(tags=["Onboarding"], prefix="/onboarding")

deviceManager = DeviceManager()


@router.post("/pairing")
async def request_pairing(pairing_request: PairingRequest):
    """
    Endpoint to request pairing with a device.
    """
    try:
        deviceManager.add_awaiting_device(
            pairing_request.device_id, pairing_request.encrypted_data, pairing_request.platform, pairing_request.capabilities)
    except ValueError as e:
        return {"error": str(e)}
    return {"message": "Pairing request received."}


@router.get("/pairing")
async def check_pairing_status(device_id: str):
    """
    Endpoint to check the status of a pairing request.
    """
    status = None
    try:
        status = deviceManager.get_pairing_status(device_id)
    except ValueError as e:
        return {"error": str(e)}
    return {"device_id": device_id, "status": status}


@router.post("/register")
async def register_device(register_request: RegisterRequest):
    """
    Endpoint to register a device after successful pairing.
    """
    try:
        deviceManager.register_device_by_id(
            register_request.device_id, register_request.data)
    except ValueError as e:
        return {"error": str(e)}
    return {"message": "Device registered successfully."}


@router.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the device manager and start the pairing code reader.
    """
    # Start the pairing code reader in a separate thread
    asyncio.create_task(deviceManager.read_pairing_codes())
