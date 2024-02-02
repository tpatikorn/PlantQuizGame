from flask import g, session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import noload

from models.db_models import User


def find_user_with_email(email) -> User:
    user = g.session.scalars(select(User).where(User.email == email).options(noload(User.submissions))).first()
    return user if user is not None else None


def find_user_with_id(user_id: int) -> User:
    user = g.session.scalars(select(User).where(User.id == user_id).options(noload(User.submissions))).first()
    return user if user is not None else None


def upsert_user_google(email, given_name, family_name, name, picture) -> User:
    q = insert(User).values(email=email, given_name=given_name, family_name=family_name,
                            name=name, picture=picture)
    q = q.on_conflict_do_update(constraint="users_email_key",
                                set_=dict(given_name=given_name, family_name=family_name,
                                          name=name, picture=picture)).returning(User.id)
    result = g.session.execute(q)
    g.session.commit()
    return find_user_with_id(result.first()[0])


def find_current_user_id():
    try:
        return session['user']['id']
    except KeyError:
        return -1
