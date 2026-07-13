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
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from app.models import User
from app.utilities.validations import email_validation, password_strength_checker
import requests


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


class JobEntry(FlaskForm):
    job_url = URLField(
        "Job Link",
        validators=[
            DataRequired("Please paste the Job Link."),
            URL(message="Invalid URL. Please include http:// or https://"),
        ],
    )

    job_title = StringField(
        "Job Title",
        validators=[
            DataRequired("Please paste your job title."),
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
            DataRequired("Please paste the company name."),
            validators.Length(
                min=2,
                max=150,
                message="Company name must be between 2 and 150 characters long.",
            ),
        ],
    )

    platform = StringField(
        "Platform",
        validators=[
            DataRequired("Please enter the platform name."),
            validators.Length(
                min=2,
                max=150,
                message="Platform name must be between 2 and 150 characters long.",
            ),
        ],
    )

    job_description = TextAreaField(
        "Job description",
        validators=[
            DataRequired("Please paste the Job Description."),
            Length(max=6000, message="Description cannot exceed 6000 characters."),
        ],
    )

    due_date = DateField(
        "Due Date",
        format="%Y-%m-%d",
        validators=[DataRequired("Please Enter the Due Date for this application")],
    )

    country = SelectField(
        "Country Name",
        choices=[
            ("afghanistan", "Afghanistan"),
            ("albania", "Albania"),
            ("algeria", "Algeria"),
            ("andorra", "Andorra"),
            ("angola", "Angola"),
            ("antigua-and-barbuda", "Antigua and Barbuda"),
            ("argentina", "Argentina"),
            ("armenia", "Armenia"),
            ("australia", "Australia"),
            ("austria", "Austria"),
            ("azerbaijan", "Azerbaijan"),
            ("bahamas", "Bahamas"),
            ("bahrain", "Bahrain"),
            ("bangladesh", "Bangladesh"),
            ("barbados", "Barbados"),
            ("belarus", "Belarus"),
            ("belgium", "Belgium"),
            ("belize", "Belize"),
            ("benin", "Benin"),
            ("bhutan", "Bhutan"),
            ("bolivia", "Bolivia"),
            ("bosnia-and-herzegovina", "Bosnia and Herzegovina"),
            ("botswana", "Botswana"),
            ("brazil", "Brazil"),
            ("brunei", "Brunei"),
            ("bulgaria", "Bulgaria"),
            ("burkina-faso", "Burkina Faso"),
            ("burundi", "Burundi"),
            ("cabo-verde", "Cabo Verde"),
            ("cambodia", "Cambodia"),
            ("cameroon", "Cameroon"),
            ("canada", "Canada"),
            ("central-african-republic", "Central African Republic"),
            ("chad", "Chad"),
            ("chile", "Chile"),
            ("china", "China"),
            ("colombia", "Colombia"),
            ("comoros", "Comoros"),
            ("congo", "Congo"),
            ("costa-rica", "Costa Rica"),
            ("cote-divoire", "Côte d'Ivoire"),
            ("croatia", "Croatia"),
            ("cuba", "Cuba"),
            ("cyprus", "Cyprus"),
            ("czechia", "Czechia"),
            ("democratic-republic-of-the-congo", "Democratic Republic of the Congo"),
            ("denmark", "Denmark"),
            ("djibouti", "Djibouti"),
            ("dominica", "Dominica"),
            ("dominican-republic", "Dominican Republic"),
            ("ecuador", "Ecuador"),
            ("egypt", "Egypt"),
            ("el-salvador", "El Salvador"),
            ("equatorial-guinea", "Equatorial Guinea"),
            ("eritrea", "Eritrea"),
            ("estonia", "Estonia"),
            ("eswatini", "Eswatini"),
            ("ethiopia", "Ethiopia"),
            ("fiji", "Fiji"),
            ("finland", "Finland"),
            ("france", "France"),
            ("gabon", "Gabon"),
            ("gambia", "Gambia"),
            ("georgia", "Georgia"),
            ("germany", "Germany"),
            ("ghana", "Ghana"),
            ("greece", "Greece"),
            ("grenada", "Grenada"),
            ("guatemala", "Guatemala"),
            ("guinea", "Guinea"),
            ("guinea-bissau", "Guinea-Bissau"),
            ("guyana", "Guyana"),
            ("haiti", "Haiti"),
            ("honduras", "Honduras"),
            ("hungary", "Hungary"),
            ("iceland", "Iceland"),
            ("india", "India"),
            ("indonesia", "Indonesia"),
            ("iran", "Iran"),
            ("iraq", "Iraq"),
            ("ireland", "Ireland"),
            ("israel", "Israel"),
            ("italy", "Italy"),
            ("jamaica", "Jamaica"),
            ("japan", "Japan"),
            ("jordan", "Jordan"),
            ("kazakhstan", "Kazakhstan"),
            ("kenya", "Kenya"),
            ("kiribati", "Kiribati"),
            ("kuwait", "Kuwait"),
            ("kyrgyzstan", "Kyrgyzstan"),
            ("laos", "Laos"),
            ("latvia", "Latvia"),
            ("lebanon", "Lebanon"),
            ("lesotho", "Lesotho"),
            ("liberia", "Liberia"),
            ("libya", "Libya"),
            ("liechtenstein", "Liechtenstein"),
            ("lithuania", "Lithuania"),
            ("luxembourg", "Luxembourg"),
            ("madagascar", "Madagascar"),
            ("malawi", "Malawi"),
            ("malaysia", "Malaysia"),
            ("maldives", "Maldives"),
            ("mali", "Mali"),
            ("malta", "Malta"),
            ("marshall-islands", "Marshall Islands"),
            ("mauritania", "Mauritania"),
            ("mauritius", "Mauritius"),
            ("mexico", "Mexico"),
            ("micronesia", "Micronesia"),
            ("moldova", "Moldova"),
            ("monaco", "Monaco"),
            ("mongolia", "Mongolia"),
            ("montenegro", "Montenegro"),
            ("morocco", "Morocco"),
            ("mozambique", "Mozambique"),
            ("myanmar", "Myanmar"),
            ("namibia", "Namibia"),
            ("nauru", "Nauru"),
            ("nepal", "Nepal"),
            ("netherlands", "Netherlands"),
            ("new-zealand", "New Zealand"),
            ("nicaragua", "Nicaragua"),
            ("niger", "Niger"),
            ("nigeria", "Nigeria"),
            ("north-korea", "North Korea"),
            ("north-macedonia", "North Macedonia"),
            ("norway", "Norway"),
            ("oman", "Oman"),
            ("pakistan", "Pakistan"),
            ("palau", "Palau"),
            ("palestine", "Palestine"),
            ("panama", "Panama"),
            ("papua-new-guinea", "Papua New Guinea"),
            ("paraguay", "Paraguay"),
            ("peru", "Peru"),
            ("philippines", "Philippines"),
            ("poland", "Poland"),
            ("portugal", "Portugal"),
            ("qatar", "Qatar"),
            ("romania", "Romania"),
            ("russia", "Russia"),
            ("rwanda", "Rwanda"),
            ("saint-kitts-and-nevis", "Saint Kitts and Nevis"),
            ("saint-lucia", "Saint Lucia"),
            ("saint-vincent-and-the-grenadines", "Saint Vincent and the Grenadines"),
            ("samoa", "Samoa"),
            ("san-marino", "San Marino"),
            ("sao-tome-and-principe", "São Tomé and Príncipe"),
            ("saudi-arabia", "Saudi Arabia"),
            ("senegal", "Senegal"),
            ("serbia", "Serbia"),
            ("seychelles", "Seychelles"),
            ("sierra-leone", "Sierra Leone"),
            ("singapore", "Singapore"),
            ("slovakia", "Slovakia"),
            ("slovenia", "Slovenia"),
            ("solomon-islands", "Solomon Islands"),
            ("somalia", "Somalia"),
            ("south-africa", "South Africa"),
            ("south-korea", "South Korea"),
            ("south-sudan", "South Sudan"),
            ("spain", "Spain"),
            ("sri-lanka", "Sri Lanka"),
            ("sudan", "Sudan"),
            ("suriname", "Suriname"),
            ("sweden", "Sweden"),
            ("switzerland", "Switzerland"),
            ("syria", "Syria"),
            ("tajikistan", "Tajikistan"),
            ("tanzania", "Tanzania"),
            ("thailand", "Thailand"),
            ("timor-leste", "Timor-Leste"),
            ("togo", "Togo"),
            ("tonga", "Tonga"),
            ("trinidad-and-tobago", "Trinidad and Tobago"),
            ("tunisia", "Tunisia"),
            ("turkey", "Turkey"),
            ("turkmenistan", "Turkmenistan"),
            ("tuvalu", "Tuvalu"),
            ("uganda", "Uganda"),
            ("ukraine", "Ukraine"),
            ("united-arab-emirates", "United Arab Emirates"),
            ("united-kingdom", "United Kingdom"),
            ("united-states", "United States"),
            ("uruguay", "Uruguay"),
            ("uzbekistan", "Uzbekistan"),
            ("vanuatu", "Vanuatu"),
            ("vatican-city", "Vatican City"),
            ("venezuela", "Venezuela"),
            ("vietnam", "Vietnam"),
            ("yemen", "Yemen"),
            ("zambia", "Zambia"),
            ("zimbabwe", "Zimbabwe"),
        ],
        validators=[
            DataRequired("Please select the country."),
            validators.Length(
                min=2,
                max=50,
                message="Country name must be between 2 and 50 characters long.",
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
