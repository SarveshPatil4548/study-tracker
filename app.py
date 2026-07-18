from flask import Flask, send_from_directory, abort, render_template, flash, make_response, redirect, url_for
from flask_login import LoginManager, current_user
from werkzeug.exceptions import RequestEntityTooLarge
from config import Config
from models import db, Subject, User
from utils import format_duration, split_duration
from sqlalchemy import inspect
from datetime import date
import os

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

    app.jinja_env.filters["format_duration"] = format_duration
    app.jinja_env.filters["split_duration"] = split_duration

    db.init_app(app)
    login_manager.init_app(app)

    uploads_dir = os.path.join(app.root_path, "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ["users", "subjects", "study_sessions", "goals", "topics", "exams"]
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            db.create_all()

        _migrate_existing_data()

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.subjects import subjects_bp
    from routes.sessions import sessions_bp
    from routes.stats import stats_bp
    from routes.goals import goals_bp
    from routes.charts import charts_bp
    from routes.topics import topics_bp
    from routes.notes import notes_bp
    from routes.calendar import calendar_bp
    from routes.exams import exams_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(profile_bp)

    @app.route("/uploads/<filename>")
    def serve_upload(filename):
        uploads_dir = os.path.join(app.root_path, "..", "uploads")
        if not os.path.isfile(os.path.join(uploads_dir, filename)):
            abort(404)
        return send_from_directory(uploads_dir, filename, as_attachment=True)

    @app.route("/uploads/<filename>/view")
    def serve_upload_inline(filename):
        uploads_dir = os.path.join(app.root_path, "..", "uploads")
        filepath = os.path.join(uploads_dir, filename)
        if not os.path.isfile(filepath):
            abort(404)
        ext = filename.rsplit(".", 1)[-1].lower()
        content_type_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "txt": "text/plain",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
        with open(filepath, "rb") as f:
            data = f.read()
        resp = make_response(data)
        resp.headers["Content-Type"] = content_type
        resp.headers["Content-Disposition"] = f"inline; filename=\"{filename}\""
        return resp

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        flash("File is too large. Maximum size is 5MB.", "error")
        if current_user.is_authenticated:
            subjects = Subject.query.filter_by(user_id=current_user.id).order_by(Subject.name).all()
        else:
            subjects = []
        return render_template("log_session.html", subjects=subjects, today=date.today().isoformat()), 413

    return app


def _migrate_existing_data():
    from models import StudySession, Topic, Goal, Exam

    tables_to_check = [
        ("subjects", Subject),
        ("study_sessions", StudySession),
        ("topics", Topic),
        ("goals", Goal),
        ("exams", Exam),
    ]

    insp = inspect(db.engine)
    if "users" not in insp.get_table_names():
        return

    first_user = User.query.order_by(User.id.asc()).first()
    if not first_user:
        return

    existing_tables = set(insp.get_table_names())
    for table_name, model in tables_to_check:
        if table_name not in existing_tables:
            continue
        has_user_id_col = any(
            col["name"] == "user_id"
            for col in insp.get_columns(table_name)
        )
        if not has_user_id_col:
            continue
        orphans = model.query.filter(model.user_id.is_(None)).first()
        if orphans:
            model.query.filter(model.user_id.is_(None)).update({"user_id": first_user.id})
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)