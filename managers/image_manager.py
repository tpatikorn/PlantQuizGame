from flask import g
from sqlalchemy.sql.expression import select, func
from models.db_models import Image, Tag, ImageTag


def fetch_all_with_seed(q, seed):
    __set_db_seed(seed)
    return g.session.scalars(q).fetchall()


def __set_db_seed(seed: float):
    if seed is not None:
        g.session.scalars(select(func.setseed(seed)))


def fetch_tags(conditions: list = None, limit=None, seed: float = None) -> list[Tag]:
    q = select(Tag).order_by(func.random())
    if conditions is not None:
        q = q.where(*conditions)
    if limit is not None:
        q = q.limit(limit)
    return [_ for _ in fetch_all_with_seed(q, seed)]


def fetch_image_from_id(image_id: int) -> Image:
    q = select(Image).where(Image.id == image_id)
    return g.session.scalars(q).first()


def fetch_images(conditions=None, limit: int = None, seed: float = None) -> list[Image]:
    q = select(Image).join(ImageTag).join(Tag).order_by(func.random())
    if conditions is not None:
        q = q.where(conditions)
    if limit is not None:
        q = q.limit(limit)
    return [_ for _ in fetch_all_with_seed(q, seed)]


def fetch_images_with_tags(include_tags=None, exclude_tags=None, limit=None, seed: float = None) -> list[Image]:
    q = select(Image).join(ImageTag).join(Tag).order_by(func.random())
    if include_tags is not None:
        if type(include_tags) == int:
            include_tags = [include_tags]
        inc_query = Tag.id.in_(include_tags)
        q = q.where(inc_query)

    if exclude_tags is not None:
        if type(exclude_tags) == int:
            exclude_tags = [exclude_tags]
        exc_query = Image.id.notin_(
            select(Image.id).join(ImageTag).join(Tag).where(Tag.id.in_(exclude_tags)).distinct())
        q = q.where(exc_query)

    if limit is not None:
        q = q.limit(limit)
    return [_ for _ in fetch_all_with_seed(q, seed)]


if __name__ == "__main__":
    def to_test():
        print(fetch_tags())
        print(fetch_tags(conditions=[Tag.tag_type_id == 2]))
        result = fetch_images()
        print(type(result), type(result[0]), len(result))
        result = fetch_images(limit=5)
        print(type(result), type(result[0]), len(result))
        result = fetch_images(Tag.id == 2)
        print(type(result), type(result[0]), len(result))
        print(result[0].tags)
        print(fetch_image_from_id(7))
        print(fetch_images_with_tags(include_tags=[20], exclude_tags=[21], limit=10, seed=0.1))
        print(fetch_images_with_tags(include_tags=20, exclude_tags=21, limit=10))


    from util.simple_main_test import test_this

    test_this(to_test)
