"""
Webdisplay Server
Device Manager Device Class

License: MIT license

Author: C2311231

Notes:
Temporary class to hold information about devices that are awaiting registration. 
Will be replaced by a proper database implementation in the future.
"""

import time

STATUS_OPTIONS = ["pending", "awaiting_verification", "online", "offline", "error"]

class Device:
    def __init__(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]) -> None:
        self.device_id: str = device_id
        self.encrypted_data = encrypted_data
        self.platform: str = platform
        self.capabilities: list[str] = capabilities
        self.last_seen: float = time.time()
        self.encryption_key: None | bytes = None
        self.status: str = "pending"
        self.pairing_code: str = ""
        self.account_id: str | None = None
        self.current_message_id = 0

    def update_timestamp(self) -> None:
        self.last_seen: float = time.time()

    def set_status(self, status: str) -> None:
        if status not in STATUS_OPTIONS:
            raise ValueError(f"Invalid status: {status}. Must be one of {STATUS_OPTIONS}")
        self.status: str = status

    def __str__(self) -> str:
        return f"Device(device_id={self.device_id}, platform={self.platform}, capabilities={self.capabilities}, last_seen={self.last_seen}, status={self.status})"
