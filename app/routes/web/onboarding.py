from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required
from app.forms import EducationForm, SkillForm, ExperienceForm
from app.models import Education, Skill, UserSkill, WorkExperience
from app.extensions import db

onboarding_web_bp = Blueprint("onboarding_web", __name__)


# NOTE: remeber to remove the user_id from here
@onboarding_web_bp.route("/", methods=["POST", "GET"])
@login_required
def home():
    return render_template("onboarding/base.html", page="home")


@onboarding_web_bp.route("/education/", methods=["POST", "GET"])
@login_required
def education():
    form = EducationForm()

    qualifications = db.session.scalars(
        db.select(Education).where(Education.user_id == current_user.user_id)
    ).all()

    # Remove user_id before send SQLAlchemy model to frontend
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
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="education",
            form=form,
            qualifications=qualifications_frontend,
        )


@onboarding_web_bp.route("/experience/", methods=["POST", "GET"])
@login_required
def experience():
    form = ExperienceForm()

    work_experiences = db.session.scalars(
        db.select(WorkExperience).where(WorkExperience.user_id == current_user.user_id)
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
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="experience",
            form=form,
            experiences=work_experiences_frontend,
        )


@onboarding_web_bp.route("/skills/", methods=["POST", "GET"])
@login_required
def skills():
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
        return render_template("onboarding/skills.html", form=form, skills=skills)
    else:
        return render_template(
            "onboarding/base.html", page="skills", form=form, skills=skills
        )
