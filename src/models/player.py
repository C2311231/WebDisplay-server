"""
Webdisplay Server
Player Device Model

License: MIT license

Author: C2311231

Notes:
"""
import datetime
import json

class PlayerDevice:
    def __init__(self, device_id: str, config_id: str, platform: str, capabilities: list[str], encryption_key: str):
        self.device_id = device_id
        self.config_id = config_id
        self.platform = platform
        self.capabilities = capabilities
        self.encryption_key = encryption_key

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "config_id": self.config_id,
            "platform": self.platform,
            "capabilities": self.capabilities,
            "encryption_key": self.encryption_key,
        }
        
    def to_json(self):
        return json.dumps(self.to_dict())