import os
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, redirect, session, url_for
from managers import user_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if "user" not in session.keys():
            return "You cannot test code while not logged in.", 403
        else:
            return func(*args, **kwargs)
    return check_login


@bp.route('/login', methods=['POST', 'GET'])
def login():
    redirect_uri = url_for('auth.callback', _external=True, _scheme="https")
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/callback')
def callback():
    token = oauth.google.authorize_access_token()
    user = token['userinfo']

    new_user = user_manager.upsert_user_google(email=user.email, given_name=user.given_name,
                                               family_name=user.family_name, name=user.name, picture=user.picture)
    session['user'] = new_user
    return redirect('/index')


@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/index')
