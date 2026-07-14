from flask import Blueprint, request, render_template, session, abort
from flask_login import current_user, login_required
from app.forms import JobLinkForm
from app.models import (
    Document,
    UserPersonal,
    UserSkill,
    Education,
    WorkExperience,
    JobEntry,
    Application,
)
from app.extensions import db


apply_web_bp = Blueprint("apply_web", __name__)


@apply_web_bp.route("/apply/", methods=["POST", "GET"])
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
    stmt_user_profile = (
        db.select(UserPersonal)
        .where(UserPersonal.user_id == current_user.user_id)
        .exists()
    )
    message = ""

    # Execute using session.scalar() to get a boolean
    if not (
        db.session.scalar(db.select(stmt_skill))
        and db.session.scalar(db.select(stmt_experience))
        and db.session.scalar(db.select(stmt_education))
        and db.session.scalar(db.select(stmt_user_profile))
    ):
        message = "You need to complete the onboarding before proceeding. Click here to Continue"

    stmt_job_entry = db.select(JobEntry).where(JobEntry.user_id == current_user.user_id)
    job_entries = db.session.scalars(stmt_job_entry).all()

    job_entries_frontend = []

    # Remove user_id, and unwanted data before send it to the frontend
    # remove user_id, to keep the user protected
    for j in job_entries:
        job_entry = {
            "job_entry_id": j.job_entry_id,
            "job_title": j.job_title,
            "company_name": j.company_name,
            "relevancy": j.relevancy,
        }
        job_entries_frontend.append(job_entry)

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "user/apply/base.html",
            form=form,
            message=message,
            job_entries=job_entries_frontend,
        )
    else:
        return render_template(
            "user/base.html",
            page="apply",
            form=form,
            message=message,
            job_entries=job_entries_frontend,
        )


@apply_web_bp.route("/apply/<id>/", methods=["GET"])
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
