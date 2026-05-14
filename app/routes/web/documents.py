from flask import Blueprint, request, render_template


documents_web_bp = Blueprint("documents_web", __name__)


@documents_web_bp.route("/documents-editor", methods=["POST", "GET"])
def document_editor():
    if request.headers.get("HX-Request") == "true":
        return render_template("user/documents-pages/document-editor.html")
    else:
        return render_template(
            "user/base.html",
            title="Document Editor",
            page="document-editor",
        )
