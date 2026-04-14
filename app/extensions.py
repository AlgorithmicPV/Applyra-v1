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
serializer = URLSafeTimedSerializer("temporary")
migrate = Migrate()
password_hasher = PasswordHasher()
login_manager = LoginManager()


def get_totp():
    secret = current_app.config["OTP_SECRET"]
    return pyotp.TOTP(secret)


def get_fernet():
    secret = current_app.config["FERNET_KEY"]
    return Fernet(secret)


def get_aessiv():
    secret = current_app.config["FERNET_KEY"]
    return AESSIV(secret)
