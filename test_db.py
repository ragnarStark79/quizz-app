from app import create_app
from app.models.activity import Activity
from datetime import datetime

app = create_app()
with app.app_context():
    acts = Activity.query.filter_by(action_type='AI Generate').all()
    print("Action type 'AI Generate' count:", len(acts))
    for a in acts:
        print(f"ID: {a.id}, User: {a.user_id}, Timestamp: {a.timestamp}, Now UTC: {datetime.utcnow()}")
