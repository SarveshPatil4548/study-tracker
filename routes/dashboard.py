from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import func
from models import db, StudySession, Subject, Exam

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def dashboard():
    uid = current_user.id
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    day_of_week = today.weekday()
    days_in_week = 7

    today_total = (
        db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
        .filter(StudySession.user_id == uid, StudySession.date == today)
        .scalar()
    )

    week_total = (
        db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
        .filter(StudySession.user_id == uid, StudySession.date >= week_start, StudySession.date <= today)
        .scalar()
    )

    alltime_total = (
        db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
        .filter(StudySession.user_id == uid)
        .scalar()
    )

    total_sessions = db.session.query(func.count(StudySession.id)).filter(StudySession.user_id == uid).scalar()

    recent_sessions = (
        StudySession.query
        .filter(StudySession.user_id == uid)
        .order_by(StudySession.date.desc(), StudySession.id.desc())
        .limit(5)
        .all()
    )

    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()
    weekly_subject = {}
    for s in subjects:
        weekly_subject[s.id] = (
            db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
            .filter(
                StudySession.user_id == uid,
                StudySession.subject_id == s.id,
                StudySession.date >= week_start,
                StudySession.date <= today,
            )
            .scalar()
        )

    has_logged_today = today_total > 0

    goal_progress = []
    for s in subjects:
        if s.goal:
            current = weekly_subject.get(s.id, 0)
            target = s.goal.weekly_target_minutes
            pct = min(round((current / target) * 100) if target > 0 else 0, 100)
            expected_pct = round(((day_of_week + 1) / days_in_week) * 100)
            behind = pct < (expected_pct * 0.5)
            goal_progress.append({
                "subject": s,
                "current": current,
                "target": target,
                "pct": pct,
                "behind": behind,
            })

    upcoming_exams = (
        Exam.query
        .filter(Exam.user_id == uid, Exam.exam_date >= today)
        .order_by(Exam.exam_date.asc())
        .limit(3)
        .all()
    )
    upcoming_exams_data = []
    for exam in upcoming_exams:
        days_left = (exam.exam_date - today).days
        if days_left <= 3:
            urgency = "urgent"
        elif days_left <= 7:
            urgency = "soon"
        else:
            urgency = "normal"
        upcoming_exams_data.append({"exam": exam, "days_left": days_left, "urgency": urgency})

    return render_template(
        "dashboard.html",
        today_total=today_total,
        week_total=week_total,
        alltime_total=alltime_total,
        total_sessions=total_sessions,
        recent_sessions=recent_sessions,
        subjects=subjects,
        weekly_subject=weekly_subject,
        today=today,
        has_logged_today=has_logged_today,
        goal_progress=goal_progress,
        upcoming_exams=upcoming_exams_data,
    )
