"""
Webdisplay Server
Device Manager

License: MIT license

Author: C2311231

Notes:
"""
import json

from src.models.player import PlayerDevice
from src.models.player_config import PlayerConfig
import time
import uuid

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# TODO Add a method to remove devices that have not been seen for a certain amount of time.
# TODO Add ability to associate devices with a certian user or account.
# TODO Workout encryption method and key managment.


def derive_key(pairing_code: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=pairing_code.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,  # 64 MB
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )


def decrypt_pairing_data(pairing_code: str, encrypted: dict) -> dict:
    """
    Attempt to decrypt pairing data using the supplied pairing code.
    """

    salt = bytes.fromhex(encrypted["salt"])
    nonce = bytes.fromhex(encrypted["nonce"])
    ciphertext = bytes.fromhex(encrypted["ciphertext"])

    key = derive_key(pairing_code, salt)

    cipher = ChaCha20Poly1305(key)

    plaintext = cipher.decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(plaintext.decode())


class AwaitingDevice:
    def __init__(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]):
        self.device_id = device_id
        self.encrypted_data = encrypted_data
        self.platform = platform
        self.capabilities = capabilities
        self.timestamp = time.time()

    def update_timestamp(self):
        self.timestamp = time.time()


class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.awaiting_registration = []
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

    def add_awaiting_device(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]):
        if device_id in [device.device_id for device in self.awaiting_registration]:
            print(f"Device {device_id} is already awaiting registration.")
            return

        awaiting_device = AwaitingDevice(
            device_id, encrypted_data, platform, capabilities)
        self.awaiting_registration.append(awaiting_device)
        print(
            f"Added awaiting device: {device_id}, {platform}, {capabilities}")

    def register_awaiting_device(self, pairing_code: str):
        self.approved_devices.append({pairing_code, time.time()})

    def get_awaiting_devices(self):
        return self.awaiting_registration

    def get_approved_devices(self):
        return self.approved_devices

    def register_approved_device(self, pairing_code: str):
        waiting_device = None
        encrypted_data = None
        for device in self.awaiting_registration:
            try:
                encrypted_data = decrypt_pairing_data(
                    pairing_code, device.encrypted_data["data"])
            except Exception as e:
                continue
            finally:
                if encrypted_data:
                    waiting_device = device
            break

        if waiting_device == None or encrypted_data == None:
            print(
                f"Device with pairing code {pairing_code} not found in awaiting registration.")
            return

        self.approved_devices = [
            device for device in self.approved_devices if pairing_code not in device]
        self.awaiting_registration.pop(waiting_device.device_id)

        self.register_device(waiting_device.device_id, waiting_device.platform,
                             waiting_device.capabilities, encrypted_data["encryption_key"])

        print(
            f"Device {waiting_device.device_id} registered with pairing code {pairing_code}.")
