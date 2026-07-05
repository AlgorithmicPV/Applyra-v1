from flask import Blueprint, render_template, request, session
from flask_login import current_user, login_required
from app.forms import EducationForm
from app.models import UserProfile, Education
import uuid
from app.extensions import db
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete


onboarding_api_bp = Blueprint("onboarding_api", __name__)


@onboarding_api_bp.route("/education/collect", methods=["POST", "GET"])
@login_required
def education_collect():
    form = EducationForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    education_id = str(uuid.uuid4())
    certificate = form.certificate.data
    institution = form.institution.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data
    update_form = EducationForm()

    new_qualification = Education(
        education_id=education_id,
        user_profile_id=current_user.user_id,  # this is not the user_profile_id, this id is from the user table
        qualification=certificate,
        institution=institution,
        location=location,
        start_year=date(start_year, 1, 1),  # Convert the integer to a date object
        end_year=date(end_year, 12, 31),  # Convert the integer to a date object
        notes=notes,
    )

    try:
        db.session.add(new_qualification)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    # It is required to have the same variable's names as the web/onboarding.py
    # Because, I am using same html page
    return render_template(
        "onboarding/components/education.html",
        education_id=education_id,
        certificate=certificate,
        institution=institution,
        location=location,
        start_year=start_year,
        end_year=end_year,
        notes=notes,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.route("/education/update/<id>", methods=["POST", "GET"])
@login_required
def education_update(id):
    form = EducationForm(request.form)

    if not (request.method == "POST" and form.validate()):
        return form.errors

    stmt = db.select(Education).where(Education.education_id == id)
    education = db.session.execute(stmt).scalar_one()

    certificate = form.certificate.data
    institution = form.institution.data
    location = form.location.data
    start_year = form.start_year.data
    end_year = form.end_year.data
    notes = form.description.data
    update_form = EducationForm()

    try:
        education.qualification = certificate
        education.institution = institution
        education.location = location
        education.start_year = date(start_year, 1, 1)
        education.end_year = date(end_year, 12, 31)
        education.notes = notes
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "The data you're trying to add already exists"}

    return render_template(
        "onboarding/components/education.html",
        education_id=id,
        certificate=certificate,
        institution=institution,
        location=location,
        start_year=start_year,
        end_year=end_year,
        notes=notes,
        form=update_form,
        api=True,
    )


@onboarding_api_bp.route("/education/delete/<id>", methods=["DELETE"])
@login_required
def education_delete(id):
    stmt = delete(Education).where(Education.education_id == id)
    db.session.execute(stmt)
    db.session.commit()

    return "", 200
