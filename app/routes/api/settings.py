import base64
import uuid
from datetime import date

from flask import (
    Blueprint,
    jsonify,
    make_response,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db, password_hasher
from app.forms import (
    EducationForm,
    ExperienceForm,
    SettingsCodeRequestForm,
    SettingsDeleteForm,
    SettingsPasswordForm,
    SettingsProfileForm,
    SettingsTotpForm,
    SkillForm,
)
from app.models import (
    Application,
    Document,
    Education,
    JobEntry,
    Skill,
    User,
    UserPersonal,
    UserSkill,
    WorkExperience,
)
from app.utilities.validations import email_confirm

settings_api_bp = Blueprint("settings_api", __name__)


@settings_api_bp.post("/request-code/")
@login_required
def request_code():
    form = SettingsCodeRequestForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    result = email_confirm(current_user.email, interval=600)
    if result:
        return result

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

    return render_template(
        "user/settings/settings-static.html",
        code_form=SettingsCodeRequestForm(),
        pin_form=SettingsTotpForm(),
        code_sent=True,
        educations=educations,
        experiences=experiences,
        skills=skills,
    )


@settings_api_bp.post("/verify-code/")
@login_required
def verify_code():
    form = SettingsTotpForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    session["settings-verified-user"] = current_user.user_id

    profile_form = SettingsProfileForm()
    password_form = SettingsPasswordForm()
    skill_form = SkillForm()
    education_form = EducationForm()
    experience_form = ExperienceForm()
    delete_form = SettingsDeleteForm()

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
            skills.append(
                {
                    "user_skill_id": user_skill.user_skill_id,
                    "skill_id": skill.skill_id,
                    "skill_name": skill.skill_name,
                }
            )

    return render_template(
        "user/settings/settings-editable/settings-edit.html",
        profile_form=profile_form,
        password_form=password_form,
        skill_form=skill_form,
        education_form=education_form,
        experience_form=experience_form,
        delete_form=delete_form,
        educations=educations,
        experiences=experiences,
        skills=skills,
    )


@settings_api_bp.get("/skill/search/")
@login_required
def search_skills():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    skills = db.session.scalars(
        db.select(Skill).where(Skill.skill_name.ilike(f"%{query}%")).limit(20)
    ).all()

    result = []
    for skill in skills:
        result.append({"id": skill.skill_id, "name": skill.skill_name})
    return jsonify(result)


@settings_api_bp.post("/profile/update/")
@login_required
def profile_update():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = SettingsProfileForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    image = form.profile_image.data
    if image:
        image_data = image.read(5 * 1024 * 1024 + 1)
        if len(image_data) > 5 * 1024 * 1024:
            return {"error": "Profile picture cannot be larger than 5 MB"}

        encoded_image = base64.b64encode(image_data).decode("utf-8")
        image_type = image.mimetype or "image/png"
        current_user.profile_image = "data:" + image_type + ";base64," + encoded_image

    current_user.full_name = form.full_name.data
    current_user.email = form.email.data

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That email address is already in use"}

    return {"success": "Personal details updated. Reload the Page"}


@settings_api_bp.post("/password/update/")
@login_required
def password_update():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    if current_user.auth_provider != "manual" or not current_user.password_hash:
        return {"error": "Password changes are not available for this account"}

    form = SettingsPasswordForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    current_user.password_hash = password_hasher.hash(form.new_password.data)
    db.session.commit()
    return {"success": "Password updated"}


@settings_api_bp.post("/skill/add/")
@login_required
def skill_add():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = SkillForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    skill = db.session.get(Skill, form.skill_name.data)
    if not skill:
        return {"error": "Please select a valid skill"}

    user_skill = UserSkill(
        user_skill_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        skill_id=skill.skill_id,
    )

    try:
        db.session.add(user_skill)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That skill has already been added"}

    return render_template(
        "user/settings/components/skill.html",
        user_skill=user_skill,
        skill=skill,
    )


@settings_api_bp.delete("/skill/delete/<user_skill_id>/")
@login_required
def skill_delete(user_skill_id):
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    user_skill = db.session.scalar(
        db.select(UserSkill).where(
            UserSkill.user_skill_id == user_skill_id,
            UserSkill.user_id == current_user.user_id,
        )
    )
    if not user_skill:
        return {"error": "Skill was not found"}

    db.session.delete(user_skill)
    db.session.commit()
    return "", 200


@settings_api_bp.post("/education/add/")
@login_required
def education_add():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = EducationForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}
    if form.start_year.data > form.end_year.data:
        return {"error": "Start year cannot be after end year"}

    education = Education(
        education_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        qualification=form.certificate.data,
        institution=form.institution.data,
        location=form.location.data,
        start_year=date(form.start_year.data, 1, 1),
        end_year=date(form.end_year.data, 12, 31),
        notes=form.description.data,
    )

    try:
        db.session.add(education)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That education record already exists"}

    return render_template(
        "user/settings/components/education.html",
        education=education,
        form=EducationForm(),
    )


