from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required


onboarding_web_bp = Blueprint("onboarding_web", __name__)


@onboarding_web_bp.route("/", methods=["POST", "GET"])
@login_required
def home():
    return render_template("onboarding/base.html", page="home")


@onboarding_web_bp.route("/education/", methods=["POST", "GET"])
@login_required
def education():
    if request.headers.get("HX-Request") == "true":
        return render_template("onboarding/education.html")
    else:
        return render_template("onboarding/base.html", page="education")


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
