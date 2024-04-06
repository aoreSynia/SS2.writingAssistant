from flask import Blueprint, session, abort, redirect, request, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import pathlib
import requests

# Tạo một blueprint mới với tên là google_auth_bp
google_auth_bp = Blueprint("google_auth", __name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "48603665006-p0tkod3fl4iskfs52b8ear7ruhgg5acu.apps.googleusercontent.com"
# google_auth_service_path = os.path.join(pathlib.Path(__file__).parent, "google_auth_service")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/auth/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    return wrapper

@google_auth_bp.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@google_auth_bp.route("/callback")
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        if not session["state"] == request.args["state"]:
            abort(500)  # State does not match!

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")
        return redirect(url_for("google_auth.index"))
    except Exception as e:
        # Handle errors here, such as authentication failure
        print("Error in callback:", e)
        abort(500)  # Internal server error

@google_auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@google_auth_bp.route("/")
def index():
    if "google_id" in session:
        return redirect(url_for("google_auth.protected_area"))
    return "Hello World <a href='/auth/login'><button>Login</button></a>"

@google_auth_bp.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/auth/logout'><button>Logout</button></a>"
