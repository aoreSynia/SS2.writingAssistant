
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Activity(db.Model):
    user_id = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    input_text = db.Column(db.Text, nullable=True)
    output_text = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_activity(action, input_text=None, output_text=None):
    from flask import session
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError("User must be logged in to log activity")
    activity = Activity(
        user_id=user_id,
        action=action,
        input_text=input_text,
        output_text=output_text
    )
    db.session.add(activity)
    db.session.commit()
