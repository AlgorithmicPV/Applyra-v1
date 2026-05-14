"""
This module covers all the authentications in the system
"""

import uuid
from flask import Blueprint, current_app, request, url_for, redirect, session, abort
from app.forms import SignUpForm, TotpForm, LoginForm
from itsdangerous import SignatureExpired, BadSignature
from app.extensions import mail, limiter, serializer, password_hasher, db, get_totp
from app.models import User
from datetime import datetime
from sqlalchemy import and_
import time
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin, login_user


auth_api_bp = Blueprint("auth_api", __name__)


current_datetime = datetime.now()
current_timestamp = current_datetime.timestamp()


@auth_api_bp.route("/sign-up", methods=["POST", "GET"])
@limiter.limit("1 per 3 seconds; 5 per minute; 20 per hour")
def sign_up():
    """Save new users to the system

    Returns:
        _type_: _description_
    """

    form = SignUpForm(request.form)

    if not (request.method == "POST" and form.validate()):
        print("not pass")
        return form.errors

    email_exist = db.session.execute(
        db.select(User).where(and_(User.email == form.email_address.data))
    ).first()

    if email_exist is None:
        # Add a brand new user
        user_id = str(uuid.uuid4())

        new_user = User(
            user_id=user_id,
            email=form.email_address.data,
            full_name=form.full_name.data,
            password_hash=password_hasher.hash(form.password.data),
            auth_provider="manual",
            profile_image="https://placehold.co/300x300",
            theme_preference="dark",
            join_date=current_datetime,
            onbaording_completed=False,
            is_verified=False,
        )

        db.session.add(new_user)
    else:
        if email_exist.User.is_verified and email_exist.User.email:
            return {"error": "User email is existing"}
        # If the email is in the database, and not verified,
        # it will update only, the full name, password, auth_provider
        # also makes the google_id None, because, if the email is loggined though gmail
        # but haven't verified, we need to update that
        email_exist.User.full_name = form.full_name.data
        email_exist.User.password_hasher = password_hasher.hash(form.password.data)
        email_exist.User.auth_provider = "manual"
        email_exist.User.profile_image = "https://placehold.co/300x300"
        email_exist.User.theme_preference = "dark"
        email_exist.User.join_date = current_datetime
        email_exist.User.google_id = None

    db.session.commit()

    user_email = form.email_address.data

    session[hash_key("user-email")] = encrypt_value(user_email)
    session[hash_key("email-confirm")] = encrypt_value("1")

    return redirect(url_for("auth_web.totp"))


@auth_api_bp.route("/confirm/", methods=["GET", "POST"])
def confirm_email():

    if not (session.get(hash_key("email-confirm-backend"))):
        abort(403)

    del session[hash_key("email-confirm-backend")]

    form = TotpForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    if not get_totp().verify(form.code.data):
        return {"error": "Token has expired"}

    unverified_user = db.session.execute(
        db.select(User).where(
            and_(
                User.email == decrypt_value(session.get(hash_key("user-email"))),
                User.is_verified != True,
            )
        )
    ).first()
    if not unverified_user.User.email:
        return {"error": "User is not existing"}

    unverified_user.User.is_verified = True

    db.session.commit()

    return redirect(url_for("auth_web.login"))


# Change this to flask-login
@auth_api_bp.route("/login/", methods=["GET", "POST"])
def login():

    form = LoginForm(request.form)

    if not (request.method == "POST" and form.validate()):
        print("not pass")
        return form.errors

    email_exist = db.session.execute(
        db.select(User).where(and_(User.email == form.email_address.data))
    ).first()

    if not (email_exist.User.email):
        return {"error": "User email does not exist"}

    if not (email_exist.User.is_verified):
        return {"error": "User email is not verified"}

    try:
        password_hasher.verify(email_exist.User.password_hash, form.password.data)
    except VerifyMismatchError:
        return {"error": "Login is failed"}

    login_user(
        user=email_exist.User,
        remember=True,
        duration=None,
        force=False,
        fresh=True,
    )

    session["first-access-to-dashboard-via-htmx"] = True

    return redirect(url_for("dashboard_web.dashboard"))
