import os
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from google_auth_service.google_auth import google_auth_bp
from ai_services.ai_services import configure_genai, grammar_check, check_plagiarism, complete_text, paraphrase_text

app = Flask(__name__)
app.secret_key = "1"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    output_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize OpenAI
configure_genai(os.environ["API_KEY"])

# Register Blueprints
app.register_blueprint(google_auth_bp, url_prefix="/")


@app.route("/")
def index():
    return redirect(url_for("google_auth.homepage"))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for("google_auth.homepage"))
    user_id = session['user']['id']
    activities = Activity.query.filter_by(user_id=user_id).order_by(Activity.timestamp.desc()).all()
    return render_template('dashboard.html', activities=activities)

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
        
        # Save the activity to the database
        new_activity = Activity(
            user_id=session['user']['id'],
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

@app.route('/ai_service')
def home():
    if 'user' not in session:
        return redirect(url_for("google_auth.homepage"))
    return render_template('home.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they do not exist
    app.run(debug=True)
