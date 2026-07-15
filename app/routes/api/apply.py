from datetime import date
from ollama import chat
from pydantic import BaseModel, Field
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
import uuid
from app.extensions import db
from playwright.sync_api import sync_playwright
from app.forms import JobLinkForm
from app.models import (
    UserSkill,
    Education,
    WorkExperience,
    Skill,
    UserPersonal,
    User,
    Document,
    JobEntry,
    Application,
)
from app.utilities.ai_service import ai_service
from app.ai.prompts.job_analyse import PROMPT as analyse_prompt
from app.ai.schemas.job_analyse import JSON_SCHEMA as analyse_schema
from app.ai.prompts.cv import PROMPT as cv_prompt
from app.ai.schemas.cv import JSON_SCHEMA as cv_schema
from app.ai.prompts.cover_letter import PROMPT as cover_letter_prompt
from app.ai.schemas.cover_letter import JSON_SCHEMA as conver_letter_schema


apply_api_bp = Blueprint("apply_api", __name__)


@apply_api_bp.route("/job_entry", methods=["POST", "GET"])
@login_required
def job_entry():

    form = JobLinkForm(request.form)

    stmt_skill = db.select(UserSkill).where(UserSkill.user_id == current_user.user_id)
    stmt_experience = db.select(WorkExperience).where(
        WorkExperience.user_id == current_user.user_id
    )
    stmt_education = db.select(Education).where(
        Education.user_id == current_user.user_id
    )
    stmt_user_personal = db.select(UserPersonal).where(
        UserPersonal.user_id == current_user.user_id
    )
    stmt_user = db.select(User).where(User.user_id == current_user.user_id)

    user_skills_data = db.session.scalars(stmt_skill).all()
    work_experiences_data = db.session.scalars(stmt_experience).all()
    education_data = db.session.scalars(stmt_education).all()
    user_personal = db.session.scalar(stmt_user_personal)
    user_data = db.session.scalar(stmt_user)

    # Check whether user has completed the onboarding
    # Because ai model needs that data to process the rest
    if (
        len(user_skills_data) == 0
        or len(work_experiences_data) == 0
        or len(education_data) == 0
        or not (user_personal)
    ):
        return {"warning": "You have to complete the onboarding"}

    if not (request.method == "POST" and form.validate()):
        return form.errors

    job = ""

    job_url = form.job_url.data
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)
        text = page.locator("body").inner_text()
        job = text
        browser.close()

    # Collect all users info
    user_info = {
        "full_name": user_data.full_name,
        "email": "dev@gmail.com",  # user_data.email
        "phone_number": user_personal.phone_number,
        "city": user_personal.city,
        "country": user_personal.country,
        "linkedin_url": user_personal.linkedin_url,
    }
    skills_list = []
    work_experiences_list = []
    education_list = []

    for user_skill in user_skills_data:
        skill_row = db.session.scalars(
            db.select(Skill).where(Skill.skill_id == user_skill.skill_id)
        ).first()

        skills_list.append(skill_row.skill_name)

    for work_experience in work_experiences_data:
        w = {
            "job_title": work_experience.job_title,
            "company": work_experience.company,
            "employment_type": work_experience.employment_type,
            "location": work_experience.location,
            "start_year": work_experience.start_year,
            "end_year": work_experience.end_year,
            "responsibilities": work_experience.responsibilities,
        }

        work_experiences_list.append(w)

    for education in education_data:
        e = {
            "qualification": education.qualification,
            "institution": education.institution,
            "location": education.location,
            "start_year": education.start_year,
            "end_year": education.end_year,
            "notes": education.notes,
        }
        education_list.append(e)

    job_entry_json = ai_service(
        analyse_prompt.format(
            job=job,
            job_url=form.job_url.data,
            skills_list=skills_list,
            work_experiences_list=work_experiences_list,
            education_list=education_list,
        ),
        analyse_schema,
    )

    if not job_entry_json["is_valid"]:
        return {"error": job_entry_json["invalid_reason"]}

    print("Complete the job analysing part")

    cv_json = ai_service(
        cv_prompt.format(
            job_entry=job_entry,
            user_info=user_info,
            skills_list=skills_list,
            work_experiences_list=work_experiences_list,
            education_list=education_list,
        ),
        cv_schema,
    )

    print("Generate the CV")

    cover_letter_json = ai_service(
        cover_letter_prompt.format(
            job_entry=job_entry,
            user_info=user_info,
            skills_list=skills_list,
            work_experiences_list=work_experiences_list,
            education_list=education_list,
        ),
        conver_letter_schema,
    )

    print("Generate the cover letter")

    job_entry_id = str(uuid.uuid4())

    new_job_entry = JobEntry(
        job_entry_id=job_entry_id,
        user_id=current_user.user_id,
        source_url=job_url,
        platform=job_entry_json["source_platform"],
        job_title=job_entry_json["job_title"],
        company_name=job_entry_json["company_name"],
        country_code=job_entry_json["country"],
        job_description=job_entry_json["job_description"],
        captured_at=date.today(),
        relevancy=int(job_entry_json["relevancy"]),
        matching_skills=job_entry_json["matching_skills"],
        tips=job_entry_json["tips"],
    )

    db.session.add(new_job_entry)

    print("new_job_entry is added to the db session")

    cv_id = str(uuid.uuid4())
    new_cv = Document(
        doc_id=cv_id,
        doc_type="cv",
        user_id=current_user.user_id,
        content=cv_json["html_code"],
        created_at=date.today(),
        country_code=cv_json["country"],
        role=cv_json["role"],
    )

    db.session.add(new_cv)

    print("new_cv is added to the db session")

    cover_letter_id = str(uuid.uuid4())
    new_cover_letter = Document(
        doc_id=cover_letter_id,
        doc_type="coverLetter",
        user_id=current_user.user_id,
        content=cover_letter_json["html_code"],
        created_at=date.today(),
        country_code=cover_letter_json["country"],
        role=cover_letter_json["role"],
    )

    db.session.add(new_cover_letter)

    print("new_cover_letter is added to the db session")

    application_id = str(uuid.uuid4())
    new_application = Application(
        application_id=application_id,
        user_id=current_user.user_id,
        job_entry_id=job_entry_id,
        cv_document_id=cv_id,
        cover_letter_document_id=cover_letter_id,
    )

    db.session.add(new_application)

    print("new_application is added to the db session")

    db.session.commit()

    print("commit to the db")

    return render_template(
        "user/apply/components/card.html",
        job_entry_id=job_entry_id,
        job_title=job_entry_json["job_title"],
        company_name=job_entry_json["company_name"],
        relevancy=job_entry_json["relevancy"],
    )


