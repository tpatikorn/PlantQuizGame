from flask import g
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from models.db_models import User
from psycopg2.errors import UniqueViolation


def find_user_with_email(email):
    user = g.session.scalars(select(User).where(User.email == email)).first()
    return user if user is not None else None


def upsert_user_google(email, given_name, family_name, name, picture):
    try:
        q = insert(User).values(email=email, given_name=given_name, family_name=family_name,
                                name=name, picture=picture)
        q = q.on_conflict_do_update(constraint="users_email_key",
                                    set_=dict(given_name=given_name, family_name=family_name,
                                              name=name, picture=picture)).returning(User.id)
        result = g.session.execute(q)
        g.session.commit()
        return result.first()
    except UniqueViolation:
        return -1
