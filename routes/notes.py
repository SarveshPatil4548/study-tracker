from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, StudySession, Subject

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/notes")
@login_required
def notes():
    uid = current_user.id
    query = StudySession.query.filter(
        StudySession.user_id == uid,
        (StudySession.notes.isnot(None) & (StudySession.notes != ""))
        | (StudySession.attachment_filename.isnot(None))
    )

    subject_id = request.args.get("subject_id", type=int)
    search = request.args.get("q", "").strip()

    if subject_id:
        query = query.filter(StudySession.subject_id == subject_id)
    if search:
        query = query.filter(StudySession.notes.ilike(f"%{search}%"))

    sessions = query.order_by(StudySession.date.desc(), StudySession.id.desc()).all()
    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()

    return render_template(
        "notes.html",
        sessions=sessions,
        subjects=subjects,
        selected_subject=subject_id,
        search=search,
    )
