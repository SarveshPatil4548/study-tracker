from datetime import date, timedelta
from collections import defaultdict
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, StudySession, Subject, Topic

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats")
@login_required
def stats():
    uid = current_user.id
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()

    today_stats = {}
    week_stats = {}
    alltime_stats = {}

    for s in subjects:
        today_stats[s.id] = (
            db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
            .filter(StudySession.user_id == uid, StudySession.subject_id == s.id, StudySession.date == today)
            .scalar()
        )
        week_stats[s.id] = (
            db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
            .filter(
                StudySession.user_id == uid,
                StudySession.subject_id == s.id,
                StudySession.date >= week_start,
                StudySession.date <= today,
            )
            .scalar()
        )
        alltime_stats[s.id] = (
            db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
            .filter(StudySession.user_id == uid, StudySession.subject_id == s.id)
            .scalar()
        )

    all_dates = (
        db.session.query(StudySession.date)
        .filter(StudySession.user_id == uid)
        .distinct()
        .order_by(StudySession.date.desc())
        .all()
    )
    all_dates = [row[0] for row in all_dates]

    streak = 0
    check_date = today
    date_set = set(all_dates)
    while check_date in date_set:
        streak += 1
        check_date -= timedelta(days=1)

    topic_stats = {}
    for s in subjects:
        topics = Topic.query.filter_by(user_id=uid, subject_id=s.id).order_by(Topic.name).all()
        if topics:
            topic_data = []
            for t in topics:
                total = (
                    db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
                    .filter(StudySession.user_id == uid, StudySession.topic_id == t.id)
                    .scalar()
                )
                topic_data.append({"name": t.name, "total": total})
            unassigned = (
                db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
                .filter(StudySession.user_id == uid, StudySession.subject_id == s.id, StudySession.topic_id.is_(None))
                .scalar()
            )
            topic_stats[s.id] = {"topics": topic_data, "unassigned": unassigned}

    insights = compute_insights(uid, all_dates, subjects, alltime_stats)

    return render_template(
        "stats.html",
        subjects=subjects,
        today_stats=today_stats,
        week_stats=week_stats,
        alltime_stats=alltime_stats,
        streak=streak,
        topic_stats=topic_stats,
        insights=insights,
    )


def compute_insights(uid, all_dates, subjects, alltime_stats):
    if not all_dates:
        return None

    weekday_minutes = defaultdict(int)
    weekday_count = defaultdict(int)
    all_sessions = StudySession.query.filter(StudySession.user_id == uid).all()

    for s in all_sessions:
        wd = s.date.weekday()
        weekday_minutes[wd] += s.duration_minutes
        weekday_count[wd] += 1

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    best_weekday = None
    worst_weekday = None
    if weekday_minutes:
        best_wd = max(weekday_minutes, key=weekday_minutes.get)
        best_weekday = {
            "name": weekday_names[best_wd],
            "avg": weekday_minutes[best_wd] // max(weekday_count[best_wd], 1),
            "total": weekday_minutes[best_wd],
        }

        studied_wds = {wd for wd in weekday_count if weekday_count[wd] > 0}
        unstudied = [wd for wd in range(7) if wd not in studied_wds]
        if unstudied:
            worst_weekday = {"name": weekday_names[unstudied[0]], "avg": 0, "total": 0}
        else:
            worst_wd = min(weekday_minutes, key=weekday_minutes.get)
            worst_weekday = {
                "name": weekday_names[worst_wd],
                "avg": weekday_minutes[worst_wd] // max(weekday_count[worst_wd], 1),
                "total": weekday_minutes[worst_wd],
            }

    longest_streak = 0
    current_streak = 0
    sorted_dates = sorted(set(all_dates))
    for i, d in enumerate(sorted_dates):
        if i == 0:
            current_streak = 1
        else:
            if d - sorted_dates[i - 1] == timedelta(days=1):
                current_streak += 1
            else:
                current_streak = 1
        longest_streak = max(longest_streak, current_streak)

    most_studied = None
    if alltime_stats:
        top_id = max(alltime_stats, key=alltime_stats.get)
        top_minutes = alltime_stats[top_id]
        if top_minutes > 0:
            top_subject = next((s for s in subjects if s.id == top_id), None)
            if top_subject:
                most_studied = {
                    "name": top_subject.name,
                    "minutes": top_minutes,
                }

    busiest_day = None
    day_totals = defaultdict(int)
    for s in all_sessions:
        day_totals[s.date] += s.duration_minutes
    if day_totals:
        busiest_date = max(day_totals, key=day_totals.get)
        busiest_day = {"date": busiest_date, "minutes": day_totals[busiest_date]}

    return {
        "best_weekday": best_weekday,
        "worst_weekday": worst_weekday,
        "longest_streak": longest_streak,
        "most_studied": most_studied,
        "busiest_day": busiest_day,
    }
