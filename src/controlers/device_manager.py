"""
Webdisplay Server
Device Manager

License: MIT license

Author: C2311231

Notes:
"""
import asyncio
import json
import os

from src.models.player import PlayerDevice
from src.models.player_config import PlayerConfig
import time
import uuid

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

import logging

# TODO Add ability to associate devices with a certian user or account.
# TODO Add ability to automatically cycle pairing codes for security purposes.

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
    logging.debug(f"Decrypted pairing data: {plaintext.decode()}")
    return json.loads(plaintext.decode())


def encrypt_command(key: bytes, data: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)

    cipher = ChaCha20Poly1305(key)
    ciphertext = cipher.encrypt(nonce, data, None)

    return nonce, ciphertext


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes | None:
    cipher = ChaCha20Poly1305(key)

    try:
        return cipher.decrypt(nonce, ciphertext, None)
    except ValueError:
        logging.error("Decryption failed. Invalid key or corrupted data.")
        return None
        


class AwaitingDevice:
    def __init__(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]):
        self.device_id = device_id
        self.encrypted_data = encrypted_data
        self.platform = platform
        self.capabilities = capabilities
        self.timestamp = time.time()
        self.encryption_key = None

    def update_timestamp(self):
        self.timestamp = time.time()

    def __str__(self):
        return f"AwaitingDevice(device_id={self.device_id}, platform={self.platform}, capabilities={self.capabilities}, timestamp={self.timestamp}), encrypted_data={self.encrypted_data}"

class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.awaiting_registration = []
        self.approved_devices = []


    ## Complete registration from player approval to ensure that the player is still available to be paired with and that the player can verify the pairing code itself.
    def register_device(self, device_id: str, data: dict):
        found_device = None
        
        for device in self.awaiting_registration:
            if device.device_id == device_id:
                decrypted_data = decrypt(device.encryption_key, bytes.fromhex(data["nonce"]), bytes.fromhex(data["ciphertext"]))
                if decrypted_data:
                    found_device = device
                    self.awaiting_registration.remove(device)
                    break
                found_device = device
                self.awaiting_registration.remove(device)
                break
            
        if found_device is None:
            logging.error(f"Device {device_id} not found in awaiting registration.")
            return
        
            
        config_id = str(uuid.uuid4())
        config = PlayerConfig(config_id, f"Player {device_id}", "default")

        if device_id in self.devices:
            self.devices[device_id].update_timestamp()
            logging.info(f"Device {device_id} is already registered.")
            return

        device = PlayerDevice(device_id, config_id,
                              found_device.platform, found_device.capabilities, found_device.encryption_key)
        self.devices[device_id] = device
        logging.info(
            f"Registered device: {device_id}, {config_id}, {found_device.platform}, {found_device.capabilities}")
        
    def approve_device(self, device_id: str):
        if device_id in self.devices:
            self.devices[device_id].update_timestamp()
            logging.info(f"Device {device_id} is already approved.")
            return

        approved_device = None
        for device in self.awaiting_registration:
            if device.device_id == device_id:
                approved_device = device
                self.awaiting_registration.remove(device)
                break
            
    
        self.approved_devices.append(approved_device)
        logging.info(
            f"Approved device: {approved_device}")

    def get_device(self, device_id: str):
        return self.devices.get(device_id, None)

    def list_devices(self):
        return self.devices

    def add_awaiting_device(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]):
        if device_id in [device.device_id for device in self.awaiting_registration] or device_id in self.devices or device_id in [device.device_id for device in self.approved_devices]:
            logging.info(f"Device {device_id} is already awaiting registration.")
            return

        awaiting_device = AwaitingDevice(
            device_id, encrypted_data, platform, capabilities)
        self.awaiting_registration.append(awaiting_device)
        logging.info(
            f"Added awaiting device: {device_id}, {platform}, {capabilities}")

    def get_awaiting_devices(self):
        return self.awaiting_registration

    def get_approved_devices(self):
        return self.approved_devices

    def approved_device(self, pairing_code: str):
        waiting_device = None
        encrypted_data = None
        for device in self.awaiting_registration:
            if device.timestamp < time.time() - 20: # 20 seconds
                logging.info(
                    f"Device {device.device_id} has been awaiting registration for more than 20 seconds. Removing from awaiting registration.")
                self.awaiting_registration.remove(device)
                continue
            
            logging.debug(device)
            try:
                encrypted_data = decrypt_pairing_data(
                    pairing_code, device.encrypted_data)
            except Exception as e:
                logging.error(e)
                continue
            finally:
                if encrypted_data:
                    waiting_device = device

        if waiting_device == None or encrypted_data == None:
            logging.error(
                f"Device with pairing code {pairing_code} not found in awaiting registration.")
            return

        waiting_device.pairing_code = pairing_code
        waiting_device.encryption_key = encrypted_data["encryption_key"]
        self.approved_devices.append(waiting_device)
        self.awaiting_registration.remove(waiting_device)

        self.approve_device(waiting_device.device_id)

        logging.info(
            f"Device {waiting_device.device_id} registered with pairing code {pairing_code}.")

    def get_pairing_status(self, device_id: str):
        for device in self.awaiting_registration:
            if device.device_id == device_id:
                device.update_timestamp()
                return "awaiting_registration", None
        for device in self.approved_devices:
            device.update_timestamp()
            if device.device_id == device_id:
                data, nonce = encrypt_command(device.encryption_key, b"pairing_code_verified")
                return "approved", {"nonce": nonce.hex(), "ciphertext": data.hex()}
        if device_id in self.devices:
            return "registered", None
        return "not_found", None
    
    ### Temporary method for testing purposes. Remove in production.
    
    async def read_pairing_codes(self):
        while True:
            text = await asyncio.to_thread(
                input,
                "Enter pairing code to register device: "
            )

            self.approved_device(text)