from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Goal, Subject

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/goals/<int:subject_id>/set", methods=["POST"])
@login_required
def set_goal(subject_id):
    uid = current_user.id
    subject = Subject.query.filter_by(id=subject_id, user_id=uid).first()
    if not subject:
        abort(404)
    weekly_target = request.form.get("weekly_target_minutes", type=int)

    if not weekly_target or weekly_target <= 0:
        flash("Please enter a valid weekly target in minutes.", "error")
        return redirect(url_for("subjects.subjects"))

    existing = Goal.query.filter_by(user_id=uid, subject_id=subject_id).first()
    if existing:
        existing.weekly_target_minutes = weekly_target
    else:
        goal = Goal(user_id=uid, subject_id=subject_id, weekly_target_minutes=weekly_target)
        db.session.add(goal)

    db.session.commit()
    flash(f"Goal set for {subject.name}: {weekly_target} min/week.", "success")
    return redirect(url_for("subjects.subjects"))


@goals_bp.route("/goals/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_goal(subject_id):
    uid = current_user.id
    goal = Goal.query.filter_by(user_id=uid, subject_id=subject_id).first()
    if goal:
        db.session.delete(goal)
        db.session.commit()
        flash("Goal removed.", "success")
    return redirect(url_for("subjects.subjects"))
