"""This module contains the forms and validation used by the application."""

import re

import phonenumbers
import requests
from argon2.exceptions import VerifyMismatchError
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    EmailField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
    URLField,
    ValidationError,
    validators,
)
from wtforms.validators import (
    AnyOf,
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    URL,
)

from app.extensions import db, get_totp, password_hasher
from app.models import User
from app.utilities.validations import (
    email_validation,
    password_strength_checker,
)


countries = [
    ("Afghanistan", "Afghanistan"),
    ("Albania", "Albania"),
    ("Algeria", "Algeria"),
    ("Andorra", "Andorra"),
    ("Angola", "Angola"),
    ("Antigua and Barbuda", "Antigua and Barbuda"),
    ("Argentina", "Argentina"),
    ("Armenia", "Armenia"),
    ("Australia", "Australia"),
    ("Austria", "Austria"),
    ("Azerbaijan", "Azerbaijan"),
    ("Bahamas", "Bahamas"),
    ("Bahrain", "Bahrain"),
    ("Bangladesh", "Bangladesh"),
    ("Barbados", "Barbados"),
    ("Belarus", "Belarus"),
    ("Belgium", "Belgium"),
    ("Belize", "Belize"),
    ("Benin", "Benin"),
    ("Bhutan", "Bhutan"),
    ("Bolivia", "Bolivia"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Botswana", "Botswana"),
    ("Brazil", "Brazil"),
    ("Brunei", "Brunei"),
    ("Bulgaria", "Bulgaria"),
    ("Burkina Faso", "Burkina Faso"),
    ("Burundi", "Burundi"),
    ("Cabo Verde", "Cabo Verde"),
    ("Cambodia", "Cambodia"),
    ("Cameroon", "Cameroon"),
    ("Canada", "Canada"),
    ("Central African Republic", "Central African Republic"),
    ("Chad", "Chad"),
    ("Chile", "Chile"),
    ("China", "China"),
    ("Colombia", "Colombia"),
    ("Comoros", "Comoros"),
    ("Congo", "Congo"),
    ("Costa Rica", "Costa Rica"),
    ("Croatia", "Croatia"),
    ("Cuba", "Cuba"),
    ("Cyprus", "Cyprus"),
    ("Czech Republic", "Czech Republic"),
    (
        "Democratic Republic of the Congo",
        "Democratic Republic of the Congo",
    ),
    ("Denmark", "Denmark"),
    ("Djibouti", "Djibouti"),
    ("Dominica", "Dominica"),
    ("Dominican Republic", "Dominican Republic"),
    ("Ecuador", "Ecuador"),
    ("Egypt", "Egypt"),
    ("El Salvador", "El Salvador"),
    ("Equatorial Guinea", "Equatorial Guinea"),
    ("Eritrea", "Eritrea"),
    ("Estonia", "Estonia"),
    ("Eswatini", "Eswatini"),
    ("Ethiopia", "Ethiopia"),
    ("Fiji", "Fiji"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("Gabon", "Gabon"),
    ("Gambia", "Gambia"),
    ("Georgia", "Georgia"),
    ("Germany", "Germany"),
    ("Ghana", "Ghana"),
    ("Greece", "Greece"),
    ("Grenada", "Grenada"),
    ("Guatemala", "Guatemala"),
    ("Guinea", "Guinea"),
    ("Guinea-Bissau", "Guinea-Bissau"),
    ("Guyana", "Guyana"),
    ("Haiti", "Haiti"),
    ("Honduras", "Honduras"),
    ("Hungary", "Hungary"),
    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Indonesia", "Indonesia"),
    ("Iran", "Iran"),
    ("Iraq", "Iraq"),
    ("Ireland", "Ireland"),
    ("Israel", "Israel"),
    ("Italy", "Italy"),
    ("Jamaica", "Jamaica"),
    ("Japan", "Japan"),
    ("Jordan", "Jordan"),
    ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"),
    ("Kiribati", "Kiribati"),
    ("Kuwait", "Kuwait"),
    ("Kyrgyzstan", "Kyrgyzstan"),
    ("Laos", "Laos"),
    ("Latvia", "Latvia"),
    ("Lebanon", "Lebanon"),
    ("Lesotho", "Lesotho"),
    ("Liberia", "Liberia"),
    ("Libya", "Libya"),
    ("Liechtenstein", "Liechtenstein"),
    ("Lithuania", "Lithuania"),
    ("Luxembourg", "Luxembourg"),
    ("Madagascar", "Madagascar"),
    ("Malawi", "Malawi"),
    ("Malaysia", "Malaysia"),
    ("Maldives", "Maldives"),
    ("Mali", "Mali"),
    ("Malta", "Malta"),
    ("Marshall Islands", "Marshall Islands"),
    ("Mauritania", "Mauritania"),
    ("Mauritius", "Mauritius"),
    ("Mexico", "Mexico"),
    ("Micronesia", "Micronesia"),
    ("Moldova", "Moldova"),
    ("Monaco", "Monaco"),
    ("Mongolia", "Mongolia"),
    ("Montenegro", "Montenegro"),
    ("Morocco", "Morocco"),
    ("Mozambique", "Mozambique"),
    ("Myanmar", "Myanmar"),
    ("Namibia", "Namibia"),
    ("Nauru", "Nauru"),
    ("Nepal", "Nepal"),
    ("Netherlands", "Netherlands"),
    ("New Zealand", "New Zealand"),
    ("Nicaragua", "Nicaragua"),
    ("Niger", "Niger"),
    ("Nigeria", "Nigeria"),
    ("North Korea", "North Korea"),
    ("North Macedonia", "North Macedonia"),
    ("Norway", "Norway"),
    ("Oman", "Oman"),
    ("Pakistan", "Pakistan"),
    ("Palau", "Palau"),
    ("Palestine", "Palestine"),
    ("Panama", "Panama"),
    ("Papua New Guinea", "Papua New Guinea"),
    ("Paraguay", "Paraguay"),
    ("Peru", "Peru"),
    ("Philippines", "Philippines"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Qatar", "Qatar"),
    ("Romania", "Romania"),
    ("Russia", "Russia"),
    ("Rwanda", "Rwanda"),
    ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
    ("Saint Lucia", "Saint Lucia"),
    (
        "Saint Vincent and the Grenadines",
        "Saint Vincent and the Grenadines",
    ),
    ("Samoa", "Samoa"),
    ("San Marino", "San Marino"),
    ("Sao Tome and Principe", "Sao Tome and Principe"),
    ("Saudi Arabia", "Saudi Arabia"),
    ("Senegal", "Senegal"),
    ("Serbia", "Serbia"),
    ("Seychelles", "Seychelles"),
    ("Sierra Leone", "Sierra Leone"),
    ("Singapore", "Singapore"),
    ("Slovakia", "Slovakia"),
    ("Slovenia", "Slovenia"),
    ("Solomon Islands", "Solomon Islands"),
    ("Somalia", "Somalia"),
    ("South Africa", "South Africa"),
    ("South Korea", "South Korea"),
    ("South Sudan", "South Sudan"),
    ("Spain", "Spain"),
    ("Sri Lanka", "Sri Lanka"),
    ("Sudan", "Sudan"),
    ("Suriname", "Suriname"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
    ("Syria", "Syria"),
    ("Taiwan", "Taiwan"),
    ("Tajikistan", "Tajikistan"),
    ("Tanzania", "Tanzania"),
    ("Thailand", "Thailand"),
    ("Timor-Leste", "Timor-Leste"),
    ("Togo", "Togo"),
    ("Tonga", "Tonga"),
    ("Trinidad and Tobago", "Trinidad and Tobago"),
    ("Tunisia", "Tunisia"),
    ("Turkey", "Turkey"),
    ("Turkmenistan", "Turkmenistan"),
    ("Tuvalu", "Tuvalu"),
    ("Uganda", "Uganda"),
    ("Ukraine", "Ukraine"),
    ("United Arab Emirates", "United Arab Emirates"),
    ("United Kingdom", "United Kingdom"),
    ("United States", "United States"),
    ("Uruguay", "Uruguay"),
    ("Uzbekistan", "Uzbekistan"),
    ("Vanuatu", "Vanuatu"),
    ("Vatican City", "Vatican City"),
    ("Venezuela", "Venezuela"),
    ("Vietnam", "Vietnam"),
    ("Yemen", "Yemen"),
    ("Zambia", "Zambia"),
    ("Zimbabwe", "Zimbabwe"),
]


class SignUpForm(FlaskForm):
    """Collect and validate the information needed to create an account."""

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired("Full name is empty"),
            validators.Length(
                min=3, message="Full name must be at least 3 characters long"
            ),
            validators.Length(
                max=255,
                message="Full name must no more than 255 characters long",
            ),
        ],
    )
    email_address = EmailField(
        "Email Address",
        validators=[
            DataRequired("Email Address is empty"),
            validators.Length(
                min=3, message="Email must be at least 3 characters long"
            ),
            validators.Length(
                max=255, message="Email must no more than 255 characters long"
            ),
            Email("Not a valid email address"),
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
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired("Confirm Password is empty"),
            validators.Length(
                min=8, message="Password must be at least 8 characters long"
            ),
            validators.Length(
                max=64, message="Password must no more than 64 characters long"
            ),
        ],
    )

    def validate_full_name(self, field):
        """Check that the full name contains valid characters.

        Args:
            field: The full-name form field.

        Raises:
            ValidationError: If the full name is not valid.
        """

        if field.data.isspace():
            raise ValidationError("Full name is empty")

        if bool(re.search(r"\d", field.data)):
            raise ValidationError("Full name can not have numbers in it")

        if not field.data.isascii():
            raise ValidationError("Full name must not have unicode characters")

    def validate_email_address(self, field):
        """Check that the email address is valid.

        Args:
            field: The email-address form field.

        Raises:
            ValidationError: If the email address is not valid.
        """

        if not email_validation(field.data, True):
            raise ValidationError("Not a valid email address")

        if not field.data.isascii():
            raise ValidationError("Email must not have unicode characters")

        if field.data.isspace():
            raise ValidationError("Email Address is empty")

        if not field.data.isascii():
            raise ValidationError("Email must not have unicode characters")

    def validate_password(self, field):
        """Check that the password uses valid characters and is strong.

        Args:
            field: The password form field.

        Raises:
            ValidationError: If the password is not valid.
        """

        if not field.data.isascii():
            raise ValidationError("Password must not have unicode characters")

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
    """Collect and validate a verification code."""

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
        """Check that the verification code contains only numbers.

        Args:
            field: The verification-code form field.

        Raises:
            ValidationError: If the code contains other characters.
        """

        if not field.data.isdigit():
            raise ValidationError("Code must contain only numbers.")


class AuthResendCodeForm(FlaskForm):
    """Provide CSRF validation when requesting another code."""

    pass


class LoginForm(FlaskForm):
    """Collect and validate the information needed to log in."""

    email_address = EmailField(
        "Email Address",
        validators=[
            validators.Length(
                min=3, message="Email must be at least 3 characters long"
            ),
            validators.Length(
                max=255, message="Email must no more than 255 characters long"
            ),
            DataRequired("Email Address is empty"),
            Email("Not a valid email address"),
            DataRequired("Full Name is empty"),
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

    def validate_full_name(self, field):
        """Check that the full name contains valid characters.

        Args:
            field: The full-name form field.

        Raises:
            ValidationError: If the full name is not valid.
        """

        if field.data.isspace():
            raise ValidationError("Full name is empty")

        if bool(re.search(r"\d", field.data)):
            raise ValidationError("Full name can not have numbers in it")

    def validate_email_address(self, field):
        """Check that the email address is valid.

        Args:
            field: The email-address form field.

        Raises:
            ValidationError: If the email address is not valid.
        """

        if not email_validation(field.data, True):
            raise ValidationError("Not a valid email address")

        if not field.data.isascii():
            raise ValidationError("Email must not have unicode characters")

        if field.data.isspace():
            raise ValidationError("Email Address is empty")

    def validate_password(self, field):
        """Check that the password contains valid characters.

        Args:
            field: The password form field.

        Raises:
            ValidationError: If the password is not valid.
        """

        if not field.data.isascii():
            raise ValidationError("Password must not have unicode characters")


# Settings forms
class SettingsCodeRequestForm(FlaskForm):
    """Provide CSRF validation when requesting a settings code."""

    pass


class SettingsTotpForm(TotpForm):
    """Collect and validate the settings verification code."""

    def validate_code(self, field):
        """Check that the settings verification code is valid.

        Args:
            field: The verification-code form field.

        Raises:
            ValidationError: If the code is invalid or expired.
        """

        super().validate_code(field)
        if not get_totp(interval=600).verify(field.data):
            raise ValidationError("The verification code is invalid or expired")


class SettingsProfileForm(FlaskForm):
    """Collect and validate profile setting changes."""

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
            Length(
                max=255,
                message="Email address cannot exceed 255 characters",
            ),
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
        """Check that the profile email is valid and available.

        Args:
            field: The email form field.

        Raises:
            ValidationError: If the email is invalid or already in use.
        """

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
    """Collect and validate a password change."""

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
        """Check that the current password is correct.

        Args:
            field: The current-password form field.

        Raises:
            ValidationError: If the password is incorrect.
        """

        try:
            password_hasher.verify(current_user.password_hash, field.data)
        except (VerifyMismatchError, TypeError):
            raise ValidationError("Current password is incorrect")

    def validate_new_password(self, field):
        """Check that the new password is strong enough.

        Args:
            field: The new-password form field.

        Raises:
            ValidationError: If the password is not strong enough.
        """

        strength = password_strength_checker(
            field.data,
            current_user.email,
            current_user.full_name,
        )
        if strength is not True:
            message = strength.get("warning") or "Please choose a stronger password"
            raise ValidationError(message)


class SettingsDeleteForm(FlaskForm):
    """Collect confirmation before deleting an account."""

    confirmation = StringField(
        "Type DELETE to confirm",
        filters=[lambda value: value.strip() if value else value],
        validators=[
            DataRequired("Type DELETE to confirm account deletion"),
            AnyOf(
                ["DELETE"],
                message="Type DELETE to confirm account deletion",
            ),
        ],
    )


class fileUplaod(FlaskForm):
    """Collect and validate an uploaded document file."""

    file = FileField(
        validators=[
            FileRequired("File is empty"),
            FileAllowed(["docx", "doc", "docm", "dotx", "dotm", "dot"]),
        ],
    )


# Onboarding forms
class UserInfoForm(FlaskForm):
    """Collect and validate the user's personal information."""

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
            validators.Length(
                max=100,
                message="City cannot exceed 100 characters",
            ),
        ],
    )

    country = SelectField(
        "Country",
        choices=countries,
        validators=[
            DataRequired("Please select the Countr Name."),
            validators.Length(
                min=2,
                max=255,
                message=("Company Name must be between 2 and 255 characters long."),
            ),
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
        """Check that the phone number is valid.

        Args:
            phone: The phone-number form field.

        Raises:
            ValidationError: If the phone number is not valid.
        """

        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid phone number")

    def validate_city(self, field):
        """Check that the city contains valid characters.

        Args:
            field: The city form field.

        Raises:
            ValidationError: If the city is not valid.
        """
        if field.data.isspace():
            raise ValidationError("City name is empty")

        if not field.data.isascii():
            raise ValidationError("City name must not have unicode characters")

        if field.data.isdigit():
            raise ValidationError("City name can not be a number")

        # Check that the city contains only letters, spaces, hyphens, or apostrophes
        if not bool(re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", field.data)):
            raise ValidationError("Invalid city name. Please enter a valid city name.")

    def validate_linkedin_url(self, field):
        """Check that the url contains valid characters.

        Args:
            field: The url form field.

        Raises:
            ValidationError: If the url is not valid.
        """

        first_part = "https://www.linkedin.com/in/"
        # There are 21 characters here
        # Check first 21 characters in the user provided link with this
        # to check, is it a valid link or not
        if field.data.strip().lower()[: len(first_part)] != first_part:
            raise ValidationError("Please enter a valid LinkedIn personal profile URL.")


class EducationForm(FlaskForm):
    """Collect and validate an education record."""

    certificate = StringField(
        "Degree / Certiications",
        validators=[
            DataRequired("Please enter your degree or certification"),
            validators.Length(
                min=2,
                message=("Degree or certification must be at least 2 characters long"),
            ),
            validators.Length(
                max=255,
                message=("Degree or certification cannot exceed 255 characters"),
            ),
        ],
    )

    institution = StringField(
        "Institution",
        validators=[
            DataRequired("Please enter the institution name."),
            validators.Length(
                min=2,
                message="Institution name must be at least 2 characters long.",
            ),
            validators.Length(
                max=150,
                message="Institution name cannot exceed 150 characters.",
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
                message=("Please enter a valid 4-digit year between 1900 and 2100."),
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
                message=("Please enter a valid 4-digit year between 1900 and 2100."),
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=1000,
                message="Description cannot exceed 1000 characters.",
            ),
        ],
    )


class SkillForm(FlaskForm):
    """Collect and validate a skill selection."""

    skill_name = SelectField(
        "Skill Name",
        choices=[],
        validators=[DataRequired("Please enter your skills.")],
        # Disable built-in choice validation because Tom Select loads the
        # options using AJAX. The server validates the submitted skill ID
        # separately against the database.
        validate_choice=False,
    )


class ExperienceForm(FlaskForm):
    """Collect and validate a work experience record."""

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
                message=("Company name must be between 2 and 150 characters long."),
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
                message=("Employment type must be between 2 and 50 characters long."),
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
    """Collect and validate a job-posting link."""

    job_url = URLField(
        "Job Link",
        validators=[
            DataRequired("Please paste the Job Link."),
            URL(message="Invalid URL. Please include http:// or https://"),
        ],
    )

    def validate_url(self, field):
        """Check that the job-posting link can be reached.

        Args:
            field: The job-link form field.

        Raises:
            ValidationError: If the link cannot be reached.
        """

        try:
            response = requests.get(field.data, timeout=5, allow_redirects=True)

            if response.status_code >= 400:
                raise ValidationError("This link is not working.")

        except requests.RequestException:
            raise ValidationError("Unable to reach this link.")


class JobForm(FlaskForm):
    """Collect and validate the information from a job posting."""

    source_url = URLField(
        "Job Link",
        validators=[
            DataRequired("Please paste the Job Link."),
            URL(message="Invalid URL. Please include http:// or https://"),
        ],
    )

    job_title = StringField(
        "Job Role",
        validators=[
            DataRequired("Please paste the Job Role."),
            validators.Length(
                min=2,
                max=255,
                message="Job Role must be between 2 and 255 characters long.",
            ),
        ],
    )

    company_name = StringField(
        "Company Name",
        validators=[
            DataRequired("Please paste the Company Name."),
            validators.Length(
                min=2,
                max=255,
                message=("Company Name must be between 2 and 255 characters long."),
            ),
        ],
    )

    country_code = SelectField(
        "Country Name",
        choices=countries,
        validators=[
            DataRequired("Please paste the Company Name."),
            validators.Length(
                min=2,
                max=255,
                message=("Company Name must be between 2 and 255 characters long."),
            ),
        ],
    )

    job_description = TextAreaField(
        "Job Description",
        validators=[
            DataRequired("Please paste the Job Description."),
            Length(
                max=8000,
                min=100,
                message=(
                    "Job Description must be between 100 and 8000 characters long"
                ),
            ),
        ],
    )

    def validate_url(self, field):
        """Check that the job-posting link can be reached.

        Args:
            field: The job-link form field.

        Raises:
            ValidationError: If the link cannot be reached.
        """

        try:
            response = requests.get(field.data, timeout=5, allow_redirects=True)

            if response.status_code >= 400:
                raise ValidationError("This link is not working.")

        except requests.RequestException:
            raise ValidationError("Unable to reach this link.")
