from flask import Blueprint, render_template

landing_web_bp = Blueprint("landing_web", __name__)


@landing_web_bp.route("/", methods=["POST", "GET"])
def landing():
    return render_template(
        "landing/index.html", title="Applyra — Tailored resumes for every job"
    )
