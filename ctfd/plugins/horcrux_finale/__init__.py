"""Horcrux finale-scoring plugin.

Records each player's capstone-quiz result server-side for GRADING. Nothing is
shown to the player — the quiz UI only reveals the pass/fail ending. The engine
POSTs the result to /api/v1/horcrux/finale on submit; this stores one aggregate
row per player (attempts, first-try score, best score, whether they ever passed).

Read it with tools/finale_report.py.
"""
import datetime

from flask import Blueprint, jsonify, request

from CTFd.models import db
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user


class HorcruxFinale(db.Model):
    __tablename__ = "horcrux_finale"
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    attempts = db.Column(db.Integer, default=0)
    best_correct = db.Column(db.Integer, default=0)
    first_correct = db.Column(db.Integer)
    total = db.Column(db.Integer)
    ever_passed = db.Column(db.Boolean, default=False)
    first_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


def load(app):
    with app.app_context():
        db.create_all()  # idempotent — creates horcrux_finale if missing

    bp = Blueprint("horcrux_finale", __name__)

    @bp.route("/api/v1/horcrux/finale", methods=["POST"])
    @authed_only
    def record_finale():
        user = get_current_user()
        data = request.get_json(silent=True) or {}
        try:
            correct = int(data.get("correct", 0))
            total = int(data.get("total", 0))
        except (TypeError, ValueError):
            return jsonify({"success": False}), 400
        passed = bool(data.get("passed", False))
        now = datetime.datetime.utcnow()

        row = HorcruxFinale.query.get(user.id)
        if row is None:
            row = HorcruxFinale(
                user_id=user.id, attempts=1, best_correct=correct,
                first_correct=correct, total=total, ever_passed=passed,
                first_date=now, last_date=now,
            )
            db.session.add(row)
        else:
            row.attempts = (row.attempts or 0) + 1
            row.best_correct = max(row.best_correct or 0, correct)
            row.ever_passed = bool(row.ever_passed) or passed
            row.total = total
            row.last_date = now
        db.session.commit()
        return jsonify({"success": True})

    app.register_blueprint(bp)
    app.logger.info("[horcrux] finale-scoring plugin loaded")
