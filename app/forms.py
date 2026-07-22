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


class JobForm(FlaskForm):
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
                message="Company Name must be between 2 and 255 characters long.",
            ),
        ],
    )

    country_code = SelectField(
        "Country Name",
        choices=[
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
            ("Democratic Republic of the Congo", "Democratic Republic of the Congo"),
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
            ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
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
        ],
        validators=[
            DataRequired("Please paste the Company Name."),
            validators.Length(
                min=2,
                max=255,
                message="Company Name must be between 2 and 255 characters long.",
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
                message="Job Description must be between 100 and 8000 characters long",
            ),
        ],
    )

    def validate_url(self, field):
        try:
            response = requests.get(field.data, timeout=5, allow_redirects=True)

            if response.status_code >= 400:
                raise ValidationError("This link is not working.")

        except requests.RequestException:
            raise ValidationError("Unable to reach this link.")
