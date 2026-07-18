from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField,
    PasswordField,
    EmailField,
    validators,
    ValidationError,
    IntegerField,
    TextAreaField,
    SelectField,
    URLField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
    Length,
    URL,
    AnyOf,
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from app.models import User
from app.utilities.validations import email_validation, password_strength_checker
import requests
import phonenumbers
from argon2.exceptions import VerifyMismatchError
from flask_login import current_user
from app.extensions import db, get_totp, password_hasher


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


class AuthResendCodeForm(FlaskForm):
    pass


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


# Settings forms
class SettingsCodeRequestForm(FlaskForm):
    pass


class SettingsTotpForm(TotpForm):
    def validate_code(self, field):
        super().validate_code(field)
        if not get_totp(interval=600).verify(field.data):
            raise ValidationError("The verification code is invalid or expired")


class SettingsProfileForm(FlaskForm):
    full_name = StringField(
        "Full name",
        filters=[lambda value: value.strip() if value else value],
        validators=[
            DataRequired("Full name is empty"),
            Length(
                min=3,
                max=255,
                message="Full name must be between 3 and 255 characters",
            ),
        ],
    )
    email = EmailField(
        "Email address",
        filters=[lambda value: value.strip().lower() if value else value],
        validators=[
            DataRequired("Email address is empty"),
            Email("Enter a valid email address"),
            Length(max=255, message="Email address cannot exceed 255 characters"),
        ],
    )
    profile_image = FileField(
        "Profile picture",
        validators=[
            Optional(),
            FileAllowed(
                ["png", "jpg", "jpeg", "gif", "webp"],
                "Profile picture must be a PNG, JPG, GIF, or WebP image",
            ),
        ],
    )

    def validate_email(self, field):
        if not email_validation(field.data, False):
            raise ValidationError("Enter a valid email address")

        existing_user = db.session.scalar(
            db.select(User).where(
                User.email == field.data,
                User.user_id != current_user.user_id,
            )
        )
        if existing_user:
            raise ValidationError("That email address is already in use")


class SettingsPasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current password",
        validators=[DataRequired("Current password is empty")],
    )
    new_password = PasswordField(
        "New password",
        validators=[
            DataRequired("New password is empty"),
            Length(
                min=8,
                max=64,
                message="Password must be between 8 and 64 characters",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired("Please confirm your new password"),
            EqualTo("new_password", message="New passwords do not match"),
        ],
    )

    def validate_current_password(self, field):
        try:
            password_hasher.verify(current_user.password_hash, field.data)
        except (VerifyMismatchError, TypeError):
            raise ValidationError("Current password is incorrect")

    def validate_new_password(self, field):
        strength = password_strength_checker(
            field.data,
            current_user.email,
            current_user.full_name,
        )
        if strength is not True:
            message = strength.get("warning") or "Please choose a stronger password"
            raise ValidationError(message)


class SettingsDeleteForm(FlaskForm):
    confirmation = StringField(
        "Type DELETE to confirm",
        filters=[lambda value: value.strip() if value else value],
        validators=[
            DataRequired("Type DELETE to confirm account deletion"),
            AnyOf(["DELETE"], message="Type DELETE to confirm account deletion"),
        ],
    )


class fileUplaod(FlaskForm):
    file = FileField(
        validators=[
            FileRequired("File is empty"),
            FileAllowed(["docx", "doc", "docm", "dotx", "dotm", "dot"]),
        ],
    )


# Onboarding forms
class UserInfoForm(FlaskForm):
    phone = StringField(
        "Phone", validators=[DataRequired("Please enter your phone number")]
    )

    city = StringField(
        "City",
        validators=[
            DataRequired("Please enter your city"),
            validators.Length(
                min=3,
                message="City must be at least 3 characters long",
            ),
            validators.Length(max=100, message="City cannot exceed 100 characters"),
        ],
    )

    country = StringField(
        "Country",
        validators=[
            DataRequired("Please enter your country"),
            validators.Length(
                min=3,
                message="Country must be at least 3 characters long",
            ),
            validators.Length(max=100, message="Country cannot exceed 100 characters"),
        ],
    )

    linkedin_url = URLField(
        "Linkedin URL",
        validators=[
            Optional(),
            URL(message="Invalid URL. Please include http:// or https://"),
        ],
    )

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid phone number")


class EducationForm(FlaskForm):
    certificate = StringField(
        "Degree / Certiications",
        validators=[
            DataRequired("Please enter your degree or certification"),
            validators.Length(
                min=2,
                message="Degree or certification must be at least 2 characters long",
            ),
            validators.Length(
                max=255, message="Degree or certification cannot exceed 255 characters"
            ),
        ],
    )

    institution = StringField(
        "Institution",
        validators=[
            DataRequired("Please enter the institution name."),
            validators.Length(
                min=2, message="Institution name must be at least 2 characters long."
            ),
            validators.Length(
                max=150, message="Institution name cannot exceed 150 characters."
            ),
        ],
    )

    location = StringField(
        "Location",
        validators=[
            DataRequired("Please enter the institution location."),
            validators.Length(
                min=2, message="Location must be at least 2 characters long."
            ),
            validators.Length(
                max=100, message="Location cannot exceed 100 characters."
            ),
        ],
    )

    start_year = IntegerField(
        "Start Year",
        validators=[
            DataRequired("Please enter the start year."),
            NumberRange(
                min=1900,
                max=2100,
                message="Please enter a valid 4-digit year between 1900 and 2100.",
            ),
        ],
    )

    end_year = IntegerField(
        "End Year",
        validators=[
            DataRequired("Please enter the end year."),
            NumberRange(
                min=1900,
                max=2100,
                message="Please enter a valid 4-digit year between 1900 and 2100.",
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=1000, message="Description cannot exceed 1000 characters."),
        ],
    )


class SkillForm(FlaskForm):
    skill_name = SelectField(
        "Skill Name",
        choices=[],
        validators=[DataRequired("Please enter your skills.")],
        # Disable built-in WTForms choice validation because the options are loaded
        # dynamically on the client via Tom Select (AJAX) rather than being populated
        # in the field's choices list. The submitted skill ID is validated separately
        # on the server against the database.
        validate_choice=False,
    )


class ExperienceForm(FlaskForm):
    job_title = StringField(
        "Job Title",
        validators=[
            DataRequired("Please enter your job title."),
            validators.Length(
                min=2,
                max=100,
                message="Job title must be between 2 and 100 characters long.",
            ),
        ],
    )

    company = StringField(
        "Company",
        validators=[
            DataRequired("Please enter the company name."),
            validators.Length(
                min=2,
                max=150,
                message="Company name must be between 2 and 150 characters long.",
            ),
        ],
    )

    employment_type = SelectField(
        "Employment Type",
        choices=[
            ("Full-time", "Full-time"),
            ("Part-time", "Part-time"),
            ("Permanent", "Permanent"),
            ("Temporary", "Temporary"),
            ("Fixed-term", "Fixed-term"),
            ("Casual", "Casual"),
            ("Contract", "Contract"),
            ("Seasonal", "Seasonal"),
            ("Freelance", "Freelance"),
            ("Intership", "Intership"),
            ("Apprenticeship", "Apprenticeship"),
        ],
        validators=[
            DataRequired("Please select the employment type."),
            validators.Length(
                min=2,
                max=50,
                message="Employment type must be between 2 and 50 characters long.",
            ),
        ],
    )

    start_year = IntegerField(
        "Start Year",
        validators=[
            DataRequired("Please enter the start year."),
            NumberRange(
                min=1950,
                max=2100,
                message="Please enter a valid year between 1950 and 2100.",
            ),
        ],
    )

    end_year = IntegerField(
        "End Year",
        validators=[
            DataRequired("Please enter the end year."),
            NumberRange(
                min=1950,
                max=2100,
                message="Please enter a valid year between 1950 and 2100.",
            ),
        ],
    )

    location = StringField(
        "Location",
        validators=[
            DataRequired("Please enter the job location."),
            validators.Length(
                min=2,
                max=100,
                message="Location must be between 2 and 100 characters long.",
            ),
        ],
    )

    responsibilities = TextAreaField(
        "Responsibilities",
        validators=[
            Optional(),
            Length(
                max=2000,
                message="Responsibilities cannot exceed 2000 characters.",
            ),
        ],
    )


class JobLinkForm(FlaskForm):
    job_url = URLField(
        "Job Link",
        validators=[
            DataRequired("Please paste the Job Link."),
            URL(message="Invalid URL. Please include http:// or https://"),
        ],
    )

    def validate_url(self, field):
        try:
            response = requests.get(field.data, timeout=5, allow_redirects=True)

            if response.status_code >= 400:
                raise ValidationError("This link is not working.")

        except requests.RequestException:
            raise ValidationError("Unable to reach this link.")