@settings_api_bp.post("/education/update/<education_id>/")
@login_required
def education_update(education_id):
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = EducationForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}
    if form.start_year.data > form.end_year.data:
        return {"error": "Start year cannot be after end year"}

    education = db.session.scalar(
        db.select(Education).where(
            Education.education_id == education_id,
            Education.user_id == current_user.user_id,
        )
    )
    if not education:
        return {"error": "Education record was not found"}

    education.qualification = form.certificate.data
    education.institution = form.institution.data
    education.location = form.location.data
    education.start_year = date(form.start_year.data, 1, 1)
    education.end_year = date(form.end_year.data, 12, 31)
    education.notes = form.description.data

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That education record already exists"}

    return render_template(
        "user/settings/components/education.html",
        education=education,
        form=EducationForm(),
    )


@settings_api_bp.delete("/education/delete/<education_id>/")
@login_required
def education_delete(education_id):
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    education = db.session.scalar(
        db.select(Education).where(
            Education.education_id == education_id,
            Education.user_id == current_user.user_id,
        )
    )
    if not education:
        return {"error": "Education record was not found"}

    db.session.delete(education)
    db.session.commit()
    return "", 200


@settings_api_bp.post("/experience/add/")
@login_required
def experience_add():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = ExperienceForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}
    if form.start_year.data > form.end_year.data:
        return {"error": "Start year cannot be after end year"}

    experience = WorkExperience(
        experience_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        job_title=form.job_title.data,
        company=form.company.data,
        employment_type=form.employment_type.data,
        location=form.location.data,
        start_year=date(form.start_year.data, 1, 1),
        end_year=date(form.end_year.data, 12, 31),
        responsibilities=form.responsibilities.data,
    )

    try:
        db.session.add(experience)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That work experience already exists"}

    return render_template(
        "user/settings/components/experience.html",
        experience=experience,
        form=ExperienceForm(),
    )


@settings_api_bp.post("/experience/update/<experience_id>/")
@login_required
def experience_update(experience_id):
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = ExperienceForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}
    if form.start_year.data > form.end_year.data:
        return {"error": "Start year cannot be after end year"}

    experience = db.session.scalar(
        db.select(WorkExperience).where(
            WorkExperience.experience_id == experience_id,
            WorkExperience.user_id == current_user.user_id,
        )
    )
    if not experience:
        return {"error": "Work experience was not found"}

    experience.job_title = form.job_title.data
    experience.company = form.company.data
    experience.employment_type = form.employment_type.data
    experience.location = form.location.data
    experience.start_year = date(form.start_year.data, 1, 1)
    experience.end_year = date(form.end_year.data, 12, 31)
    experience.responsibilities = form.responsibilities.data

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That work experience already exists"}

    return render_template(
        "user/settings/components/experience.html",
        experience=experience,
        form=ExperienceForm(),
    )


@settings_api_bp.delete("/experience/delete/<experience_id>/")
@login_required
def experience_delete(experience_id):
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    experience = db.session.scalar(
        db.select(WorkExperience).where(
            WorkExperience.experience_id == experience_id,
            WorkExperience.user_id == current_user.user_id,
        )
    )
    if not experience:
        return {"error": "Work experience was not found"}

    db.session.delete(experience)
    db.session.commit()
    return "", 200


@settings_api_bp.post("/account/delete/")
@login_required
def account_delete():
    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = SettingsDeleteForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    user_id = current_user.user_id

    # Delete child records first because they belong to the user account.
    db.session.query(Application).filter(Application.user_id == user_id).delete()
    db.session.query(Document).filter(Document.user_id == user_id).delete()
    db.session.query(JobEntry).filter(JobEntry.user_id == user_id).delete()
    db.session.query(Education).filter(Education.user_id == user_id).delete()
    db.session.query(UserSkill).filter(UserSkill.user_id == user_id).delete()
    db.session.query(WorkExperience).filter(WorkExperience.user_id == user_id).delete()
    db.session.query(UserPersonal).filter(UserPersonal.user_id == user_id).delete()
    db.session.query(User).filter(User.user_id == user_id).delete()
    db.session.commit()

    logout_user()
    session.clear()

    response = make_response({"success": "Your account has been deleted"})
    response.headers["HX-Redirect"] = url_for("auth_web.login")
    return response
