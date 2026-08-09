"""This module creates and configures the Flask application."""

import pyotp
from flask import Flask, session
from flask_cors import CORS
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer

from config import Config

from app.extensions import (
    db,
    limiter,
    login_manager,
    mail,
    migrate,
    serializer,
)
from app.models import User

from app.errors.handlers import register_error_handlers


def create_app(debug=False):
    """Create and configure the Flask application.

    Args:
        debug: Whether Flask debug mode should be enabled.

    Returns:
        The configured Flask application.
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["MAIL_SERVER"] = Config.MAIL_SERVER
    app.config["MAIL_PORT"] = Config.MAIL_PORT
    app.config["MAIL_USE_TLS"] = Config.MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = Config.MAIL_USE_SSL
    app.config["MAIL_USERNAME"] = Config.MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = Config.MAIL_PASSWORD
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["OTP_SECRET"] = Config.OTP_SECRET
    app.config["FERNET_KEY"] = Config.FERNET_SECRET

    # app.config["RECAPTCHA_PUBLIC_KEY"] = Config.RECAPTCHA_PUBLIC_KEY
    # app.config["RECAPTCHA_PRIVATE_KEY"] = Config.RECAPTCHA_PRIVATE_KEY

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # HTTPS only
        SESSION_COOKIE_SAMESITE="Lax",
    )

    app.debug = debug
    CORS(app, supports_credentials=True)

    # Initialize the Flask extensions.
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth_web.login"
    register_error_handlers(app)

    # Load the logged-in user from the database using their session ID.
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user using the ID stored in the session.

        Args:
            user_id: The ID of the logged-in user.

        Returns:
            The matching user, or None if the user does not exist.
        """

        return User.query.get(user_id)

    # Replace the temporary serializer key from the extensions module.
    # WARNING: Try to improve this later, or keep it if needed.
    if Config.SECRET_KEY is not None:
        serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

    # from app import models

    # with app.app_context():
    #    db.create_all()

    Migrate(app, db)

    # Register API blueprints.
    from app.routes.api.auth import auth_api_bp
    from app.routes.api.documents import documents_api_bp
    from app.routes.api.onboarding import onboarding_api_bp
    from app.routes.api.apply import apply_api_bp
    from app.routes.api.settings import settings_api_bp

    # Register web blueprints.
    from app.routes.web.landing import landing_web_bp
    from app.routes.web.auth import auth_web_bp
    from app.routes.web.documents import documents_web_bp
    from app.routes.web.onboarding import onboarding_web_bp
    from app.routes.web.apply import apply_web_bp
    from app.routes.web.settings import settings_web_bp

    # API routes.
    app.register_blueprint(auth_api_bp, url_prefix="/api/auth")
    app.register_blueprint(documents_api_bp, url_prefix="/api/doc")
    app.register_blueprint(onboarding_api_bp, url_prefix="/api/onboarding")
    app.register_blueprint(apply_api_bp, url_prefix="/api/apply")
    app.register_blueprint(settings_api_bp, url_prefix="/api/settings")

    # Web routes.
    app.register_blueprint(landing_web_bp, url_prefix="/")
    app.register_blueprint(auth_web_bp)
    app.register_blueprint(documents_web_bp)
    app.register_blueprint(onboarding_web_bp, url_prefix="/onboarding")
    app.register_blueprint(apply_web_bp)
    app.register_blueprint(settings_web_bp)

    return app
