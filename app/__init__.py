from app.extensions import db, migrate
from flask import Flask, session
from flask_cors import CORS
from flask_migrate import Migrate
from app.models import User
from config import Config


def create_app(debug=False):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # https only
        SESSION_COOKIE_SAMESITE="Lax",
    )

    app.debug = debug
    CORS(app, supports_credentials=True)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    with app.app_context():
        db.create_all()

    Migrate(app, db)

    return app
