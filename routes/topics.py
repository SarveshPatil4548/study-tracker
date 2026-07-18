from flask import Blueprint, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from models import db, Topic, Subject

topics_bp = Blueprint("topics", __name__)


@topics_bp.route("/topics/<int:subject_id>/add", methods=["POST"])
@login_required
def add_topic(subject_id):
    uid = current_user.id
    Subject.query.filter_by(id=subject_id, user_id=uid).first() or abort(404)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Topic name is required.", "error")
        return redirect(url_for("subjects.subjects"))
    topic = Topic(user_id=uid, subject_id=subject_id, name=name)
    db.session.add(topic)
    db.session.commit()
    flash(f"Topic \"{name}\" added.", "success")
    return redirect(url_for("subjects.subjects"))


@topics_bp.route("/topics/<int:topic_id>/edit", methods=["POST"])
@login_required
def edit_topic(topic_id):
    topic = Topic.query.filter_by(id=topic_id, user_id=current_user.id).first()
    if not topic:
        abort(404)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Topic name is required.", "error")
    else:
        topic.name = name
        db.session.commit()
        flash("Topic updated.", "success")
    return redirect(url_for("subjects.subjects"))


@topics_bp.route("/topics/<int:topic_id>/delete", methods=["POST"])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.filter_by(id=topic_id, user_id=current_user.id).first()
    if not topic:
        abort(404)
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted.", "success")
    return redirect(url_for("subjects.subjects"))


@topics_bp.route("/api/topics/<int:subject_id>")
@login_required
def topics_for_subject(subject_id):
    uid = current_user.id
    Subject.query.filter_by(id=subject_id, user_id=uid).first() or abort(404)
    topics = Topic.query.filter_by(user_id=uid, subject_id=subject_id).order_by(Topic.name).all()
    return jsonify([{"id": t.id, "name": t.name} for t in topics])


@topics_bp.route("/topics/<int:topic_id>/toggle-complete", methods=["POST"])
@login_required
def toggle_topic_complete(topic_id):
    topic = Topic.query.filter_by(id=topic_id, user_id=current_user.id).first()
    if not topic:
        abort(404)
    topic.completed = not topic.completed
    db.session.commit()
    return jsonify({"id": topic.id, "completed": topic.completed})
