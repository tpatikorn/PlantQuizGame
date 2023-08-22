def test_this(fun):
    from flask import g
    from app import create_app
    import os
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    with create_app().app_context():
        load_dotenv()
        engine = create_engine("postgresql://%s:%s@%s:5432/%s" %
                               (os.getenv("DB_USER"),
                                os.getenv("DB_PASS"),
                                os.getenv("DB_SERVER"),
                                os.getenv("DB_DB")))

        with Session(engine) as session:
            g.session = session
            fun()
