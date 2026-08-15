"""This module handles the frontend routes for the documents pages."""

from datetime import datetime

from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Application, Document, JobEntry

documents_web_bp = Blueprint("documents_web", __name__)


@documents_web_bp.route("/files/", methods=["POST", "GET"])
@login_required
def doc_home():
    """Display all documents belonging to the current user.

    Returns:
        The full documents page or partial HTML for an HTMX request.
    """

    stmt = db.select(Document).where(Document.user_id == current_user.user_id)
    documents = db.session.execute(stmt).scalars().all()

    all_docs = []

    for doc in documents:
        doc_type = ""
        company = ""
        if doc.doc_type == "cv":
            doc_type = "cv"
            job_stmt = db.select(Application).where(
                Application.cv_document_id == doc.doc_id
            )
            # Currently, each job entry has one application document.
            application = db.session.execute(job_stmt).scalars().first()

            job_entry_id = application.job_entry_id

            job_entry_stmt = db.select(JobEntry).where(
                JobEntry.job_entry_id == job_entry_id
            )
            job_entry = db.session.execute(job_entry_stmt).scalars().first()

            company = job_entry.company_name

        else:
            doc_type = "cover-letter"
            job_stmt = db.select(Application).where(
                Application.cover_letter_document_id == doc.doc_id
            )
            # Currently, each job entry has one application document.
            application = db.session.execute(job_stmt).scalars().first()

            job_entry_id = application.job_entry_id

            job_entry_stmt = db.select(JobEntry).where(
                JobEntry.job_entry_id == job_entry_id
            )
            job_entry = db.session.execute(job_entry_stmt).scalars().first()

            company = job_entry.company_name

        d = {
            "doc_id": doc.doc_id,
            "created_at": doc.created_at.strftime("%Y-%m-%d"),
            "updated_at": (
                doc.updated_at.strftime("%Y-%m-%d") if doc.updated_at else None
            ),
            "doc_type": doc_type,
            "role": doc.role,
            "company": company,
        }

        all_docs.append(d)
        all_docs.sort(
            key=lambda d: datetime.strptime(
                d["updated_at"] if d["updated_at"] else d["created_at"],
                "%Y-%m-%d",
            ),
            reverse=True,  # newest first
        )

    if request.headers.get("HX-Request") == "true":
        return render_template("user/documents-pages/doc-home.html", all_docs=all_docs)
    else:
        return render_template(
            "user/base.html",
            title="All Documents",
            page="doc-home",
            all_docs=all_docs,
        )


@documents_web_bp.get("/editor/<id>/")
@login_required
def editor(id):
    """Display the editor for a selected document.

    Args:
        id: The ID of the document.

    Returns:
        The full editor page or partial HTML for an HTMX request.
    """

    stmt = db.select(Document).where(Document.doc_id == id)
    doc = db.session.scalars(stmt).first()

    if not doc:
        abort(404)

    # Check whether document belongs to the logged user
    doc_type = doc.doc_type
    application_stmt = (
        db.select(Application).where(
            Application.cv_document_id == id,
            Application.user_id == current_user.user_id,
        )
        if doc_type == "cv"
        else db.select(Application).where(
            Application.cover_letter_document_id == id,
            Application.user_id == current_user.user_id,
        )
    )
    application = db.session.scalars(application_stmt).first()

    if not application:
        abort(404)

    content = doc.content

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "user/documents-pages/editor.html",
            doc=content,
            doc_id=id,
            role=doc.role,
            doc_type=doc.doc_type,
        )
    else:
        return render_template(
            "user/base.html",
            title="Document Editor",
            page="document-editor",
            doc=content,
            doc_id=id,
            role=doc.role,
            doc_type=doc.doc_type,
        )
