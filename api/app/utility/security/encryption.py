import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()

AES_KEY = bytes.fromhex(os.getenv("AES_SECRET_KEY") or "")

if not AES_KEY:
    raise RuntimeError("Missing required secret: AES_SECRET_KEY")


def encrypt_field(value: str) -> str:
    """Encrypt a string using AES-256-GCM (returns base64 string)."""
    aesgcm = AESGCM(AES_KEY)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, value.encode("utf-8"), associated_data=None)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt_field(encrypted_base64: str) -> str:
    """Decrypt a base64-encoded AES-256-GCM encrypted value."""
    data = base64.b64decode(encrypted_base64)
    iv, ciphertext = data[:12], data[12:]
    return AESGCM(AES_KEY).decrypt(iv, ciphertext, associated_data=None).decode("utf-8")
