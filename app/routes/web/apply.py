from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required
from app.forms import JobLinkForm
from app.models import UserSkill, Education, WorkExperience
from app.extensions import db

apply_web_bp = Blueprint("apply_web", __name__)


@apply_web_bp.route("/apply", methods=["POST", "GET"])
@login_required
def apply():
    form = JobLinkForm()

    stmt_skill = (
        db.select(UserSkill).where(UserSkill.user_id == current_user.user_id).exists()
    )
    stmt_experience = (
        db.select(WorkExperience)
        .where(WorkExperience.user_id == current_user.user_id)
        .exists()
    )
    stmt_education = (
        db.select(Education).where(Education.user_id == current_user.user_id).exists()
    )

    message = ""

    # Execute using session.scalar() to get a boolean
    if not (
        db.session.scalar(db.select(stmt_skill))
        and db.session.scalar(db.select(stmt_experience))
        and db.session.scalar(db.select(stmt_education))
    ):
        message = "You need to complete the onboarding before proceeding. Click here to Continue"

    if request.headers.get("HX-Request") == "true":
        return render_template("user/apply/base.html", form=form, message=message)
    else:
        return render_template(
            "user/base.html", page="apply", form=form, message=message
        )
