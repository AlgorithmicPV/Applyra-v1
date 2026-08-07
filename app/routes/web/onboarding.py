"""This module handles the frontend routes for the onboarding pages."""

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import EducationForm, ExperienceForm, SkillForm, UserInfoForm
from app.models import Education, Skill, UserSkill, WorkExperience

onboarding_web_bp = Blueprint("onboarding_web", __name__)


@onboarding_web_bp.route("/", methods=["POST", "GET"])
@login_required
def home():
    """Display the onboarding home page.

    Returns:
        The rendered onboarding home page.
    """

    return render_template("onboarding/base.html", page="home")


@onboarding_web_bp.route("/you", methods=["POST", "GET"])
@login_required
def user():
    """Display the personal information onboarding page.

    Returns:
        The full page or partial personal information HTML for HTMX.
    """

    form = UserInfoForm()
    if request.headers.get("HX-Request") == "true":
        return render_template(
            "onboarding/user_info.html",
            form=form,
            title="Your info",
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="user_info",
            form=form,
            title="Your info",
        )


@onboarding_web_bp.route("/education/", methods=["POST", "GET"])
@login_required
def education():
    """Display the current user's education information.

    Returns:
        The full page or partial education HTML for an HTMX request.
    """

    form = EducationForm()

    qualifications = db.session.scalars(
        db.select(Education).where(Education.user_id == current_user.user_id)
    ).all()

    # Remove the user ID before sending the SQLAlchemy data to the frontend.
    qualifications_frontend = []

    for qualification in qualifications:
        q = {
            "education_id": qualification.education_id,
            "qualification": qualification.qualification,
            "institution": qualification.institution,
            "location": qualification.location,
            "start_year": qualification.start_year,
            "end_year": qualification.end_year,
            "notes": qualification.notes,
        }
        qualifications_frontend.append(q)

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "onboarding/education.html",
            form=form,
            qualifications=qualifications_frontend,
            title="Your Education Background",
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="education",
            form=form,
            qualifications=qualifications_frontend,
            title="Your Education Background",
        )


@onboarding_web_bp.route("/experience/", methods=["POST", "GET"])
@login_required
def experience():
    """Display the current user's work experience information.

    Returns:
        The full page or partial experience HTML for an HTMX request.
    """

    form = ExperienceForm()

    work_experiences = db.session.scalars(
        db.select(WorkExperience).where(
            WorkExperience.user_id == current_user.user_id
        )
    ).all()

    work_experiences_frontend = []

    for experience in work_experiences:
        e = {
            "experience_id": experience.experience_id,
            "job_title": experience.job_title,
            "company": experience.company,
            "employment_type": experience.employment_type,
            "location": experience.location,
            "start_year": experience.start_year.year,
            "end_year": experience.end_year.year,
            "responsibilities": experience.responsibilities,
        }
        work_experiences_frontend.append(e)

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "onboarding/experience.html",
            form=form,
            experiences=work_experiences_frontend,
            title="Your work experiences",
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="experience",
            form=form,
            experiences=work_experiences_frontend,
            title="Your work experiences",
        )


@onboarding_web_bp.route("/skills/", methods=["POST", "GET"])
@login_required
def skills():
    """Display the current user's skills.

    Returns:
        The full page or partial skills HTML for an HTMX request.
    """

    form = SkillForm()

    user_skill_data_list = db.session.scalars(
        db.select(UserSkill).where(UserSkill.user_id == current_user.user_id)
    ).all()

    skills = []

    for item in user_skill_data_list:
        skill_row = db.session.scalars(
            db.select(Skill).where(Skill.skill_id == item.skill_id)
        ).first()

        if skill_row:
            s = {
                "user_skill_id": item.user_skill_id,
                "skill_name": skill_row.skill_name,
                "current_id": item.skill_id,
            }
            skills.append(s)

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "onboarding/skills.html",
            form=form,
            skills=skills,
            title="Your Skills",
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="skills",
            form=form,
            skills=skills,
            title="Your Skills",
        )
