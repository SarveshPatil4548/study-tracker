from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, User, Subject, StudySession

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_info":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()

            errors = []
            if not username or not email:
                errors.append("Username and email are required.")
            if len(username) < 3:
                errors.append("Username must be at least 3 characters.")
            if username != user.username and User.query.filter_by(username=username).first():
                errors.append("Username already taken.")
            if email != user.email and User.query.filter_by(email=email).first():
                errors.append("Email already registered.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return redirect(url_for("profile.profile"))

            user.username = username
            user.email = email
            db.session.commit()
            flash("Profile updated.", "success")

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            errors = []
            if not current_password or not new_password or not confirm_password:
                errors.append("All password fields are required.")
            if not user.check_password(current_password):
                errors.append("Current password is incorrect.")
            if len(new_password) < 6:
                errors.append("New password must be at least 6 characters.")
            if new_password != confirm_password:
                errors.append("New passwords do not match.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return redirect(url_for("profile.profile"))

            user.set_password(new_password)
            db.session.commit()
            flash("Password changed successfully.", "success")

        return redirect(url_for("profile.profile"))

    total_subjects = Subject.query.filter_by(user_id=user.id).count()
    total_sessions = StudySession.query.filter_by(user_id=user.id).count()
    total_minutes = (
        db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
        .filter(StudySession.user_id == user.id)
        .scalar()
    )

    return render_template(
        "profile.html",
        total_subjects=total_subjects,
        total_sessions=total_sessions,
        total_minutes=total_minutes,
    )
