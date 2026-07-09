from app.extensions import db
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin


class User(UserMixin, db.Model):
    user_id = db.Column(db.VARCHAR(36), primary_key=True)
    email = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    full_name = db.Column(db.VARCHAR(255), nullable=False)
    password_hash = db.Column(db.VARCHAR(255))
    google_id = db.Column(db.VARCHAR(255))
    auth_provider = db.Column(db.VARCHAR(45), nullable=False)
    profile_image = db.Column(db.TEXT, nullable=False)
    theme_preference = db.Column(db.VARCHAR(45), nullable=False)
    join_date = db.Column(db.TIMESTAMP, nullable=False)
    onbaording_completed = db.Column(db.BOOLEAN, nullable=False)
    is_verified = db.Column(db.BOOLEAN)

    practice_answers = db.relationship("PracticeAnswer", backref="user")
    documents = db.relationship("Document", backref="user")
    job_entries = db.relationship("JobEntry", backref="user")
    applications = db.relationship("Application", backref="user")

    def get_id(self):
        return str(self.user_id)


class Education(db.Model):
    education_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    qualification = db.Column(db.TEXT, nullable=False)
    institution = db.Column(db.TEXT, nullable=False)
    location = db.Column(db.TEXT, nullable=False)
    start_year = db.Column(db.DATE, nullable=False)
    end_year = db.Column(db.DATE, nullable=False)
    notes = db.Column(db.TEXT)

    __table_args__ = (
        UniqueConstraint("user_id", "qualification", "institution", "start_year"),
    )


class Skill(db.Model):
    skill_id = db.Column(db.VARCHAR(36), primary_key=True)
    skill_name = db.Column(db.TEXT, nullable=False, unique=True)

    user_skills = db.relationship("UserSkill", backref="skill")


class UserSkill(db.Model):
    user_skill_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    skill_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("skill.skill_id"), nullable=False
    )

    __table_args__ = (UniqueConstraint("user_id", "skill_id"),)


class WorkExperience(db.Model):
    experience_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
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


class Question(db.Model):
    question_id = db.Column(db.VARCHAR(36), primary_key=True)
    question_text = db.Column(db.TEXT, nullable=False)
    category = db.Column(db.TEXT, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)

    practice_answers = db.relationship("PracticeAnswer", backref="question")


class PracticeAnswer(db.Model):
    practice_answer_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    question_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("question.question_id"), nullable=False
    )
    user_answer = db.Column(db.TEXT, nullable=False)
    ai_suggested_answer = db.Column(db.TEXT)
    tone_feedback = db.Column(db.TEXT)
    clarity_feedback = db.Column(db.TEXT)
    impact_feedback = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP)


class Template(db.Model):
    template_id = db.Column(db.VARCHAR(36), primary_key=True)
    doc_type = db.Column(db.TEXT, nullable=False)
    country_code = db.Column(db.VARCHAR(10), nullable=False)
    template_content = db.Column(db.TEXT, nullable=False)

    documents = db.relationship("Document", backref="template")


class Document(db.Model):
    doc_id = db.Column(db.VARCHAR(36), primary_key=True)
    doc_type = db.Column(db.TEXT, nullable=False)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    template_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("template.template_id"), nullable=False
    )
    content = db.Column(db.TEXT, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP)
    country_code = db.Column(db.VARCHAR(10))
    role = db.Column(db.TEXT, nullable=False)

    cv_documents = db.relationship(
        "Application", foreign_keys="Application.cv_document_id", backref="cv_document"
    )
    cover_letter_documents = db.relationship(
        "Application",
        foreign_keys="Application.cover_letter_document_id",
        backref="cover_letter_document",
    )


class JobEntry(db.Model):
    job_entry_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    source_url = db.Column(db.TEXT, nullable=False)
    platform = db.Column(db.TEXT, nullable=False)
    job_title = db.Column(db.TEXT, nullable=False)
    company_name = db.Column(db.TEXT, nullable=False)
    country_code = db.Column(db.VARCHAR(10), nullable=False)
    job_descripton = db.Column(db.TEXT, nullable=False)
    due_date = db.Column(db.DATETIME)
    captured_at = db.Column(db.TIMESTAMP, nullable=False)
    relevancy = db.Column(db.Integer, nullable=False)
    matching_skills = db.Column(db.TEXT, nullable=False)
    tips = db.Column(db.TEXT)

    applications = db.relationship("Application", backref="job_entry")


class Application(db.Model):
    application_id = db.Column(db.VARCHAR(36), primary_key=True)
    user_id = db.Column(db.VARCHAR(36), db.ForeignKey("user.user_id"), nullable=False)
    job_entry_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("job_entry.job_entry_id"), nullable=False
    )
    cv_document_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("document.doc_id"), nullable=False
    )
    cover_letter_document_id = db.Column(
        db.VARCHAR(36), db.ForeignKey("document.doc_id"), nullable=False
    )
    status = db.Column(db.VARCHAR(255), nullable=False)
    applied_on = db.Column(db.TIMESTAMP, nullable=False)
    notes = db.Column(db.TEXT)
