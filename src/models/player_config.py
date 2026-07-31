"""
Webdisplay Server
Player Configuration Model

License: MIT license

Author: C2311231

Notes:
"""
import json

class PlayerConfig:
    def __init__(self, config_id: str, player_name: str, player_type: str):
        self.config_id = config_id
        self.player_name = player_name
        self.player_type = player_type

    def to_dict(self):
        return {
            "config_id": self.config_id,
            "player_name": self.player_name,
            "player_type": self.player_type,
        }
        
    def to_json(self):
        return json.dumps(self.to_dict())