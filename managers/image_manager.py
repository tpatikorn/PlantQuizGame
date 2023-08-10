from connectors import db_connector as dbc
from models.db_models import Image, Tag


def fetch_image_tags(query_dict: dict = None) -> list[Tag]:
    if query_dict is None:
        query_dict = {}

    result = list(map(lambda _: Tag(_),
                      dbc.select_all(Tag.get_query(list(query_dict.keys())), list(query_dict.values()))))
    return result


def fetch_image_from_id(image_id: int) -> Image:
    return Image(dbc.select_one(Image.get_query(["id"]), [image_id]))


def fetch_images(query_dict: dict[str, any] = None) -> list[Image]:
    if query_dict is None:
        query_dict = {}
    return list(map(lambda _: Image(_),
                    dbc.select_all(Image.get_query(list(query_dict.keys())), list(query_dict.values()))))


if __name__ == "__main__":
    print(fetch_image_tags())
    print(fetch_images({"tag_ids": (1, 2)}))
    print(fetch_image_from_id(7))
