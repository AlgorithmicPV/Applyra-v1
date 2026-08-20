"""This module handles the backend routes for the settings pages."""

import base64

from flask import (
    Blueprint,
    make_response,
    render_template,
    session,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db, password_hasher
from app.forms import (
    SettingsCodeRequestForm,
    SettingsDeleteForm,
    SettingsPasswordForm,
    SettingsProfileForm,
    SettingsTotpForm,
)
from app.models import (
    Application,
    Document,
    Education,
    JobEntry,
    User,
    UserPersonal,
    UserSkill,
    WorkExperience,
)
from app.utilities.validations import email_confirm

settings_api_bp = Blueprint("settings_api", __name__)


@settings_api_bp.post("/request-code/")
@login_required
def request_code():
    """Send a verification code before allowing settings changes.

    Returns:
        The settings HTML, or a dictionary containing an error.
    """

    form = SettingsCodeRequestForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    result = email_confirm(current_user.email, interval=600)
    if result.get("error"):
        return {"error": result.get("error")}

    return render_template(
        "user/settings/settings-static.html",
        code_form=SettingsCodeRequestForm(),
        pin_form=SettingsTotpForm(),
        code_sent=True,
    )


@settings_api_bp.post("/verify-code/")
@login_required
def verify_code():
    """Verify the code and display the editable settings page.

    Returns:
        The editable settings HTML, or a dictionary containing an error.
    """

    form = SettingsTotpForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    session["settings-verified-user"] = current_user.user_id

    profile_form = SettingsProfileForm()
    password_form = SettingsPasswordForm()
    delete_form = SettingsDeleteForm()

    return render_template(
        "user/settings/settings-editable/settings-edit.html",
        profile_form=profile_form,
        password_form=password_form,
        delete_form=delete_form,
    )


@settings_api_bp.post("/profile/update/")
@login_required
def profile_update():
    """Update the current user's profile details.

    Returns:
        A success message, or a dictionary containing an error.
    """

    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = SettingsProfileForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    image = form.profile_image.data
    if image:
        image_data = image.read(5 * 1024 * 1024 + 1)
        if len(image_data) > 5 * 1024 * 1024:
            return {"error": "Profile picture cannot be larger than 5 MB"}

        encoded_image = base64.b64encode(image_data).decode("utf-8")
        image_type = image.mimetype or "image/png"
        current_user.profile_image = (
            "data:" + image_type + ";base64," + encoded_image
        )

    current_user.full_name = form.full_name.data
    current_user.email = form.email.data

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That email address is already in use"}

    return {"success": "Personal details updated. Reload the Page"}


@settings_api_bp.post("/password/update/")
@login_required
def password_update():
    """Update the current user's password.

    Returns:
        A success message, or a dictionary containing an error.
    """

    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    if (
        current_user.auth_provider != "manual"
        or not current_user.password_hash
    ):
        return {"error": "Password changes are not available for this account"}

    form = SettingsPasswordForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    current_user.password_hash = password_hasher.hash(form.new_password.data)
    db.session.commit()
    return {"success": "Password updated"}


@settings_api_bp.post("/account/delete/")
@login_required
def account_delete():
    """Delete the current user's account and related information.

    Returns:
        A response that redirects the user to the login page.
    """

    if session.get("settings-verified-user") != current_user.user_id:
        return {"error": "Please verify your PIN again"}

    form = SettingsDeleteForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            return {"error": errors[0]}

    user_id = current_user.user_id

    # Delete child records first because they belong to the user account.
    (
        db.session.query(Application)
        .filter(Application.user_id == user_id)
        .delete()
    )
    db.session.query(Document).filter(Document.user_id == user_id).delete()
    db.session.query(JobEntry).filter(JobEntry.user_id == user_id).delete()
    db.session.query(Education).filter(Education.user_id == user_id).delete()
    db.session.query(UserSkill).filter(UserSkill.user_id == user_id).delete()
    (
        db.session.query(WorkExperience)
        .filter(WorkExperience.user_id == user_id)
        .delete()
    )
    (
        db.session.query(UserPersonal)
        .filter(UserPersonal.user_id == user_id)
        .delete()
    )
    db.session.query(User).filter(User.user_id == user_id).delete()
    db.session.commit()

    logout_user()
    session.clear()

    response = make_response({"success": "Your account has been deleted"})
    response.headers["HX-Redirect"] = url_for("auth_web.login")
    return response
