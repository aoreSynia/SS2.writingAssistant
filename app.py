from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from google_auth_service.google_auth import google_auth_bp
from ai_services.grammar_check import check_grammar
from ai_services.plagiarism_check import check_plagiarism
from ai_services.text_completion import complete_text
from ai_services.paraphrasing import paraphrase_text

app = Flask(
    __name__, 
    template_folder="web/templates", 
    static_folder="web/static"
)
app.secret_key = "1"

# Register Blueprints
app.register_blueprint(google_auth_bp, url_prefix="/")

@app.route("/")
def index():
    # Redirect đến trang đăng nhập của Google
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
    result = {"errors": [], "corrected_text": ""}
    
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    try:
        if action == 'grammar_check':
            result = check_grammar(content)
        elif action == 'plagiarism_check':
            result = check_plagiarism(content)
        elif action == 'text_completion':
            result = complete_text(content)
        elif action == 'paraphrasing':
            result = paraphrase_text(content)
        else:
            return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        # Log the exception for debugging
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
