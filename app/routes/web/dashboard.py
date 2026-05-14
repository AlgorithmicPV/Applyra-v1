from flask import Blueprint, request, render_template, session
from flask_login import current_user, login_required

dashboard_web_bp = Blueprint("dashboard_web", __name__)


@dashboard_web_bp.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    print(current_user.full_name)
    print(request.headers.get("HX-Request"))
    if session.get("first-access-to-dashboard-via-htmx"):
        session["first-access-to-dashboard-via-htmx"] = False
        return render_template("user/base.html", page="dashboard")
    if request.headers.get("HX-Request") == "true":
        return render_template("user/dashboard.html")
    else:
        return render_template("user/base.html", page="dashboard")
