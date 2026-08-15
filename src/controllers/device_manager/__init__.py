"""
Webdisplay Server
Device Manager

License: MIT license

Author: C2311231

Notes:
"""
import asyncio
from typing import NoReturn


import src.models.player
import src.models.player_config
import time
import uuid

import logging

from .encryption_handler import decrypt_pairing_data, encrypt_msg, decrypt_msg
from .device import Device

# TODO Add ability to associate devices with a certian user or account.
# TODO Add ability to automatically cycle pairing codes for security purposes.


class DeviceManager:
    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}

    def register_device_by_id(self, device_id: str, data: dict) -> None:
        """Completes registration process for a player

        Args:
            device_id (str): ID of the device to register
            data (dict): Encrypted data for identity verification

        Raises:
            ValueError: Device does not have a encryption key yet.
            ValueError: Device not found in awaiting registration.
            ValueError: Device is already registered.
        """
        found_device = None
        devices = self.get_approved_devices()
        if device_id in devices:
            device = devices[device_id]
            if device.encryption_key is None:
                logging.error(
                    f"Device {device_id} does not have an encryption key. Cannot decrypt pairing data.")
                raise ValueError(
                    f"Device {device_id} does not have an encryption key. Cannot decrypt pairing data.")

            decrypted_data = decrypt_msg(device.encryption_key, bytes.fromhex(
                data["nonce"]), bytes.fromhex(data["ciphertext"]))

            if decrypted_data:
                found_device = device

        if found_device is None:
            logging.error(
                f"Device {device_id} not found in awaiting registration.")
            raise ValueError(
                f"Device {device_id} not found in awaiting registration.")

        config_id = str(uuid.uuid4())
        config = src.models.player_config.PlayerConfig(
            config_id, f"Player {device_id}", "default")

        if device_id in self.devices:
            self.devices[device_id].update_timestamp()
            logging.info(f"Device {device_id} is already registered.")
            raise ValueError(f"Device {device_id} is already registered.")

        # device = src.models.player.PlayerDevice(device_id, config_id,
        #                                         found_device.platform, found_device.capabilities, found_device.encryption_key)

        found_device.set_status("online")
        logging.info(
            f"Registered device: {device_id}, {config_id}, {found_device.platform}, {found_device.capabilities}")

    def approve_device(self, device_id: str) -> None:
        """Marks a device as approved so that it can be registered

        Args:
            device_id (str): ID of the device to approve

        Raises:
            ValueError: Device not found.
            ValueError: Device is already approved.
        """
        if device_id not in self.devices:
            logging.error(f"Device {device_id} not found.")
            raise ValueError(f"Device {device_id} not found.")

        if self.devices[device_id].status in ["awaiting_verification", "online", "offline"]:
            self.devices[device_id].update_timestamp()
            logging.info(f"Device {device_id} is already approved.")
            raise ValueError(f"Device {device_id} is already approved.")

        for device in self.devices.values():
            if device.device_id == device_id:
                device.set_status("awaiting_verification")
                logging.info(
                    f"Approved device: {device_id}, {device.platform}, {device.capabilities}")
                break

    def get_device(self, device_id: str) -> Device | None:
        """Returns the device with the provided ID

        Args:
            device_id (str): ID of the device to retrieve

        Returns:
            Device | None: The device object if found, otherwise None
        """
        return self.devices.get(device_id, None)

    def get_devices(self) -> dict[str, Device]:
        return self.devices

    def add_awaiting_device(self, device_id: str, encrypted_data: dict, platform: str, capabilities: list[str]) -> None:
        """Creates a discovered player device.

        Args:
            device_id (str): The ID of the discovered device.
            encrypted_data (dict): A encrypted blob containing the encryption key and pairing data.
            platform (str): The platform the software is installed on.
            capabilities (list[str]): A list of the players capabilities.

        Raises:
            ValueError: Device is already waiting to be registered.
        """
        if device_id in self.devices:
            logging.info(
                f"Device {device_id} is already awaiting registration.")
            raise ValueError(
                f"Device {device_id} is already awaiting registration.")

        awaiting_device = Device(
            device_id, encrypted_data, platform, capabilities)
        self.devices[device_id] = awaiting_device
        logging.info(
            f"Added awaiting device: {device_id}, {platform}, {capabilities}")

    def get_awaiting_devices(self) -> dict[str, Device]:
        """Returns devices that are awaiting approval.

        Returns:
            dict[str, Device]: A dictionary of devices that are awaiting approval.
        """
        return {device_id: self.devices[device_id] for device_id in self.devices if self.devices[device_id].status == "pending"}

    def get_approved_devices(self) -> dict[str, Device]:
        """Returns devices that are approved.

        Returns:
            dict[str, Device]: A dictionary of devices that are approved.
        """
        return {device_id: self.devices[device_id] for device_id in self.devices if self.devices[device_id].status == "awaiting_verification" or self.devices[device_id].status == "online"}

    def approved_device_by_pairing_code(self, pairing_code: str) -> None:
        """Marks a device as approved.

        Args:
            pairing_code (str): The pairing code used to approve the device.

        Raises:
            ValueError: A device with the requested pairing code wasn't found.
        """
        waiting_device = None
        encrypted_data = None
        for device_id in self.get_awaiting_devices():
            device = self.devices[device_id]
            if device.last_seen < time.time() - 20:  # 20 seconds
                logging.info(
                    f"Device {device.device_id} has been awaiting registration for more than 20 seconds. Removing from awaiting registration.")
                device.set_status("error")
                continue

            try:
                encrypted_data = decrypt_pairing_data(
                    pairing_code, device.encrypted_data)
            except Exception as e:
                logging.error(e)
                continue

            if encrypted_data:
                waiting_device = device
                break

        if waiting_device == None or encrypted_data == None:
            logging.error(
                f"Device with pairing code {pairing_code} not found in awaiting registration.")
            raise ValueError(
                f"Device with pairing code {pairing_code} not found in awaiting registration.")

        waiting_device.pairing_code = pairing_code
        waiting_device.encryption_key = encrypted_data["encryption_key"]
        waiting_device.set_status("awaiting_verification")

        self.approve_device(waiting_device.device_id)

        logging.info(
            f"Device {waiting_device.device_id} registered with pairing code {pairing_code}.")

    def get_pairing_status(self, device_id: str) -> str:
        """Returns the pairing status of a device.

        Args:
            device_id (str): ID of the requested device.

        Raises:
            ValueError: Device doesnt exist.

        Returns:
            str: The status of the device.
        """
        if device_id not in self.devices:
            logging.error(f"Device {device_id} not found.")
            raise ValueError(f"Device {device_id} not found.")

        return self.devices[device_id].status

    # Temporary method for testing purposes. Remove in production.

    async def read_pairing_codes(self) -> NoReturn:
        while True:
            text: str = await asyncio.to_thread(
                input,
                "Enter pairing code to register device: "
            )

            self.approved_device_by_pairing_code(text)
