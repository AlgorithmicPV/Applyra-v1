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
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
    Length,
)
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


# Onboarding forms
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

    employment_type = StringField(
        "Employment Type",
        validators=[
            DataRequired("Please enter the employment type."),
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
