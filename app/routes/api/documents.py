"""This module handles the backend routes for the documents pages."""

from datetime import date, datetime

from flask import Blueprint, render_template, request, abort
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Application, Document, JobEntry

documents_api_bp = Blueprint("documents_api", __name__)


@documents_api_bp.get("/search/")
@login_required
def search():
    """Return documents matching the current search and type filters.

    Returns:
        The document rows HTML containing the matching documents.
    """

    query = request.args.get("q", "").strip().lower()
    doc_type = request.args.get("doc_type", "all")

    stmt = db.select(Document).where(Document.user_id == current_user.user_id)
    if doc_type == "cv":
        stmt = stmt.where(Document.doc_type == "cv")
    elif doc_type == "cover-letter":
        stmt = stmt.where(Document.doc_type == "coverLetter")

    documents = db.session.scalars(stmt).all()
    searched_documents = []

    for document in documents:
        if document.doc_type == "cv":
            application_stmt = db.select(Application).where(
                Application.cv_document_id == document.doc_id
            )
            frontend_doc_type = "cv"
        else:
            application_stmt = db.select(Application).where(
                Application.cover_letter_document_id == document.doc_id
            )
            frontend_doc_type = "cover-letter"

        application = db.session.scalars(application_stmt).first()
        if application is None:
            continue

        job_entry_stmt = db.select(JobEntry).where(
            JobEntry.job_entry_id == application.job_entry_id,
            JobEntry.user_id == current_user.user_id,
        )
        job_entry = db.session.scalars(job_entry_stmt).first()
        if job_entry is None:
            continue

        role = document.role or ""
        company = job_entry.company_name or ""
        if (
            query
            and query not in role.lower()
            and query not in company.lower()
        ):
            continue

        searched_documents.append(
            {
                "doc_id": document.doc_id,
                "created_at": document.created_at.strftime("%Y-%m-%d"),
                "updated_at": (
                    document.updated_at.strftime("%Y-%m-%d")
                    if document.updated_at
                    else None
                ),
                "doc_type": frontend_doc_type,
                "role": role,
                "company": company,
            }
        )

    searched_documents.sort(
        key=lambda document: datetime.strptime(
            document["updated_at"] or document["created_at"], "%Y-%m-%d"
        ),
        reverse=True,
    )

    return render_template(
        "user/documents-pages/document-rows.html", all_docs=searched_documents
    )


@documents_api_bp.post("/save/")
@login_required
def doc_save():
    """Save the updated content of a document.

    Returns:
        A success message, or a dictionary containing an error.
    """

    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}

    id = data.get("doc_id")
    content = data.get("doc_content")

    stmt = db.select(Document).where(Document.doc_id == id)
    doc = db.session.scalars(stmt).first()

    if not doc:
        return {"error": "Your file id has changed"}

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

    doc.content = content
    doc.updated_at = date.today()

    db.session.commit()

    return {"success": "Your file is saved"}
