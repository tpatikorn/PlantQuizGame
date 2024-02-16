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
    idinfo = id_token.verify_oauth2_token(request.form['credential'], Request(), os.getenv('GOOGLE_CLIENT_ID'))
    new_user = user_manager.upsert_user_google(email=idinfo["email"], given_name=idinfo["given_name"],
                                               family_name=idinfo["family_name"], name=idinfo["name"],
                                               picture=idinfo["picture"])
    session['user'] = new_user
    return redirect('/index')


@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/index')
