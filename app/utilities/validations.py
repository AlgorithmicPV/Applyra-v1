"""This module contains shared validation and email helpers."""

import smtplib

from email_validator import EmailNotValidError, validate_email
from flask_mail import Message
from zxcvbn import zxcvbn

from app.extensions import get_totp, mail, serializer


def email_validation(user_email: str, check_deliverability: bool):
    """Validate and normalize a user's email address.

    Args:
        user_email: The email address that needs to be validated.
        check_deliverability: Whether to check if the email can receive mail.

    Returns:
        The normalized email address, or False if it is not valid.
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


def password_strength_checker(password: str, email: str, full_name: str):
    """Check the strength of a password using the user's information.

    Args:
        password: The password that needs to be checked.
        email: The user's email address.
        full_name: The user's full name.

    Returns:
        True if the password is strong, or a dictionary containing feedback.
    """

    results = zxcvbn(password, user_inputs=[email, full_name])

    if (
        results["feedback"]["warning"] == ""
        and len(results["feedback"]["suggestions"]) == 0
    ):
        return True
    else:
        return results["feedback"]


def email_confirm(user_email: str, interval=30):
    """Send an email containing a verification code.

    Args:
        user_email: The email address that receives the code.
        interval: The number of seconds before the code expires.

    Returns:
        An error dictionary if sending fails, otherwise None.
    """

    token = serializer.dumps(user_email, salt="email-confirm")

    msg = Message(
        "Confirm Email",
        sender="pasinduvidunitha08@gmail.com",
        recipients=[user_email],
    )

    code = get_totp(interval=interval).now()
    msg.body = (
        f"Your verification code is {code}. It expires in {interval // 60} minutes."
    )

    try:
        mail.send(msg)
    except (smtplib.SMTPException, OSError) as e:
        error = f"Error sending email: {e}"
        print(error)
        return {"error": error}