@apply_api_bp.route("/show/<id>/", methods=["GET"])
@login_required
def show(id):
    job_entry_stmt = db.select(JobEntry).where(JobEntry.job_entry_id == id)
    job_entry = db.session.scalars(job_entry_stmt).first()

    if job_entry is None:
        return {"error": "The job you’re looking for could not be found"}

    application_stmt = db.select(Application).where(Application.job_entry_id == id)
    application = db.session.scalars(application_stmt).first()

    cv_stmt = db.select(Document).where(
        Document.doc_id == application.cv_document_id, Document.doc_type == "cv"
    )
    cv = db.session.scalars(cv_stmt).first()

    cover_letter_stmt = db.select(Document).where(
        Document.doc_id == application.cover_letter_document_id,
        Document.doc_type == "coverLetter",
    )
    cover_letter = db.session.scalars(cover_letter_stmt).first()

    detail = {
        "job_entry_id": job_entry.job_entry_id,
        "source_url": job_entry.source_url,
        "job_title": job_entry.job_title,
        "company_name": job_entry.company_name,
        "country": job_entry.country_code,
        "captured_at": job_entry.captured_at.strftime(
            "%Y-%m-%d"
        ),  # get only yyyy-mm-dd
        "relevancy": job_entry.relevancy,
        "matching_skills": job_entry.matching_skills,
        "tips": job_entry.tips,
        "job_description": job_entry.job_description,
        "cv": cv.content,
        "cv_id": cv.doc_id,
        "cover_letter": cover_letter.content,
        "cover_letter_id": cover_letter.doc_id,
    }

    # Prevent users from accessing the route by typing the URL directly.
    if request.headers.get("HX-Request") == "true":
        return render_template("user/apply/components/detail.html", detail=detail)
    else:
        abort(403)
