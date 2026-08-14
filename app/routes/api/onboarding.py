"""This module handles the backend routes for the onboarding pages."""

import uuid
from datetime import date

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import Null
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms import EducationForm, ExperienceForm, SkillForm, UserInfoForm
from app.models import (
    Education,
    Skill,
    UserPersonal,
    UserSkill,
    WorkExperience,
)

onboarding_api_bp = Blueprint("onboarding_api", __name__)


@onboarding_api_bp.post("/user-info/collect")
@login_required
def user_info_collect():
    """Collect and save the user's personal information.

    Returns:
        A redirect when successful, or a dictionary containing errors.
    """

    form = UserInfoForm(request.form)

    stmt = (
        db.select(UserPersonal)
        .where(UserPersonal.user_id == current_user.user_id)
        .exists()
    )

    data_exists = db.session.scalar(db.select(stmt))

    if data_exists:
        return {
            "error": (
                "You have submited your personal info. Use setting page to do "
                "any changes"
            )
        }

    if not form.validate():
        return form.errors

    user_personal_id = str(uuid.uuid4())
    phone_number = form.phone.data
    city = form.city.data
    country = form.country.data
    linkedin_url = form.linkedin_url.data

    user_personal = UserPersonal(
        user_personal_id=user_personal_id,
        user_id=current_user.user_id,
        phone_number=phone_number,
        city=city.strip().lower(),  # Remove spaces and convert to lowercase.
        country=country,
        linkedin_url=linkedin_url.strip(),  # Remove spaces and convert to lowercase.
    )

    db.session.add(user_personal)
    db.session.commit()

    return redirect(url_for("onboarding_web.education"))


