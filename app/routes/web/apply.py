from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required

apply_web_bp = Blueprint("apply_web", __name__)


@apply_web_bp.route("/apply", methods=["POST", "GET"])
@login_required
def apply():
    if request.headers.get("HX-Request") == "true":
        return render_template("user/apply/base.html")
    else:
        return render_template("user/base.html", page="apply")
