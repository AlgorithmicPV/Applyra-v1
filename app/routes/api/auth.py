"""
This module covers all the authentications in the system
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, url_for, redirect, session, abort
from sqlalchemy import and_
from argon2.exceptions import VerifyMismatchError
from flask_login import login_user, current_user
from app.forms import AuthResendCodeForm, SignUpForm, TotpForm, LoginForm
from app.extensions import limiter, password_hasher, db, get_totp
from app.models import User, UserSkill, WorkExperience, Education, UserPersonal
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from app.utilities.validations import email_confirm

auth_api_bp = Blueprint("auth_api", __name__)


current_datetime = datetime.now()
current_timestamp = current_datetime.timestamp()
AUTH_TOTP_INTERVAL = 120  # 2 minutes


@auth_api_bp.post("/sign-up/")
@limiter.limit("1 per 3 seconds; 5 per minute; 20 per hour")
def sign_up():
    """Save new users to the system

    Returns:
        _type_: _description_
    """

    form = SignUpForm(request.form)

    if not form.validate():
        return form.errors

    # Trim spaces and convert all letters to lowercase (only email_address)
    email_address = form.email_address.data.strip().lower()
    print(email_address)
    full_name = form.full_name.data.strip()

    email_exist = db.session.execute(
        db.select(User).where(and_(User.email == email_address))
    ).first()

    if email_exist is None:
        # Add a brand new user
        user_id = str(uuid.uuid4())
        new_user = User(
            user_id=user_id,
            email=email_address,
            full_name=full_name,
            password_hash=password_hasher.hash(form.password.data),
            auth_provider="manual",
            profile_image="https://placehold.co/300x300",
            theme_preference="dark",
            join_date=current_datetime,
            is_verified=False,
        )

        db.session.add(new_user)

    else:
        if email_exist.User.is_verified and email_exist.User.email:
            return {"error": "User email is existing"}
        # If the email is in the database, and not verified,
        # it will update only, the full name, password, auth_provider
        # also makes the google_id None, because,
        # if the email is loggined though gmail
        # but haven't verified, we need to update that
        email_exist.User.full_name = full_name
        email_exist.User.password_hasher = password_hasher.hash(form.password.data)
        email_exist.User.auth_provider = "manual"
        email_exist.User.profile_image = "https://placehold.co/300x300"
        email_exist.User.theme_preference = "dark"
        email_exist.User.join_date = current_datetime
        email_exist.User.google_id = None

    db.session.commit()

    user_email = email_address

    session[hash_key("user-email")] = encrypt_value(user_email)
    session[hash_key("email-confirm")] = encrypt_value("1")

    return redirect(url_for("auth_web.totp"))


@auth_api_bp.post("/confirm/")
def confirm_email():

    if not session.get(hash_key("email-confirm-backend")):
        abort(403)

    form = TotpForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    if not get_totp(interval=AUTH_TOTP_INTERVAL).verify(form.code.data):
        return {"error": "Token has expired"}

    unverified_user = db.session.execute(
        db.select(User).where(
            and_(
                User.email == decrypt_value(session.get(hash_key("user-email"))),
                User.is_verified is not True,
            )
        )
    ).first()
    if not unverified_user:
        return {"error": "User is not existing"}

    unverified_user.User.is_verified = True

    db.session.commit()
    session.pop(hash_key("email-confirm-backend"), None)

    return redirect(url_for("auth_web.login"))


@auth_api_bp.post("/resend-code/")
@limiter.limit("1 per 30 seconds; 5 per 10 minutes")
def resend_code():
    if not session.get(hash_key("email-confirm-backend")):
        abort(403)

    form = AuthResendCodeForm()
    if not form.validate_on_submit():
        return {"error": next(iter(form.errors.values()))[0]}, 400

    encrypted_email = session.get(hash_key("user-email"))
    if not encrypted_email:
        abort(403)

    result = email_confirm(
        user_email=decrypt_value(encrypted_email),
        interval=AUTH_TOTP_INTERVAL,
    )
    if isinstance(result, dict) and result.get("error"):
        return result, 500
    return {"success": "A new verification code has been sent"}


@auth_api_bp.post("/login/")
def login():

    form = LoginForm(request.form)

    if not form.validate():
        return form.errors

    email_exist = db.session.execute(
        db.select(User).where(
            and_(User.email == form.email_address.data.strip().lower())
        )
    ).first()

    if not email_exist:
        return {"error": "User email does not exist"}

    if not email_exist.User.is_verified:
        return {"error": "User email is not verified"}

    try:
        password_hasher.verify(email_exist.User.password_hash, form.password.data)
    except VerifyMismatchError:
        return {"error": "Login is failed"}

    login_user(
        user=email_exist.User,
        remember=True,
        duration=None,
        # NOTE: Change this later: duration
        force=False,
        fresh=True,
    )

    session["first-access-to-app-via-htmx"] = True

    # Check whether, the user has completed the onboarding,
    # if yes, user will be redirected to the app,
    # if no, user will be redirected to the onboarding page
    stmt_skill = (
        db.select(UserSkill).where(UserSkill.user_id == current_user.user_id).exists()
    )
    stmt_experience = (
        db.select(WorkExperience)
        .where(WorkExperience.user_id == current_user.user_id)
        .exists()
    )
    stmt_education = (
        db.select(Education).where(Education.user_id == current_user.user_id).exists()
    )
    stmt_user_profile = (
        db.select(UserPersonal)
        .where(UserPersonal.user_id == current_user.user_id)
        .exists()
    )

    # Before redirecting to the login page,
    # check whether the user has completed the onboarding process.

    # Scalar gives a boolean output, True, or False
    # Pages are organized in the same order as the website structure.
    # The route function names are used as the page names.
    # This helps avoid writing repetitive code.
    onboarding_status = {
        "user": db.session.scalar(db.select(stmt_user_profile)),
        "education": db.session.scalar(db.select(stmt_education)),
        "skills": db.session.scalar(db.select(stmt_education)),
        "experience": db.session.scalar(db.select(stmt_experience)),
    }

    # If all are False, it will redirect to onboarding home page
    # False + False + False + False = 0, because False is 0
    if sum(list(onboarding_status.values())) == 0:
        return redirect(url_for("onboarding_web.home"))

    for page, status in onboarding_status.items():
        if status == False:
            return redirect(url_for(f"onboarding_web.{page}"))

    return redirect(url_for("apply_web.apply"))
