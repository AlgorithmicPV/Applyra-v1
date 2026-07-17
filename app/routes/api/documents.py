from datetime import date, datetime

from flask import Blueprint, request, render_template, redirect, url_for, session
from app.forms import fileUplaod
import pypandoc
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from app.models import Application, Document, JobEntry
from flask_login import current_user, login_required
import mammoth
import io
import uuid
from app.extensions import db


documents_api_bp = Blueprint("documents_api", __name__)


@documents_api_bp.route("/search/", methods=["GET"])
@login_required
def search():
    """Return documents matching the current search and type filters."""

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
        if query and query not in role.lower() and query not in company.lower():
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


@documents_api_bp.route("/uploads/", methods=["POST"])
@login_required
def doc_home():
    form = fileUplaod()

    if not (request.method == "POST" and form.validate()):
        return form.errors

    file = form.file.data
    content = file.read()
    # md = pypandoc.convert_text(content, "md", format="docx")

    # Dont do like this, put this into the database, and access to this again via the database
    # session[hash_key("markdown_code")] = encrypt_value(md)

    # result = mammoth.convert_to_html(io.BytesIO(content))
    # html = result.value

    # doc_id = str(uuid.uuid4())

    # print(html)

    # new_doc = Document(
    #    doc_id = doc_id,
    #    doc_type = "cv",
    #    user_id = current_user.user_id,
    #    content = html,
    #    created_at = "",
    #    updated_at = "",
    # )

    # WARNING: There is an issue, because the docs that is uploaded, i don't have a method to find what kind of document is that,
    # (there is a method, but takes a lot of time for that, and my main function is not a document editor, it is just to make CVs via AI),
    # Therefore, for now, Upload part will be stopped, i moved into other part, making the doc

    return redirect(url_for("documents_web.document_editor"))


@documents_api_bp.route("/save/", methods=["POST"])
@login_required
def doc_save():

    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}

    id = data.get("doc_id")
    content = data.get("doc_content")

    stmt = db.select(Document).where(Document.doc_id == id)
    doc = db.session.scalars(stmt).first()

    if not doc:
        return {"error": "Your file id has changed"}

    doc.content = content
    doc.updated_at = date.today()

    db.session.commit()

    return {"success": "Your file is saved"}
