import json
import os
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from google_auth_service.google_auth import google_auth_bp
from ai_services.ai_services import configure_genai, grammar_check, check_plagiarism, complete_text, paraphrase_text
from models import db, log_user_activity, log_activity_result, UserActivity

# Initialize Flask app
app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static",
    instance_relative_config=True
)

# Load configuration from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
db_path = os.path.join(app.instance_path, 'activities.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance folder exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

# Initialize the database with the app
db.init_app(app)

# Create database tables before the first request
with app.app_context():
    db.create_all()

# Initialize OpenAI
configure_genai(os.environ["API_KEY"])

# Register Blueprints
app.register_blueprint(google_auth_bp, url_prefix="/")

# Routes
@app.route("/")
def index():
    return redirect(url_for("google_auth.homepage"))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for("google_auth.homepage"))
    user_info = session['user']
    user_id = session.get('user_id')
    user_name = user_info.get('name', 'Unknown')
    activities = db.session.query(UserActivity).filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).all()
    activities_dict = [activity.to_dict() for activity in activities]  # Convert to dict
    print(f"Activities fetched: {activities_dict}")  # Debugging
    return render_template('dashboard.html', activities=activities_dict, user_name=user_name)

@app.route('/api/<action>', methods=['POST'])
def api(action):
    data = request.json
    content = data.get('contents')
    if not content:
        return jsonify({"error": "No content provided"}), 400

    result = {}
    try:
        if action == 'grammar_check':
            result = grammar_check(content)
        elif action == 'plagiarism_check':
            result = check_plagiarism(content)
        elif action == 'text_completion':
            result = complete_text(content)
        elif action == 'paraphrasing':
            result = paraphrase_text(content)
        else:
            return jsonify({'error': 'Invalid action'}), 400

        # Log both the input and output
        log_user_activity(session.get('user_id'), action, 'Activity performed', content, json.dumps(result))
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result)

if __name__ == "__main__":
    # Run the Flask application
    app.run(debug=True)
