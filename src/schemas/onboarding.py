"""
Webdisplay Server
Onboarding Schemas
License: MIT license

Author: C2311231

Notes:
"""

from pydantic import BaseModel


class PairingRequest(BaseModel):
    device_id: str
    platform: str
    capabilities: list[str]
    encrypted_data: dict

class RegisterRequest(BaseModel):
    device_id: str
    data: dict