@onboarding_api_bp.post("/education/collect")
@login_required
def education_collect():
    """Collect and save a new education record.

    Returns:
        The new education HTML, or a dictionary containing errors.
    """

    form = EducationForm(request.form)

    if not form.validate():
        return form.errors

    education_id = str(uuid.uuid4())
    certificate = form.certificate.data.strip()
    institution = form.institution.data.strip()
    location = form.location.data.strip()
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data.strip()
    update_form = EducationForm()

    # Convert the integer years to date objects.
    new_qualification = Education(
        education_id=education_id,
        user_id=current_user.user_id,
        qualification=certificate,
        institution=institution,
        location=location,
        start_year=date(start_year, 1, 1),
        end_year=date(end_year, 12, 31),
        notes=notes,
    )

    try:
        db.session.add(new_qualification)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    # It is required to have the same variable's names as the web/onboarding.py
    # Because, I am using same html page
    return render_template(
        "onboarding/components/education.html",
        education_id=education_id,
        certificate=certificate,
        institution=institution,
        location=location,
        start_year=start_year,
        end_year=end_year,
        notes=notes,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.post("/education/update/<id>")
@login_required
def education_update(id):
    """Update an education record if it belongs to the current user.

    Args:
        id: The ID of the education record.

    Returns:
        The updated education HTML, or a dictionary containing errors.
    """

    form = EducationForm(request.form)

    if not form.validate():
        return form.errors

    stmt = db.select(Education).where(
        Education.education_id == id,
        Education.user_id == current_user.user_id,
    )
    education = db.session.execute(stmt).scalar_one_or_none()

    if education is None:
        return {"error": "The education record does not exist"}

    certificate = form.certificate.data.strip()
    institution = form.institution.data.strip()
    location = form.location.data.strip()
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data.strip()
    update_form = EducationForm()

    try:
        education.qualification = certificate
        education.institution = institution
        education.location = location
        education.start_year = date(start_year, 1, 1)
        education.end_year = date(end_year, 12, 31)
        education.notes = notes
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    return render_template(
        "onboarding/components/education.html",
        education_id=id,
        certificate=certificate,
        institution=institution,
        location=location,
        start_year=start_year,
        end_year=end_year,
        notes=notes,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.delete("/education/delete/<id>")
@login_required
def education_delete(id):
    """Delete an education record if it belongs to the current user.

    Args:
        id: The ID of the education record.

    Returns:
        An empty response when successful, or an error if it does not exist.
    """

    stmt = db.select(Education).where(
        Education.education_id == id,
        Education.user_id == current_user.user_id,
    )
    education = db.session.execute(stmt).scalar_one_or_none()

    if education is None:
        return {"error": "The education record does not exist"}

    db.session.delete(education)
    db.session.commit()

    return "", 200


@onboarding_api_bp.get("/skill/search/")
@login_required
def search_skills():
    """Search for skills using the given search text.

    Returns:
        A JSON list containing the matching skills.
    """

    query_item = request.args.get("q")
    stmt = db.select(Skill).where(Skill.skill_name.ilike(f"%{query_item}%"))

    searched_skills = db.session.scalars(stmt).all()

    # Convert the SQL object to a python dict
    searched_dict = {}

    for s in searched_skills:
        searched_dict[s.skill_id] = s.skill_name

    return jsonify([{"id": k, "name": v} for k, v in searched_dict.items()])


@onboarding_api_bp.post("/skill/collect")
@login_required
def skill_collect():
    """Collect and save a new skill for the current user.

    Returns:
        The new skill HTML, or a dictionary containing errors.
    """

    form = SkillForm(request.form)

    if not form.validate():
        return form.errors

    user_skill_id = str(uuid.uuid4())
    skill_id = form.skill_name.data

    new_skill = UserSkill(
        user_skill_id=user_skill_id,
        user_id=current_user.user_id,
        skill_id=skill_id,
    )

    try:
        db.session.add(new_skill)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    stmt = db.select(Skill).where(Skill.skill_id == skill_id)
    skill_name = db.session.execute(stmt).scalar_one().skill_name
    update_form = SkillForm()

    return render_template(
        "onboarding/components/skill.html",
        user_skill_id=user_skill_id,
        skill_name=skill_name,
        current_id=skill_id,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.post("/skill/update/<id>")
@login_required
def skill_update(id):
    """Update a user skill if it belongs to the current user.

    Args:
        id: The ID of the user's skill record.

    Returns:
        The updated skill HTML, or a dictionary containing errors.
    """

    # id is user_skill_id (primary key of user_skill table)
    form = SkillForm(request.form)

    if not form.validate():
        return form.errors

    stmt = db.select(UserSkill).where(
        UserSkill.user_skill_id == id,
        UserSkill.user_id == current_user.user_id,
    )
    user_skill = db.session.execute(stmt).scalar_one_or_none()

    if user_skill is None:
        return {"error": "The user skill does not exist"}

    update_skill_id = form.skill_name.data

    try:
        user_skill.skill_id = update_skill_id
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    stmt = db.select(Skill).where(Skill.skill_id == update_skill_id)
    skill_name = db.session.execute(stmt).scalar_one().skill_name
    update_form = SkillForm()

    return render_template(
        "onboarding/components/skill.html",
        user_skill_id=id,
        skill_name=skill_name,
        current_id=id,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.delete("/skill/delete/<id>")
@login_required
def skill_delete(id):
    """Delete a user skill if it belongs to the current user.

    Args:
        id: The ID of the user's skill record.

    Returns:
        An empty response when successful, or an error if it does not exist.
    """

    stmt = db.select(UserSkill).where(
        UserSkill.user_skill_id == id,
        UserSkill.user_id == current_user.user_id,
    )
    user_skill = db.session.execute(stmt).scalar_one_or_none()

    if user_skill is None:
        return {"error": "The user skill does not exist"}

    db.session.delete(user_skill)
    db.session.commit()

    return "", 200


@onboarding_api_bp.post("/work_experience/collect")
@login_required
def work_experience_collect():
    """Collect and save a new work experience record.

    Returns:
        The new work experience HTML, or a dictionary containing errors.
    """

    form = ExperienceForm(request.form)

    if not form.validate():
        return form.errors

    experience_id = str(uuid.uuid4())
    company = form.company.data.strip()
    job_title = form.job_title.data.strip()
    employment_type = form.employment_type.data
    location = form.location.data.strip()
    start_year = form.start_year.data
    end_year = form.end_year.data
    responsibilities = form.responsibilities.data.strip()
    update_form = ExperienceForm()

    # Currently, I have made end_year complusory,
    # in future development, I will remove
    # therefore, I am keeping this code

    # Users can use the end_year as the present year

    date_version_end_year = Null

    if end_year:
        date_version_end_year = date(end_year, 1, 1)

    new_work_experience = WorkExperience(
        experience_id=experience_id,
        user_id=current_user.user_id,
        job_title=job_title,
        company=company,
        employment_type=employment_type,
        location=location,
        start_year=date(start_year, 1, 1),
        end_year=date_version_end_year,
        responsibilities=responsibilities,
    )
    print(new_work_experience)
    try:
        db.session.add(new_work_experience)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    return render_template(
        "onboarding/components/experience.html",
        experience_id=experience_id,
        job_title=job_title,
        company=company,
        employment_type=employment_type,
        start_year=start_year,
        end_year=end_year,
        responsibilities=responsibilities,
        form=update_form,
        location=location,
        api=True,
    )


@onboarding_api_bp.post("/work_experience/update/<id>")
@login_required
def work_experience_update(id):
    """Update work experience if it belongs to the current user.

    Args:
        id: The ID of the work experience record.

    Returns:
        The updated work experience HTML, or a dictionary containing errors.
    """

    form = ExperienceForm(request.form)

    if not form.validate():
        return form.errors

    stmt = db.select(WorkExperience).where(
        WorkExperience.experience_id == id,
        WorkExperience.user_id == current_user.user_id,
    )
    experience = db.session.execute(stmt).scalar_one_or_none()

    if experience is None:
        return {"error": "The work experience does not exist"}

    company = form.company.data.strip()
    job_title = form.job_title.data.strip()
    employment_type = form.employment_type.data
    location = form.location.data.strip()
    start_year = form.start_year.data
    end_year = form.end_year.data
    responsibilities = form.responsibilities.data.strip()
    update_form = ExperienceForm()

    # Currently, I have made end_year complusory,
    # in future development, I will remove
    # therefore, I am keeping this code for the future

    # Users can use the end_year as the present year
    date_version_end_year = Null

    if end_year:
        date_version_end_year = date(end_year, 1, 1)

    try:
        experience.job_title = job_title
        experience.company = company
        experience.employment_type = employment_type
        experience.location = location
        experience.start_year = date(start_year, 1, 1)
        experience.end_year = date_version_end_year
        experience.responsibilities = responsibilities
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    return render_template(
        "onboarding/components/experience.html",
        experience_id=id,
        job_title=job_title,
        company=company,
        employment_type=employment_type,
        start_year=start_year,
        end_year=end_year,
        responsibilities=responsibilities,
        form=update_form,
        location=location,
        api=True,
    )


@onboarding_api_bp.delete("/work_experience/delete/<id>")
@login_required
def work_experience_delete(id):
    """Delete work experience if it belongs to the current user.

    Args:
        id: The ID of the work experience record.

    Returns:
        An empty response when successful, or an error if it does not exist.
    """

    stmt = db.select(WorkExperience).where(
        WorkExperience.experience_id == id,
        WorkExperience.user_id == current_user.user_id,
    )
    experience = db.session.execute(stmt).scalar_one_or_none()

    if experience is None:
        return {"error": "The work experience does not exist"}

    db.session.delete(experience)
    db.session.commit()

    return "", 200
