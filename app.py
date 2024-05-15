from flask import Flask, redirect, url_for, session, render_template
from google_auth_service.google_auth import google_auth_bp
from ai_service.ai_service import ai_service_bp

app = Flask(__name__)
app.secret_key = "1"

# Đăng ký Blueprint vào ứng dụng chính
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

if __name__ == "__main__":
    app.run(debug=True)
