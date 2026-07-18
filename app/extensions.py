from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_migrate import Migrate
from argon2 import PasswordHasher
import pyotp
from flask import current_app
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESSIV


db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()
limiter = Limiter(get_remote_address, default_limits=[], storage_uri="memory://")
serializer = URLSafeTimedSerializer("temporary")  # This will be updated by __init__.py
migrate = Migrate()
password_hasher = PasswordHasher()
login_manager = LoginManager()


def get_totp(interval=30):
    return pyotp.TOTP(current_app.config["OTP_SECRET"], interval=interval)


def get_fernet():
    return Fernet(current_app.config["FERNET_KEY"])


def get_aessiv():
    return AESSIV(current_app.config["FERNET_KEY"])
