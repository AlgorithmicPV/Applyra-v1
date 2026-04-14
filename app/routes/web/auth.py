from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    current_app,
    session,
    abort,
)
from app.forms import SignUpForm, TotpForm, LoginForm
from app.extensions import get_fernet
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from app.utilities.validations import email_confirm

auth_web_bp = Blueprint("auth_web", __name__)


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

    # if not session.get(hash_key("email-confirm")):
    #    abort(403)
    if not (session.get(hash_key("email-confirm"))):
        abort(403)

    email_confirm(user_email=decrypt_value(session.get(hash_key("user-email"))))

    del session[hash_key("email-confirm")]

    session[hash_key("email-confirm-backend")] = encrypt_value("1")

    form = TotpForm()
    return render_template(
        "auth/base.html", form=form, title="Email Validation", page="totp"
    )
