import os
from functools import wraps

import requests
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, redirect, session, url_for
from werkzeug.exceptions import BadRequestKeyError

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


from google.oauth2 import id_token
from flask import request
from google.auth.transport.requests import Request


@bp.route('/login', methods=['POST', 'GET'])
def login():
    print(request.headers["Referer"])
    user = id_token.verify_oauth2_token(request.form['credential'], Request(), os.getenv('GOOGLE_CLIENT_ID'))
    new_user = user_manager.upsert_user_google(email=user["email"], given_name=user["given_name"],
                                               family_name=user["family_name"], name=user["name"],
                                               picture=user["picture"])
    session['user'] = {"email": new_user.email, "given_name": new_user.given_name, "family_name": new_user.family_name,
                       "name": new_user.name, "picture": new_user.picture, "id": new_user.id}
    return redirect(request.headers["Referer"])


@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/index')
