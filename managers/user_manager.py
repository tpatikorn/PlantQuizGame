import psycopg2

from connectors import db_connector as dbc
from models.db_models import User
from werkzeug.security import check_password_hash, generate_password_hash


def find_username(username):
    user = dbc.select_one(User.get_query(["username"]), [username])
    return User(user) if user is not None else None


def find_userid(user_id):
    user = dbc.select_one(User.get_query(["id"]), [user_id])
    return User(user) if user is not None else None


def login(username, password):
    user = find_username(username)
    return user if user is not None and check_password_hash(user.password, password) else None


def register(username, password, email):
    """
    try to add a new user
    on success, return a new id
    on failure, return -1
    """
    try:
        return dbc.execute_commit_fetch("insert into users (username, password, email) values(%s, %s, %s)",
                                        [username, generate_password_hash(password), email])
    except psycopg2.ProgrammingError:
        return -1
