from app.extensions import (
    db,
    mail,
    limiter,
    serializer,
    migrate,
    login_manager,
)
from flask import Flask, session
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from itsdangerous import URLSafeTimedSerializer
import pyotp
from app.models import User

# NOTE: Remember there is a lib called flask-htmx


def create_app(debug=False):
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

    #    app.config["RECAPTCHA_PUBLIC_KEY"] = Config.RECAPTCHA_PUBLIC_KEY
    # app.config["RECAPTCHA_PRIVATE_KEY"] = Config.RECAPTCHA_PRIVATE_KEY

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # https only
        SESSION_COOKIE_SAMESITE="Lax",
    )

    app.debug = debug
    CORS(app, supports_credentials=True)

    # init extensions
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    #    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    if Config.SECRET_KEY is not None:
        serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

    # from app import models

    # with app.app_context():
    #    db.create_all()

    Migrate(app, db)

    # register api blueprints
    from app.routes.api.auth import auth_api_bp
    from app.routes.api.documents import documents_api_bp

    # register web blueprints
    from app.routes.web.landing import landing_web_bp
    from app.routes.web.auth import auth_web_bp
    from app.routes.web.dashboard import dashboard_web_bp
    from app.routes.web.documents import documents_web_bp
    from app.routes.web.onboarding import onboarding_web_bp

    # api
    app.register_blueprint(auth_api_bp, url_prefix="/api/auth")
    app.register_blueprint(documents_api_bp, url_prefix="/api/doc")

    # web
    app.register_blueprint(landing_web_bp, url_prefix="/")
    app.register_blueprint(auth_web_bp)
    app.register_blueprint(dashboard_web_bp)
    app.register_blueprint(documents_web_bp)
    app.register_blueprint(onboarding_web_bp, url_prefix="/onboarding")

    return app
