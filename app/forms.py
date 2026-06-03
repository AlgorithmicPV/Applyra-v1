from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField,
    PasswordField,
    EmailField,
    validators,
    ValidationError,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from app.models import User
from app.utilities.validations import email_validation, password_strength_checker


class SignUpForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired("Full Name is empty"),
            validators.Length(
                min=3, message="Full name must be at least 3 characters long"
            ),
            validators.Length(
                max=255, message="Full name must no more than 255 characters long"
            ),
        ],
    )
    email_address = EmailField(
        "Email Address",
        validators=[
            DataRequired("Email Address is empty"),
            Email("Not a valid email address"),
            DataRequired("Full Name is empty"),
            validators.Length(
                min=3, message="Full name must be at least 3 characters long"
            ),
            validators.Length(
                max=255, message="Full name must no more than 255 characters long"
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired("Password is empty"),
            EqualTo("confirm_password", message="Passwords must match"),
            validators.Length(
                min=8, message="Password must be at least 8 characters long"
            ),
            validators.Length(
                max=64, message="Password must no more than 64 characters long"
            ),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

    def validate_email_address(self, field):
        if not email_validation(field.data, True):
            raise ValidationError("Not a valid email address")

    def validate_password(self, field):
        if not (
            password_strength_checker(
                field.data, self.full_name.data, self.email_address.data
            )
        ):
            password_feedback = password_strength_checker(
                field.data, self.full_name.data, self.email_address.data
            )
            raise ValidationError(password_feedback)


class TotpForm(FlaskForm):
    code = StringField(
        "Verification Code",
        validators=[
            DataRequired("Verification code is missing"),
            validators.Length(
                min=6, max=6, message="Verification code must be 6 characters"
            ),
        ],
        render_kw={
            "inputmode": "numeric",
            "pattern": "[0-9]*",
            "autocomplete": "one-time-code",
            "maxlength": "6",
        },
    )

    def validate_code(self, field):
        if not field.data.isdigit():
            raise ValidationError("Code must contain only numbers.")


class LoginForm(FlaskForm):
    email_address = EmailField(
        "Email Address",
        validators=[
            DataRequired("Email Address is empty"),
            Email("Not a valid email address"),
            DataRequired("Full Name is empty"),
            validators.Length(
                min=3, message="Full name must be at least 3 characters long"
            ),
            validators.Length(
                max=255, message="Full name must no more than 255 characters long"
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired("Password is empty"),
            validators.Length(
                min=8, message="Password must be at least 8 characters long"
            ),
            validators.Length(
                max=64, message="Password must no more than 64 characters long"
            ),
        ],
    )

    def validate_email_address(self, field):
        if not email_validation(field.data, True):
            raise ValidationError("Not a valid email address")


class fileUplaod(FlaskForm):
    file = FileField(
        validators=[
            FileRequired("File is empty"),
            FileAllowed(["docx", "doc", "docm", "dotx", "dotm", "dot"]),
        ],
    )
