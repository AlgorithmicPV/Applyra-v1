from flask import Blueprint, render_template, request, session
from flask_login import current_user, login_required
from app.forms import EducationForm
from app.models import UserProfile, Education
import uuid
from app.extensions import db


onboarding_api_bp = Blueprint("onboarding_api", __name__)


@onboarding_api_bp.route("/education/", methods=["POST", "GET"])
@login_required
def education():
    form = EducationForm(request.form)
    update_form = EducationForm()

    if not (request.method == "POST" and form.validate()):
        return form.errors

    education_id = str(uuid.uuid4())

    certificate = form.certificate.data
    institution = form.institution.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data

    #    new_qualification = Education(
    #        education_id=education_id,
    #        user_profile_id=current_user.user_id,
    #        qualification=form.certificate.data,
    #        location=form.location.data,
    #        start_year=form.start_year.data,
    #        end_year=form.end_year.data,
    #        notes=form.description.data,
    #    )
    #
    #    db.session.add(new_qualification)

    return render_template(
        "onboarding/components/education.html",
        certificate=certificate,
        institution=institution,
        location=location,
        start_year=start_year,
        end_year=end_year,
        notes=notes,
        form=update_form,
    )
