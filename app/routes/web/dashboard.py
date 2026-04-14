from flask import Blueprint, request, render_template
from flask_login import current_user, login_required

dashboard_web_bp = Blueprint("dashboard_web", __name__)


@dashboard_web_bp.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    print(current_user.full_name)
    return render_template("user/base.html", title="Dashboard", page="dashboard")
