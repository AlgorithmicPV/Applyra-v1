# WARNING: Error handling pending: User can change values, like ids, and options
# WARNING: Put a limit for everything, otherwise, users will put 10k skills, etc
import uuid
from datetime import date
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.forms import EducationForm, SkillForm, ExperienceForm
from app.models import Education, Skill, UserSkill, WorkExperience
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Null, delete
from sqlalchemy.inspection import inspect

onboarding_api_bp = Blueprint("onboarding_api", __name__)


@onboarding_api_bp.route("/education/collect", methods=["POST", "GET"])
@login_required
def education_collect():
    form = EducationForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    education_id = str(uuid.uuid4())
    certificate = form.certificate.data
    institution = form.institution.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data
    update_form = EducationForm()

    new_qualification = Education(
        education_id=education_id,
        user_id=current_user.user_id,
        qualification=certificate,
        institution=institution,
        location=location,
        start_year=date(start_year, 1, 1),  # Convert the integer to a date object
        end_year=date(end_year, 12, 31),  # Convert the integer to a date object
        notes=notes,
    )

    try:
        db.session.add(new_qualification)
        db.session.commit()
    except IntegrityError as e:
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


@onboarding_api_bp.route("/education/update/<id>", methods=["POST", "GET"])
@login_required
def education_update(id):
    form = EducationForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    stmt = db.select(Education).where(Education.education_id == id)
    education = db.session.execute(stmt).scalar_one()

    certificate = form.certificate.data
    institution = form.institution.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data
    update_form = EducationForm()

    try:
        education.qualification = certificate
        education.institution = institution
        education.location = location
        education.start_year = date(start_year, 1, 1)
        education.end_year = date(end_year, 12, 31)
        education.notes = notes
        db.session.commit()
    except IntegrityError as e:
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


@onboarding_api_bp.route("/education/delete/<id>", methods=["DELETE"])
@login_required
def education_delete(id):
    stmt = delete(Education).where(Education.education_id == id)
    db.session.execute(stmt)
    db.session.commit()

    return "", 200


@onboarding_api_bp.route("/skill/search/")
@login_required
def search_skills():
    query_item = request.args.get("q")
    stmt = db.select(Skill).where(Skill.skill_name.ilike(f"%{query_item}%"))

    searched_skills = db.session.scalars(stmt).all()

    # Convert the SQL object to a python dict
    searched_dict = {}

    for s in searched_skills:
        searched_dict[s.skill_id] = s.skill_name

    return jsonify([{"id": k, "name": v} for k, v in searched_dict.items()])


@onboarding_api_bp.route("/skill/collect", methods=["POST", "GET"])
@login_required
def skill_collect():
    form = SkillForm(request.form)

    if not (request.method == "POST" and form.validate()):
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
    except IntegrityError as e:
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


@onboarding_api_bp.route("/skill/update/<id>", methods=["GET", "POST"])
@login_required
def skill_update(id):
    # id is user_skill_id (primary key of user_skill table)
    form = SkillForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    stmt = db.select(UserSkill).where(UserSkill.user_skill_id == id)
    user_skill = db.session.execute(stmt).scalar_one()

    update_skill_id = form.skill_name.data

    try:
        user_skill.skill_id = update_skill_id
        db.session.commit()
    except IntegrityError as e:
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


@onboarding_api_bp.route("/skill/delete/<id>", methods=["DELETE"])
@login_required
def skill_delete(id):
    stmt = delete(UserSkill).where(UserSkill.user_skill_id == id)
    db.session.execute(stmt)
    db.session.commit()

    return "", 200


@onboarding_api_bp.route("/work_experience/collect", methods=["POST", "GET"])
@login_required
def work_experience_collect():
    form = ExperienceForm(request.form)

    if not (request.method == "POST" and form.validate):
        return form.errors

    experience_id = str(uuid.uuid4())
    company = form.company.data
    job_title = form.job_title.data
    employment_type = form.employment_type.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    responsibilities = form.responsibilities.data
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

    try:
        db.session.add(new_work_experience)
        db.session.commit()
    except IntegrityError as e:
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


@onboarding_api_bp.route("/work_experience/update/<id>", methods=["POST", "GET"])
@login_required
def work_experience_update(id):
    form = ExperienceForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    stmt = db.select(WorkExperience).where(WorkExperience.experience_id == id)
    experience = db.session.execute(stmt).scalar_one()

    company = form.company.data
    job_title = form.job_title.data
    employment_type = form.employment_type.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    responsibilities = form.responsibilities.data
    update_form = ExperienceForm()

    # Currently, I have made end_year complusory,
    # in future development, I will remove
    # therefore, I am keeping this code

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
    except IntegrityError as e:
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


@onboarding_api_bp.route("/work_experience/delete/<id>", methods=["DELETE"])
@login_required
def work_experience_delete(id):
    stmt = delete(WorkExperience).where(WorkExperience.experience_id == id)
    db.session.execute(stmt)
    db.session.commit()

    return "", 200
