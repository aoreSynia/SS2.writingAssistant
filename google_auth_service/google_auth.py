from flask import Blueprint, session, abort, redirect, request, url_for
from google.oauth2 import id_token
from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth
import requests
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import cachecontrol
import google.auth.transport.requests

from models import User, UserActivity, db, log_user_activity, log_activity_result

google_auth_bp = Blueprint("google_auth", __name__)

app = Flask(
    __name__, 
    template_folder="web/templates", 
    static_folder="web/static"
)
app.secret_key = '!secret'
app.config.from_object('config')  # Remove this line

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
# @google_auth_bp.route('/loginform')
# def login_form():
#     render_template('login.html')

@google_auth_bp.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)


@google_auth_bp.route('/login')
def login():
    redirect_uri = url_for('google_auth.auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@google_auth_bp.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user_info = token['userinfo']
    session['user'] = user_info
    session['user_id'] = user_info['sub']

    if user_info:
        user = User.query.filter_by(user_id=user_info['sub']).first()
        if not user:
            user = User(
                user_id=user_info['sub'],
                email=user_info['email'],
                full_name=user_info['name']
            )
            db.session.add(user)
            db.session.commit()
        session['user'] = user_info
        session['user_id'] = user.id
    return redirect('/')


@google_auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


