from app import db
from app.models.activity import Activity

class ActivityService:
    @staticmethod
    def log_activity(user_id, action_type, description):
        try:
            activity = Activity(
                user_id=user_id,
                action_type=action_type,
                description=description
            )
            db.session.add(activity)
            db.session.commit()
            return activity
        except Exception as e:
            db.session.rollback()
            # Do not crash the main thread if logging fails
            return None
