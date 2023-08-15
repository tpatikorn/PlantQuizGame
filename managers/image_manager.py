from flask import g
from sqlalchemy import select
from models.db_models import Image, Tag, ImageTag


def fetch_tags(query_dict: dict[str, any] = None) -> list[Tag]:
    if query_dict is None:
        query_dict = {}
    q = select(Tag).where(**query_dict)
    result = [_ for _ in g.session.scalars(q).fetchall()]
    return result


def fetch_image_from_id(image_id: int) -> Image:
    q = select(Image).where(Image.id == image_id)
    result = g.session.scalars(q).first()
    return result


def fetch_images(conditions) -> list[Image]:
    q = select(Image).join(ImageTag).join(Tag).where(conditions)
    result = [_ for _ in g.session.scalars(q).fetchall()]
    return result


if __name__ == "__main__":
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
            print(fetch_tags())
            print(fetch_images(Tag.id == 2))
            print(fetch_image_from_id(7))
