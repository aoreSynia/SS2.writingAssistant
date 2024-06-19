from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.String, unique=True, index=True)  # External service user ID
    email = db.Column(db.String, unique=True, index=True)
    full_name = db.Column(db.String)
    activities = db.relationship("UserActivity", back_populates="user")

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_type = db.Column(db.String)
    activity_details = db.Column(db.String)
    input_data = db.Column(db.Text)  # Store user input
    output_data = db.Column(db.Text)  # Store output data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="activities")
    results = db.relationship("ActivityResult", back_populates="activity", lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_details': self.activity_details,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'timestamp': self.timestamp.isoformat()  # Convert datetime to string
        }

class ActivityResult(db.Model):
    __tablename__ = 'activity_results'
    id = db.Column(db.Integer, primary_key=True, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('user_activities.id'))
    result_type = db.Column(db.String)  # e.g., 'grammar_check', 'plagiarism_check', etc.
    result_data = db.Column(db.JSON)  # Store results as JSON for flexibility
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity = db.relationship("UserActivity", back_populates="results")

def log_user_activity(user_id, activity_type, activity_details, input_data, output_data):
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        activity_details=activity_details,
        input_data=input_data,
        output_data=output_data,
        timestamp=datetime.utcnow()
    )
    db.session.add(activity)
    db.session.commit()
    return activity.id

def log_activity_result(activity_id, result_type, result_data):
    result = ActivityResult(
        activity_id=activity_id,
        result_type=result_type,
        result_data=result_data,
        timestamp=datetime.utcnow()
    )
    db.session.add(result)
    db.session.commit()
