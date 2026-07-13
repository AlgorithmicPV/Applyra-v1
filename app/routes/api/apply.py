from ollama import chat
from pydantic import BaseModel, Field
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
import uuid
from app.extensions import db
from playwright.sync_api import sync_playwright
from app.forms import JobLinkForm
from app.models import UserSkill, Education, WorkExperience, Skill
from app.utilities.ai_service import ai_service
from app.ai.prompts.job_analyse import PROMPT as analyse_prompt
from app.ai.schemas.job_analyse import JSON_SCHEMA as analyse_schema


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

    user_skills_data = db.session.scalars(stmt_skill).all()
    work_experiences_data = db.session.scalars(stmt_experience).all()
    education_data = db.session.scalars(stmt_education).all()

    # Check whether user has completed the onboarding
    # Because ai model needs that data to process the rest
    if (
        len(user_skills_data) == 0
        or len(work_experiences_data) == 0
        or len(education_data) == 0
    ):
        return {"warning": "You have to complete the onboarding"}

    if not (request.method == "POST" and form.validate()):
        return form.errors

    job_entry_id = str(uuid.uuid4())
    job_url = form.job_url.data

    job = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)
        text = page.locator("body").inner_text()
        job = text
        browser.close()

    # Collect all users info
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

    response = ai_service(
        analyse_prompt.format(
            job=job,
            skills_list=skills_list,
            work_experiences_list=work_experiences_list,
            education_list=education_list,
        ),
        analyse_schema,
    )

    if not response["is_valid"]:
        return {"error": response["invalid_reason"]}

    print(response)
    # TODO: Save to the database (check the validity), and think how to make the cv and the resume letter

    # save the markdown or the html content, and via js mostly convert that to a downladble pdf
    return "hi"
