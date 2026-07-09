from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required
from app.forms import EducationForm, SkillForm, ExperienceForm
from app.models import Education, Skill, UserSkill
from app.extensions import db

onboarding_web_bp = Blueprint("onboarding_web", __name__)


@onboarding_web_bp.route("/", methods=["POST", "GET"])
@login_required
def home():
    return render_template("onboarding/base.html", page="home")


@onboarding_web_bp.route("/education/", methods=["POST", "GET"])
@login_required
def education():
    form = EducationForm()

    qualifications = db.session.scalars(
        db.select(Education).where(Education.user_profile_id == current_user.user_id)
    ).all()

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "onboarding/education.html", form=form, qualifications=qualifications
        )
    else:
        return render_template(
            "onboarding/base.html",
            page="education",
            form=form,
            qualifications=qualifications,
        )


@onboarding_web_bp.route("/experience/", methods=["POST", "GET"])
@login_required
def experience():
    if request.headers.get("HX-Request") == "true":
        return render_template("onboarding/experience.html")
    else:
        return render_template("onboarding/base.html", page="experience")


@onboarding_web_bp.route("/skills/", methods=["POST", "GET"])
@login_required
def skills():
    form = SkillForm()

    user_skill_data_list = db.session.scalars(
        db.select(UserSkill).where(UserSkill.user_profile_id == current_user.user_id)
    ).all()

    skills = []

    for item in user_skill_data_list:
        skill_row = db.session.scalars(
            db.select(Skill).where(Skill.skill_id == item.skill_id)
        ).first()

        print(item.skill_id)

        if skill_row:
            s = {
                "user_profile_id": item.user_skill_id,
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
