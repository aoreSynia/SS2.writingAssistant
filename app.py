from flask import Flask, redirect, url_for
from google_auth_service.google_auth import google_auth_bp

app = Flask(__name__)
app.secret_key = "1"

# Đăng ký Blueprint vào ứng dụng chính
app.register_blueprint(google_auth_bp, url_prefix="/")

@app.route("/")
def index():
    # Redirect đến trang đăng nhập của Google
    return redirect(url_for("google_auth.homepage"))

if __name__ == "__main__":
    app.run(debug=True)
