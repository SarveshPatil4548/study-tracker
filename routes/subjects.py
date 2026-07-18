from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Subject

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():
    uid = current_user.id
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        color = request.form.get("color", "").strip() or None
        if not name:
            flash("Subject name is required.", "error")
        else:
            subject = Subject(user_id=uid, name=name, color=color)
            db.session.add(subject)
            db.session.commit()
            flash("Subject added.", "success")
        return redirect(url_for("subjects.subjects"))

    all_subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
    return render_template("subjects.html", subjects=all_subjects)


@subjects_bp.route("/subjects/<int:id>/edit", methods=["POST"])
@login_required
def edit_subject(id):
    subject = Subject.query.filter_by(id=id, user_id=current_user.id).first()
    if not subject:
        abort(404)
    name = request.form.get("name", "").strip()
    color = request.form.get("color", "").strip() or None
    if not name:
        flash("Subject name is required.", "error")
    else:
        subject.name = name
        subject.color = color
        db.session.commit()
        flash("Subject updated.", "success")
    return redirect(url_for("subjects.subjects"))


@subjects_bp.route("/subjects/<int:id>/delete", methods=["POST"])
@login_required
def delete_subject(id):
    subject = Subject.query.filter_by(id=id, user_id=current_user.id).first()
    if not subject:
        abort(404)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "success")
    return redirect(url_for("subjects.subjects"))
