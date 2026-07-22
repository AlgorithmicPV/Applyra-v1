from flask import (
    Blueprint,
    render_template,
    session,
    abort,
)
from app.forms import AuthResendCodeForm, SignUpForm, TotpForm, LoginForm
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from app.utilities.validations import email_confirm

auth_web_bp = Blueprint("auth_web", __name__)
AUTH_TOTP_INTERVAL = 120


@auth_web_bp.route("/sign-up", methods=["POST", "GET"])
def sign_up():
    form = SignUpForm()
    return render_template("auth/base.html", form=form, title="Sign Up", page="sign-up")


@auth_web_bp.route("/login")
def login():
    form = LoginForm()
    return render_template("auth/base.html", form=form, title="Login", page="login")


@auth_web_bp.route("/email-validation")
def totp():

    # This session varaible is sent via backend, it has to be verify
    # Otherwise, users can get into this page, via url
    # Now, If they do, they get 403
    if not (session.get(hash_key("email-confirm"))):
        abort(403)

    email_confirm(
        user_email=decrypt_value(session.get(hash_key("user-email"))),
        interval=AUTH_TOTP_INTERVAL,
    )

    del session[hash_key("email-confirm")]

    # Same as the above, but vice versa, This is for the secuirty of the application
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
