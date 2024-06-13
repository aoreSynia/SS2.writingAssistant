import json
import os
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from google_auth_service.google_auth import google_auth_bp
from ai_services.ai_services import configure_genai, grammar_check, check_plagiarism, complete_text, paraphrase_text
from models import db, Activity  # Importing db and Activity from models.py

app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static",
    instance_relative_config=True  # Tells Flask that config files are relative to the instance folder
)

app.secret_key = "1"
db_path = os.path.join(app.instance_path, 'activities.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
# Initialize OpenAI
configure_genai(os.environ["API_KEY"])

# Register Blueprints
app.register_blueprint(google_auth_bp, url_prefix="/")

# @app.before_first_request
# def create_tables():
#     db.create_all()
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
    
    activities = Activity.query.filter_by(user_id=user_id).order_by(Activity.timestamp.desc()).all()
    return render_template('dashboard.html', activities=activities, user_name=user_name)

@app.route('/api/<action>', methods=['POST'])
def api(action):
    data = request.json
    content = data.get('contents')
    result = {"errors": [], "highlighted_text": ""}

    if not content:
        return jsonify({"error": "No content provided"}), 400

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
        
        new_activity = Activity(
            user_id= session.get('user_id'),
            action=action,
            input_text=content,
            output_text=json.dumps(result)
        )
        db.session.add(new_activity)
        db.session.commit()
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result)

if __name__ == "__main__":
    # Ensure instance folder exists
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # Run the Flask application
    app.run(debug=True)
