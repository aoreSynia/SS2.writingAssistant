import json
import os
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from google_auth_service.google_auth import google_auth_bp
from ai_services.ai_services import configure_genai, grammar_check, check_plagiarism, complete_text, paraphrase_text

app = Flask(
    __name__, 
    template_folder="web/templates", 
    static_folder="web/static"
)
app.secret_key = "1"

# Initialize generative AI
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
    activities = session.get('activity', [])
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
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
    
