from flask import Blueprint, render_template
from app.models.user import User
from app.models.attempt import Attempt
from app import db
from sqlalchemy import func

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def index():
    # Calculate per-user stats: avg accuracy + total attempts
    results = (
        db.session.query(
            User,
            func.avg(Attempt.accuracy).label('avg_acc'),
            func.count(Attempt.id).label('total')
        )
        .join(Attempt, Attempt.user_id == User.id)
        .filter(Attempt.submitted_at.isnot(None))
        .filter(User.is_suspended == False)
        .group_by(User.id)
        .order_by(func.avg(Attempt.accuracy).desc(), func.count(Attempt.id).desc())
        .limit(50)
        .all()
    )

    leaderboard = [
        {'rank': i + 1, 'user': r.User, 'avg_acc': round(r.avg_acc, 1), 'total': r.total}
        for i, r in enumerate(results)
    ]

    return render_template('leaderboard/index.html', leaderboard=leaderboard)
