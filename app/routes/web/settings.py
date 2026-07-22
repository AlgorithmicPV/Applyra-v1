from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_login import current_user, login_required, logout_user

from app.extensions import db
from app.forms import SettingsCodeRequestForm, SettingsTotpForm
from app.models import Education, Skill, UserSkill, WorkExperience

settings_web_bp = Blueprint("settings_web", __name__)


@settings_web_bp.before_app_request
def remove_settings_verification():
    # Keep verification while the user is using settings.
    if request.blueprint == "settings_web":
        return

    if request.blueprint == "settings_api":
        return

    # Loading CSS, images, or JavaScript is not changing the page.
    if request.endpoint == "static" or request.endpoint is None:
        return

    session.pop("settings-verified-user", None)


@settings_web_bp.route("/settings/")
@login_required
def settings():
    # Opening settings again always starts with PIN verification.
    session.pop("settings-verified-user", None)

    code_form = SettingsCodeRequestForm()
    pin_form = SettingsTotpForm()

    educations = db.session.scalars(
        db.select(Education).where(Education.user_id == current_user.user_id)
    ).all()

    experiences = db.session.scalars(
        db.select(WorkExperience).where(WorkExperience.user_id == current_user.user_id)
    ).all()

    user_skills = db.session.scalars(
        db.select(UserSkill).where(UserSkill.user_id == current_user.user_id)
    ).all()

    skills = []
    for user_skill in user_skills:
        skill = db.session.get(Skill, user_skill.skill_id)
        if skill:
            skills.append(skill.skill_name)

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "user/settings/settings-static.html",
            code_form=code_form,
            pin_form=pin_form,
            educations=educations,
            experiences=experiences,
            skills=skills,
        )

    return render_template(
        "user/base.html",
        title="Settings",
        page="settings",
        code_form=code_form,
        pin_form=pin_form,
        educations=educations,
        experiences=experiences,
        skills=skills,
    )


@settings_web_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_web.login"))
