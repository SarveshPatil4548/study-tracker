from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func
from models import db, Exam, Subject, StudySession

exams_bp = Blueprint("exams", __name__)


def _get_exams_with_stats():
    uid = current_user.id
    today = date.today()
    exams = Exam.query.filter_by(user_id=uid).order_by(Exam.exam_date.asc()).all()
    result = []
    for exam in exams:
        days_left = (exam.exam_date - today).days
        study_minutes = (
            db.session.query(
                func.coalesce(func.sum(StudySession.duration_minutes), 0)
            )
            .filter(
                StudySession.user_id == uid,
                StudySession.subject_id == exam.subject_id,
                StudySession.date >= exam.created_at.date(),
            )
            .scalar()
        )
        if days_left < 0:
            urgency = "overdue"
        elif days_left <= 3:
            urgency = "urgent"
        elif days_left <= 7:
            urgency = "soon"
        else:
            urgency = "normal"
        result.append({
            "exam": exam,
            "days_left": days_left,
            "study_minutes": study_minutes,
            "urgency": urgency,
        })
    return result


@exams_bp.route("/exams")
@login_required
def exams_list():
    exams = _get_exams_with_stats()
    subjects = Subject.query.filter_by(user_id=current_user.id).order_by(Subject.name).all()
    return render_template("exams.html", exams=exams, subjects=subjects, today=date.today())


@exams_bp.route("/exams/new", methods=["GET", "POST"])
@login_required
def new_exam():
    uid = current_user.id
    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
    if request.method == "POST":
        subject_id = request.form.get("subject_id", type=int)
        title = request.form.get("title", "").strip()
        exam_date_str = request.form.get("exam_date", "")
        notes = request.form.get("notes", "").strip() or None

        if not subject_id or not title or not exam_date_str:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("exams.new_exam"))

        from datetime import datetime as dt
        try:
            exam_date = dt.strptime(exam_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("exams.new_exam"))

        exam = Exam(
            user_id=uid,
            subject_id=subject_id,
            title=title,
            exam_date=exam_date,
            notes=notes,
        )
        db.session.add(exam)
        db.session.commit()
        flash(f"Exam '{title}' added successfully!", "success")
        return redirect(url_for("exams.exams_list"))

    return render_template("new_exam.html", subjects=subjects, today=date.today().isoformat())


@exams_bp.route("/exams/<int:id>/edit", methods=["POST"])
@login_required
def edit_exam(id):
    exam = Exam.query.filter_by(id=id, user_id=current_user.id).first()
    if not exam:
        abort(404)
    subject_id = request.form.get("subject_id", type=int)
    title = request.form.get("title", "").strip()
    exam_date_str = request.form.get("exam_date", "")
    notes = request.form.get("notes", "").strip() or None

    if not subject_id or not title or not exam_date_str:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("exams.exams_list"))

    from datetime import datetime as dt
    try:
        exam_date = dt.strptime(exam_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "error")
        return redirect(url_for("exams.exams_list"))

    exam.subject_id = subject_id
    exam.title = title
    exam.exam_date = exam_date
    exam.notes = notes
    db.session.commit()
    flash(f"Exam '{title}' updated.", "success")
    return redirect(url_for("exams.exams_list"))


@exams_bp.route("/exams/<int:id>/delete", methods=["POST"])
@login_required
def delete_exam(id):
    exam = Exam.query.filter_by(id=id, user_id=current_user.id).first()
    if not exam:
        abort(404)
    title = exam.title
    db.session.delete(exam)
    db.session.commit()
    flash(f"Exam '{title}' deleted.", "success")
    return redirect(url_for("exams.exams_list"))
