"""
Webdisplay Server
Device Manager

License: MIT license

Author: C2311231

Notes:
"""
from src.models.player import PlayerDevice
from src.models.player_config import PlayerConfig
import time
import uuid

# TODO Add a method to remove devices that have not been seen for a certain amount of time.
# TODO Add ability to associate devices with a certian user or account.
# TODO Workout encryption method and key managment.


class AwaitingDevice:
    def __init__(self, device_id: str, platform: str, capabilities: list[str]):
        self.device_id = device_id
        self.platform = platform
        self.capabilities = capabilities
        self.timestamp = time.time()

    def update_timestamp(self):
        self.timestamp = time.time()


class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.awaiting_registration = {}
        self.approved_devices = []

    def register_device(self, device_id: str, platform: str, capabilities: list[str], encryption_key: str):
        config_id = str(uuid.uuid4())
        config = PlayerConfig(config_id, f"Player {device_id}", "default")

        if device_id in self.devices:
            self.devices[device_id].update_timestamp()
            print(f"Device {device_id} is already registered.")
            return

        device = PlayerDevice(device_id, config_id,
                              platform, capabilities, encryption_key)
        self.devices[device_id] = device
        print(
            f"Registered device: {device_id}, {config_id}, {platform}, {capabilities}, {encryption_key}")

    def get_device(self, device_id: str):
        return self.devices.get(device_id, None)

    def list_devices(self):
        return self.devices

    def add_awaiting_device(self, device_id: str, platform: str, capabilities: list[str]):
        if device_id in self.awaiting_registration:
            print(f"Device {device_id} is already awaiting registration.")
            return

        awaiting_device = AwaitingDevice(device_id, platform, capabilities)
        self.awaiting_registration[device_id] = awaiting_device
        print(
            f"Added awaiting device: {device_id}, {platform}, {capabilities}")

    def register_awaiting_device(self, pairing_code: str):
        self.approved_devices.append({pairing_code, time.time()})

    def get_awaiting_devices(self):
        return self.awaiting_registration

    def get_approved_devices(self):
        return self.approved_devices

    def register_approved_device(self, device_id: str, pairing_code: str):
        if any(pairing_code in device for device in self.approved_devices) and device_id in self.awaiting_registration:

            self.approved_devices = [
                device for device in self.approved_devices if pairing_code not in device]
            awaiting_device = self.awaiting_registration.pop(device_id)

            self.register_device(device_id, awaiting_device.platform,
                                 awaiting_device.capabilities, "dummy_encryption_key")

            print(
                f"Device {device_id} registered with pairing code {pairing_code}.")
        else:
            print(
                f"Device {device_id} cannot be registered. Either the pairing code is invalid or the device is not awaiting registration.")
