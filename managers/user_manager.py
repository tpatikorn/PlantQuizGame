import psycopg2

from connectors import db_connector as dbc
from models.db_models import User
from werkzeug.security import check_password_hash, generate_password_hash


def find_username(username):
    return User(dbc.select_one(User.get_query(["username"]), username))


def find_userid(user_id):
    return User(dbc.select_one(User.get_query(["id"]), user_id))


def login(username, password):
    user = find_username(username)
    return user if check_password_hash(user.password, password) else None


def register(username, password, email):
    """
    try to add a new user
    on success, return a new id
    on failure, return -1
    """
    try:
        return dbc.execute_commit_fetch("insert into users (username, password, email) values(%s, %s, %s)",
                                        username, generate_password_hash(password), email)
    except psycopg2.ProgrammingError:
        return -1
