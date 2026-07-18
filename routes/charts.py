from datetime import date, timedelta
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, StudySession, Subject

charts_bp = Blueprint("charts", __name__)


@charts_bp.route("/api/chart-data")
@login_required
def chart_data():
    uid = current_user.id
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    subjects = Subject.query.filter_by(user_id=uid).order_by(Subject.name).all()

    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    date_labels = [d.strftime("%a %b %d") for d in dates]

    datasets = []
    for s in subjects:
        daily = []
        for d in dates:
            mins = (
                db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
                .filter(StudySession.user_id == uid, StudySession.subject_id == s.id, StudySession.date == d)
                .scalar()
            )
            daily.append(round(mins / 60, 1))
        color = s.color or "#818cf8"
        datasets.append({
            "label": s.name,
            "data": daily,
            "backgroundColor": color,
            "borderRadius": 4,
        })

    doughnut_labels = []
    doughnut_data = []
    doughnut_colors = []
    for s in subjects:
        total = (
            db.session.query(func.coalesce(func.sum(StudySession.duration_minutes), 0))
            .filter(StudySession.user_id == uid, StudySession.subject_id == s.id)
            .scalar()
        )
        if total > 0:
            doughnut_labels.append(s.name)
            doughnut_data.append(round(total / 60, 1))
            doughnut_colors.append(s.color or "#818cf8")

    return jsonify({
        "bar": {"labels": date_labels, "datasets": datasets},
        "doughnut": {"labels": doughnut_labels, "data": doughnut_data, "colors": doughnut_colors},
    })
