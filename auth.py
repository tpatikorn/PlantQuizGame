import functools

import flask_login
import psycopg2
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from managers import user_manager
from models.db_models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                new_id = user_manager.register(username, password, email)
                print(new_id)
            except psycopg2.Error:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')


@bp.route('/legacy_login', methods=('GET', 'POST'))
def legacy_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = user_manager.login(username, password)

        if user is not None:
            session.clear()
            session['user_id'] = user.id
            return render_template('index.html')

    return render_template('auth/legacy_login.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            g.user = current_user
            print(current_user)
            return render_template('index.html')
    else:
        print(request)
        print(request.data)

    return render_template('index.html')



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_manager.find_userid(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
