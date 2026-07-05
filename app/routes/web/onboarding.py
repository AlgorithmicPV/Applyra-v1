from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required
from app.forms import EducationForm, SkillForm, ExperienceForm
from app.models import Education
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
    if request.headers.get("HX-Request") == "true":
        return render_template("onboarding/skills.html")
    else:
        return render_template("onboarding/base.html", page="skills")
