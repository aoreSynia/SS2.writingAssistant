import json
import google.generativeai as genai
from flask import Flask, request, jsonify, session, Response
from flask import Blueprint

ai_service_bp = Blueprint('ai_service', __name__)

app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')  # Remove this line

API_KEY = 'YOUR_API_KEY'
genai.configure(api_key=API_KEY)

def stream_response(response):
    def generate():
        for chunk in response:
            yield 'data: %s\n\n' % json.dumps({"text": chunk.text})
    return Response(generate(), content_type='text/event-stream')

@ai_service_bp.route("/api/grammar_check", methods=["POST"])
def grammar_check():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        req_body = request.get_json()
        content = req_body.get("contents")
        model = genai.GenerativeModel(model_name="text-bison-001")
        response = model.generate_content(content, stream=True)
        if 'activity' not in session:
            session['activity'] = []
        session['activity'].append({'type': 'Grammar Check', 'input': content, 'output': response})
        return stream_response(response)
    except Exception as e:
        return jsonify({"error": str(e)})

@ai_service_bp.route("/api/plagiarism_check", methods=["POST"])
def plagiarism_check():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        req_body = request.get_json()
        content = req_body.get("contents")
        model = genai.GenerativeModel(model_name="text-bison-001")
        response = model.generate_content(content, stream=True)
        if 'activity' not in session:
            session['activity'] = []
        session['activity'].append({'type': 'Plagiarism Check', 'input': content, 'output': response})
        return stream_response(response)
    except Exception as e:
        return jsonify({"error": str(e)})

@ai_service_bp.route("/api/text_completion", methods=["POST"])
def text_completion():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        req_body = request.get_json()
        content = req_body.get("contents")
        model = genai.GenerativeModel(model_name="text-bison-001")
        response = model.generate_content(content, stream=True)
        if 'activity' not in session:
            session['activity'] = []
        session['activity'].append({'type': 'Text Completion', 'input': content, 'output': response})
        return stream_response(response)
    except Exception as e:
        return jsonify({"error": str(e)})

@ai_service_bp.route("/api/paraphrasing", methods=["POST"])
def paraphrasing():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        req_body = request.get_json()
        content = req_body.get("contents")
        model = genai.GenerativeModel(model_name="text-bison-001")
        response = model.generate_content(content, stream=True)
        if 'activity' not in session:
            session['activity'] = []
        session['activity'].append({'type': 'Paraphrasing', 'input': content, 'output': response})
        return stream_response(response)
    except Exception as e:
        return jsonify({"error": str(e)})

@ai_service_bp.route("/dashboard", methods=["GET"])
def dashboard():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    activities = session.get('activity', [])
    return jsonify(activities)
