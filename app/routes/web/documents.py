from flask import Blueprint, request, render_template, session
from app.forms import fileUplaod
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from flask_login import current_user, login_required


documents_web_bp = Blueprint("documents_web", __name__)


@documents_web_bp.route("/files", methods=["POST", "GET"])
@login_required
def doc_home():
    form = fileUplaod()
    if request.headers.get("HX-Request") == "true":
        return render_template("user/documents-pages/doc-home.html", form=form)
    else:
        return render_template(
            "user/base.html", title="Files", page="doc-home", form=form
        )


@documents_web_bp.route("/documents-editor", methods=["POST", "GET"])
@login_required
def document_editor():
    markdown_code = session.get(hash_key("markdown_code"))

    if request.headers.get("HX-Request") == "true":
        return render_template(
            "user/documents-pages/document-editor.html", markdown_code=markdown_code
        )
    else:
        return render_template(
            "user/base.html",
            title="Document Editor",
            page="document-editor",
            markdown_code=markdown_code,
        )
