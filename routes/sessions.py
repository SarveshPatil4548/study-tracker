from datetime import date
import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, StudySession, Subject, Topic
from utils import split_duration

sessions_bp = Blueprint("sessions", __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    if not file or not file.filename:
        return None
    original = secure_filename(file.filename)
    if not original:
        return None
    ext = original.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    uploads_dir = os.path.join(current_app.root_path, "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file.save(os.path.join(uploads_dir, unique_name))
    return unique_name


@sessions_bp.route("/sessions/new", methods=["GET", "POST"])
@login_required
def new_session():
    uid = current_user.id
    if request.method == "POST":
        subject_id = request.form.get("subject_id", type=int)
        session_date = request.form.get("date", "")
        hours = request.form.get("duration_hours", type=int) or 0
        mins = request.form.get("duration_mins", type=int) or 0
        duration = hours * 60 + mins
        notes = request.form.get("notes", "").strip() or None
        topic_id = request.form.get("topic_id", type=int) or None

        if not subject_id or not session_date:
            flash("Subject and date are required.", "error")
        elif duration <= 0:
            flash("Please enter a duration.", "error")
        else:
            attachment_filename = None
            file = request.files.get("attachment")
            if file and file.filename:
                if not allowed_file(file.filename):
                    flash("Invalid file type. Allowed: PDF, PNG, JPG, TXT.", "error")
                    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
                    return render_template("log_session.html", subjects=subjects, today=date.today().isoformat())
                attachment_filename = save_upload(file)

            parsed_date = date.fromisoformat(session_date)
            sess = StudySession(
                user_id=uid,
                subject_id=subject_id,
                topic_id=topic_id,
                date=parsed_date,
                duration_minutes=duration,
                notes=notes,
                attachment_filename=attachment_filename,
            )
            db.session.add(sess)
            db.session.commit()
            flash("Session logged.", "success")
            return redirect(url_for("sessions.sessions_list"))

    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
    return render_template("log_session.html", subjects=subjects, today=date.today().isoformat())


@sessions_bp.route("/sessions")
@login_required
def sessions_list():
    uid = current_user.id
    query = StudySession.query.filter(StudySession.user_id == uid)

    subject_id = request.args.get("subject_id", type=int)
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    if subject_id:
        query = query.filter(StudySession.subject_id == subject_id)
    if date_from:
        query = query.filter(StudySession.date >= date.fromisoformat(date_from))
    if date_to:
        query = query.filter(StudySession.date <= date.fromisoformat(date_to))

    sessions = query.order_by(StudySession.date.desc(), StudySession.id.desc()).all()
    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
    return render_template(
        "sessions_list.html",
        sessions=sessions,
        subjects=subjects,
        selected_subject=subject_id,
        date_from=date_from,
        date_to=date_to,
    )


@sessions_bp.route("/sessions/<int:id>/edit", methods=["POST"])
@login_required
def edit_session(id):
    sess = StudySession.query.filter_by(id=id, user_id=current_user.id).first()
    if not sess:
        abort(404)
    subject_id = request.form.get("subject_id", type=int)
    session_date = request.form.get("date", "")
    hours = request.form.get("duration_hours", type=int) or 0
    mins = request.form.get("duration_mins", type=int) or 0
    duration = hours * 60 + mins
    notes = request.form.get("notes", "").strip() or None

    if not subject_id or not session_date:
        flash("Subject and date are required.", "error")
    elif duration <= 0:
        flash("Please enter a duration.", "error")
    else:
        sess.subject_id = subject_id
        sess.date = date.fromisoformat(session_date)
        sess.duration_minutes = duration
        sess.notes = notes
        db.session.commit()
        flash("Session updated.", "success")
    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<int:id>/delete", methods=["POST"])
@login_required
def delete_session(id):
    sess = StudySession.query.filter_by(id=id, user_id=current_user.id).first()
    if not sess:
        abort(404)
    if sess.attachment_filename:
        uploads_dir = os.path.join(current_app.root_path, "..", "uploads")
        filepath = os.path.join(uploads_dir, sess.attachment_filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
    db.session.delete(sess)
    db.session.commit()
    flash("Session deleted.", "success")
    return redirect(url_for("sessions.sessions_list"))
