"""This module handles the frontend routes for authentication pages."""

from flask import (
    Blueprint,
    abort,
    render_template,
    session,
)

from app.forms import AuthResendCodeForm, LoginForm, SignUpForm, TotpForm
from app.utilities.client_sessions import (
    decrypt_value,
    encrypt_value,
    hash_key,
)
from app.utilities.validations import email_confirm

auth_web_bp = Blueprint("auth_web", __name__)
AUTH_TOTP_INTERVAL = 120


@auth_web_bp.route("/sign-up/", methods=["POST", "GET"])
def sign_up():
    """Display the sign-up page.

    Returns:
        The rendered sign-up page.
    """

    form = SignUpForm()
    return render_template("auth/base.html", form=form, title="Sign Up", page="sign-up")


@auth_web_bp.get("/login/")
def login():
    """Display the login page.

    Returns:
        The rendered login page.
    """

    form = LoginForm()
    return render_template("auth/base.html", form=form, title="Login", page="login")


@auth_web_bp.get("/email-validation/")
def totp():
    """Send a verification code and display the email validation page.

    Returns:
        The rendered email validation page.
    """

    # This session value is sent by the backend and must be verified.
    # Without it, users receive a 403 response when visiting the URL directly.
    if not (session.get(hash_key("email-confirm"))):
        abort(403)

    email_send_result = email_confirm(
        user_email=decrypt_value(session.get(hash_key("user-email"))),
        interval=AUTH_TOTP_INTERVAL,
    )

    if email_send_result.get("error"):
        return {"error": email_send_result.get("error")}

    del session[hash_key("email-confirm")]

    # Allow the backend to confirm that the user opened this page correctly.
    session[hash_key("email-confirm-backend")] = encrypt_value("1")

    form = TotpForm()
    resend_form = AuthResendCodeForm()
    return render_template(
        "auth/base.html",
        form=form,
        resend_form=resend_form,
        title="Email Validation",
        page="totp",
    )
