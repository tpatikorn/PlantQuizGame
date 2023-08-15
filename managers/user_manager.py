from flask import g
from sqlalchemy import select, insert
from models.db_models import User
from werkzeug.security import check_password_hash, generate_password_hash
from psycopg2.errors import UniqueViolation


def find_username(username):
    user = g.session.scalars(select(User).where(User.username == username)).first()
    print(username, user)
    return user if user is not None else None


def find_userid(user_id):
    user = g.session.scalars(select(User).where(User.id == user_id)).first()
    return user if user is not None else None


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
        q = insert(User).values(username=username,
                                password=generate_password_hash(password),
                                email=email).returning(User.id)
        result = g.session.execute(q)
        g.session.commit()
        return result.first()
    except UniqueViolation:
        return -1
