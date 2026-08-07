"""This module creates the shared Flask extensions and security helpers."""

import pyotp
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()
limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)
# This temporary key will be updated by app/__init__.py.
serializer = URLSafeTimedSerializer("temporary")
migrate = Migrate()
password_hasher = PasswordHasher()
login_manager = LoginManager()


def get_totp(interval=30):
    """Create a time-based one-time password generator.

    Args:
        interval: The number of seconds before the password expires.

    Returns:
        A configured TOTP generator.
    """

    return pyotp.TOTP(current_app.config["OTP_SECRET"], interval=interval)


def get_fernet():
    """Create a Fernet helper using the application key.

    Returns:
        A configured Fernet helper.
    """

    return Fernet(current_app.config["FERNET_KEY"])


def get_aessiv():
    """Create an AES-SIV helper using the application key.

    Returns:
        A configured AES-SIV helper.
    """

    return AESSIV(current_app.config["FERNET_KEY"])
