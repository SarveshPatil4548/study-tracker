from datetime import date, timedelta
from collections import defaultdict
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, StudySession, Subject

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/calendar")
@login_required
def calendar():
    uid = current_user.id
    today = date.today()
    year = today.year
    month = today.month

    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    sessions = (
        db.session.query(
            StudySession.date,
            func.coalesce(func.sum(StudySession.duration_minutes), 0),
        )
        .filter(StudySession.user_id == uid, StudySession.date >= first_day, StudySession.date <= last_day)
        .group_by(StudySession.date)
        .all()
    )

    day_minutes = {row[0]: row[1] for row in sessions}

    day_subjects = (
        db.session.query(
            StudySession.date,
            Subject.name,
            Subject.color,
            func.coalesce(func.sum(StudySession.duration_minutes), 0),
        )
        .join(Subject, StudySession.subject_id == Subject.id)
        .filter(StudySession.user_id == uid, StudySession.date >= first_day, StudySession.date <= last_day)
        .group_by(StudySession.date, Subject.name, Subject.color)
        .all()
    )

    day_subject_map = defaultdict(list)
    for row in day_subjects:
        day_subject_map[row[0]].append({
            "name": row[1],
            "color": row[2],
            "minutes": row[3],
        })

    heatmap_data = []
    total_minutes = 0
    days_studied = 0
    max_minutes = max(day_minutes.values()) if day_minutes else 0

    current = first_day
    while current <= last_day:
        minutes = day_minutes.get(current, 0)
        total_minutes += minutes
        if minutes > 0:
            days_studied += 1
        heatmap_data.append({
            "date": current.isoformat(),
            "day": current.day,
            "weekday": current.strftime("%a"),
            "is_today": current == today,
            "minutes": minutes,
            "subjects": day_subject_map.get(current, []),
        })
        current += timedelta(days=1)

    start_weekday = first_day.weekday()

    prev_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

    return render_template(
        "calendar.html",
        heatmap_data=heatmap_data,
        year=year,
        month=month,
        month_name=first_day.strftime("%B"),
        today=today,
        total_minutes=total_minutes,
        days_studied=days_studied,
        max_minutes=max_minutes,
        start_weekday=start_weekday,
        days_in_month=last_day.day,
    )
