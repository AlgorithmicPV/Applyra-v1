"""This module handles the frontend route for the apply page."""

from flask import Blueprint, render_template, request, session
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import JobForm, JobLinkForm
from app.models import (
    Education,
    JobEntry,
    UserPersonal,
    UserSkill,
    WorkExperience,
)

apply_web_bp = Blueprint("apply_web", __name__)


@apply_web_bp.route("/apply/", methods=["POST", "GET"])
@login_required
def apply():
    """Display the apply page with the current user's job entries.

    Returns:
        The full apply page or partial apply HTML for an HTMX request.
    """

    form = JobLinkForm()
    form = JobForm()

    stmt_skill = (
        db.select(UserSkill)
        .where(UserSkill.user_id == current_user.user_id)
        .exists()
    )
    stmt_experience = (
        db.select(WorkExperience)
        .where(WorkExperience.user_id == current_user.user_id)
        .exists()
    )
    stmt_education = (
        db.select(Education)
        .where(Education.user_id == current_user.user_id)
        .exists()
    )
    stmt_user_profile = (
        db.select(UserPersonal)
        .where(UserPersonal.user_id == current_user.user_id)
        .exists()
    )
    message = ""

    # Use session.scalar() to get a Boolean value.
    if not (
        db.session.scalar(db.select(stmt_skill))
        and db.session.scalar(db.select(stmt_experience))
        and db.session.scalar(db.select(stmt_education))
        and db.session.scalar(db.select(stmt_user_profile))
    ):
        message = (
            "You need to complete the onboarding before proceeding. "
            "Click here to Continue"
        )

    stmt_job_entry = db.select(JobEntry).where(
        JobEntry.user_id == current_user.user_id
    )
    job_entries = db.session.scalars(stmt_job_entry).all()

    job_entries_frontend = []

    # Remove the user ID and unwanted data before sending it to the frontend.
    for j in job_entries:
        job_entry = {
            "job_entry_id": j.job_entry_id,
            "job_title": j.job_title,
            "company_name": j.company_name,
            "relevancy": j.relevancy,
        }
        job_entries_frontend.append(job_entry)

    # HTMX requests normally return partial HTML.
    # After a successful login, I need to return the full page instead.
    # This session variable distinguishes the initial post-login request from
    # subsequent HTMX requests, allowing the correct response to be returned.
    if session.get("first-access-to-app-via-htmx"):
        session["first-access-to-app-via-htmx"] = False
        return render_template(
            "user/base.html",
            page="apply",
            form=form,
            message=message,
            job_entries=job_entries_frontend,
            title="Apply",
        )

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
            title="Apply",
        )
