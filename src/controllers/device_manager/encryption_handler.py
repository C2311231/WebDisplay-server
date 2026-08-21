"""
Webdisplay Server
Device Manager Encryption Handler

License: MIT license

Author: C2311231

Notes:
"""

import json
import os

import argon2.low_level
import cryptography.hazmat.primitives.ciphers.aead

import logging


def derive_key(pairing_code: str, salt: bytes | str) -> bytes:
    if type(salt) != bytes:
        salt = bytes.fromhex(salt)

    return argon2.low_level.hash_secret_raw(
        secret=pairing_code.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,  # 64 MB
        parallelism=4,
        hash_len=32,
        type=argon2.low_level.Type.ID,
    )


def encrypt_msg(key: bytes | str, data: dict) -> tuple[bytes, bytes]:
    if type(key) != bytes:
        key = bytes.fromhex(key)
    nonce: bytes = os.urandom(12)

    buffer = bytes(json.dumps(data), "utf-8")

    cipher: cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305 = cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305(
        key)
    ciphertext: bytes = cipher.encrypt(nonce, buffer, None)

    return nonce, ciphertext


def decrypt_msg(key: bytes | str, nonce: bytes | str, ciphertext: bytes | str) -> bytes | None:
    if type(key) != bytes:
        key = bytes.fromhex(key)
    if type(nonce) != bytes:
        nonce = bytes.fromhex(nonce)
    if type(ciphertext) != bytes:
        ciphertext = bytes.fromhex(ciphertext)

    cipher: cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305 = cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305(
        key)

    try:
        return cipher.decrypt(nonce, ciphertext, None)
    except ValueError:
        logging.error("Decryption failed. Invalid key or corrupted data.")
        return None
