from datetime import datetime
from flask import Blueprint, request, render_template, abort
from flask_login import current_user, login_required
from app.models import Document, Application, JobEntry
from app.extensions import db

documents_web_bp = Blueprint("documents_web", __name__)


@documents_web_bp.route("/files/", methods=["POST", "GET"])
@login_required
def doc_home():

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
            application = (
                db.session.execute(job_stmt).scalars().first()
            )  # Curent Status: Relationship between job_entry and document is one to one

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
            application = (
                db.session.execute(job_stmt).scalars().first()
            )  # Curent Status: Relationship between job_entry and document is one to one

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
            "user/base.html", title="All Documents", page="doc-home", all_docs=all_docs
        )


@documents_web_bp.route("/editor/<id>/", methods=["GET"])
@login_required
def editor(id):
    stmt = db.select(Document).where(Document.doc_id == id)
    doc = db.session.scalars(stmt).first()

    if not doc:
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
