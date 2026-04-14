import smtplib
from zxcvbn import zxcvbn
from email_validator import validate_email, EmailNotValidError
from wtforms.validators import ValidationError
from app.extensions import mail, serializer, get_totp
from flask_mail import Message
from flask import url_for


def email_validation(user_email: str, check_deliverability: bool):
    """Validate the user email with email-validator lib

    Args:
        user_email (str)

    Returns:

    """
    try:
        emailinfo = validate_email(
            user_email, check_deliverability=check_deliverability
        )
        print(emailinfo)
        user_email = emailinfo.normalized
        return user_email

    except EmailNotValidError:
        return False
    # raise ValidationError("Not a valid email address")


def password_strength_checker(password: str, email: str, full_name: str):
    results = zxcvbn(password, user_inputs=[email, full_name])

    if (
        results["feedback"]["warning"] == ""
        and len(results["feedback"]["suggestions"]) == 0
    ):
        # return results
        return True
    else:
        return results["feedback"]


def email_confirm(user_email: str):
    token = serializer.dumps(user_email, salt="email-confirm")

    msg = Message(
        "Confirm Email",
        sender="pasinduvidunitha08@gmail.com",
        recipients=[user_email],
    )

    code = get_totp().now()
    msg.body = f"Your code is {code}"

    try:
        mail.send(msg)
    except (smtplib.SMTPException, OSError) as e:
        error = f"Error sending email: {e}"
        print(error)
        return {"error": error}
