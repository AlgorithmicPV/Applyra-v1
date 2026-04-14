from app.extensions import get_fernet, get_aessiv, password_hasher
import base64
import hashlib


def encrypt_value(value: str) -> str:
    encrypted_bytes = get_fernet().encrypt(value.encode())
    return encrypted_bytes.decode()  # bytes -> string


def decrypt_value(value: str) -> str:
    decrypted_bytes = get_fernet().decrypt(value.encode())  # string -> bytes
    return decrypted_bytes.decode()


# one way hashing for the key
def hash_key(key: str) -> str:
    hashed_key = hashlib.sha256(key.encode()).hexdigest()
    return hashed_key
