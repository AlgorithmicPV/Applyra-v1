"""This module encrypts and hashes values used in client sessions."""

import hashlib

from app.extensions import get_fernet


def encrypt_value(value: str) -> str:
    """Encrypt a string before storing it in the client session.

    Args:
        value: The string that needs to be encrypted.

    Returns:
        The encrypted value as a string.
    """

    encrypted_bytes = get_fernet().encrypt(value.encode())
    # Convert the encrypted bytes into a string.
    return encrypted_bytes.decode()


def decrypt_value(value: str) -> str:
    """Decrypt a string taken from the client session.

    Args:
        value: The encrypted string that needs to be decrypted.

    Returns:
        The decrypted value as a string.
    """

    # Convert the string to bytes before decrypting it.
    decrypted_bytes = get_fernet().decrypt(value.encode())
    return decrypted_bytes.decode()


def hash_key(key: str) -> str:
    """Create a one-way hash for a session key.

    Args:
        key: The session key that needs to be hashed.

    Returns:
        The SHA-256 hash as a hexadecimal string.
    """

    hashed_key = hashlib.sha256(key.encode()).hexdigest()
    return hashed_key
