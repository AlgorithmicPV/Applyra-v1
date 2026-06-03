from flask import Blueprint, request, render_template, redirect, url_for, session
from app.forms import fileUplaod
import pypandoc
from app.utilities.client_sessions import encrypt_value, decrypt_value, hash_key
from app.models import Document
from flask_login import current_user, login_required


documents_api_bp = Blueprint("documents_api", __name__)


@documents_api_bp.route("/uploads/", methods=["POST"])
@login_required
def doc_home():
    form = fileUplaod()

    if not (request.method == "POST" and form.validate()):
        return form.errors

    file = form.file.data
    content = file.read()
    md = pypandoc.convert_text(content, "md", format="docx")

    # Dont do like this, put this into the database, and access to this again via the database
    session[hash_key("markdown_code")] = encrypt_value(md)

    return redirect(url_for("documents_web.document_editor"))
