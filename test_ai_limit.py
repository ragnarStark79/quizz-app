from app import create_app, db
from app.services.ai_quiz_service import AIQuizService
from app.models.activity import Activity
from datetime import date

app = create_app()
with app.app_context():
    # just create a dummy activity
    try:
        from app.models import User
        user = User.query.first()
        if user:
            print("Usage before:", AIQuizService.get_daily_usage(user.id))
            act = Activity(user_id=user.id, action_type='AI Generate', description='test')
            db.session.add(act)
            db.session.commit()
            print("Usage after:", AIQuizService.get_daily_usage(user.id))
            # see if date filter works
            today = date.today()
            count = Activity.query.filter(Activity.user_id == user.id, Activity.action_type == 'AI Generate').count()
            count_today = Activity.query.filter(Activity.user_id == user.id, Activity.action_type == 'AI Generate', db.func.date(Activity.timestamp) == today).count()
            print("Total count:", count)
            print("Count today with func.date:", count_today)
    except Exception as e:
        print("Error:", e)
