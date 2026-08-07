"""This module handles the frontend route for the landing page."""

from flask import Blueprint, render_template

landing_web_bp = Blueprint("landing_web", __name__)


@landing_web_bp.route("/", methods=["POST", "GET"])
def landing():
    """Display the main landing page.

    Returns:
        The rendered landing page.
    """

    return render_template(
        "landing/index.html", title="Applyra — Tailored resumes for every job"
    )
