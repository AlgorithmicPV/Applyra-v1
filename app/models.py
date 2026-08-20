"""This module contains the database models used by the application."""

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

from app.extensions import db


class User(UserMixin, db.Model):
    """Store a user's account and authentication information."""

    user_id = db.Column(db.VARCHAR(36), primary_key=True)
    email = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    full_name = db.Column(db.VARCHAR(255), nullable=False)
    password_hash = db.Column(db.VARCHAR(255))
    google_id = db.Column(db.VARCHAR(255))
    auth_provider = db.Column(db.VARCHAR(45), nullable=False)
    profile_image = db.Column(db.TEXT, nullable=False)
    theme_preference = db.Column(db.VARCHAR(45), nullable=False)
    join_date = db.Column(db.TIMESTAMP, nullable=False)
    is_verified = db.Column(db.BOOLEAN)

    documents = db.relationship("Document", backref="user")
    job_entries = db.relationship("JobEntry", backref="user")
    applications = db.relationship("Application", backref="user")
    user_personal = db.relationship(
        "UserPersonal", backref="user", uselist=False
    )

    def get_id(self):
        """Return the user ID in the format required by Flask-Login.

        Returns:
            The user ID as a string.
        """

        return str(self.user_id)


class UserPersonal(db.Model):
    """Store a user's personal and contact information."""

    user_personal_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    phone_number = db.Column(db.TEXT, nullable=False)
    city = db.Column(db.TEXT, nullable=False)
    country = db.Column(db.TEXT, nullable=False)
    linkedin_url = db.Column(db.TEXT)


class Education(db.Model):
    """Store an education record belonging to a user."""

    education_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    qualification = db.Column(db.TEXT, nullable=False)
    institution = db.Column(db.TEXT, nullable=False)
    location = db.Column(db.TEXT, nullable=False)
    start_year = db.Column(db.DATE, nullable=False)
    end_year = db.Column(db.DATE, nullable=False)
    notes = db.Column(db.TEXT)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "qualification", "institution", "start_year"
        ),
    )


class Skill(db.Model):
    """Store a skill that can be selected by users."""

    skill_id = db.Column(db.VARCHAR(36), primary_key=True)
    skill_name = db.Column(db.TEXT, nullable=False, unique=True)

    user_skills = db.relationship("UserSkill", backref="skill")


class UserSkill(db.Model):
    """Connect a user with one of their selected skills."""

    user_skill_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    skill_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("skill.skill_id"), nullable=False
    )

    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)


class WorkExperience(db.Model):
    """Store a work experience record belonging to a user."""

    experience_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    job_title = db.Column(db.TEXT, nullable=False)
    company = db.Column(db.TEXT, nullable=False)
    employment_type = db.Column(db.TEXT, nullable=False)
    location = db.Column(db.TEXT, nullable=False)
    start_year = db.Column(db.DATE, nullable=False)
    end_year = db.Column(db.DATE)
    responsibilities = db.Column(db.TEXT)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "job_title",
            "company",
            "employment_type",
            "start_year",
        ),
    )


class Document(db.Model):
    """Store a generated CV or cover-letter document."""

    doc_id = db.Column(db.VARCHAR(36), primary_key=True)
    doc_type = db.Column(db.TEXT, nullable=False)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    content = db.Column(db.TEXT, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP)
    country_code = db.Column(db.VARCHAR(10))
    role = db.Column(db.TEXT, nullable=False)

    cv_documents = db.relationship(
        "Application",
        foreign_keys="Application.cv_document_id",
        backref="cv_document",
    )
    cover_letter_documents = db.relationship(
        "Application",
        foreign_keys="Application.cover_letter_document_id",
        backref="cover_letter_document",
    )


class JobEntry(db.Model):
    """Store information collected from a job posting."""

    job_entry_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    source_url = db.Column(db.TEXT, nullable=False)
    platform = db.Column(db.TEXT, nullable=False)
    job_title = db.Column(db.TEXT, nullable=False)
    company_name = db.Column(db.TEXT, nullable=False)
    country_code = db.Column(db.VARCHAR(10), nullable=False)
    captured_at = db.Column(db.TIMESTAMP, nullable=False)
    relevancy = db.Column(db.Integer, nullable=False)
    matching_skills = db.Column(db.JSON, nullable=False)
    tips = db.Column(db.TEXT)
    job_description = db.Column(db.JSON, nullable=False)

    applications = db.relationship("Application", backref="job_entry")


class Application(db.Model):
    """Connect a job entry with its generated application documents."""

    application_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False
    )
    job_entry_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("job_entry.job_entry_id"), nullable=False
    )
    cv_document_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("document.doc_id"), nullable=False
    )
    cover_letter_document_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("document.doc_id"), nullable=False
    )
