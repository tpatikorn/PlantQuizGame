from connectors import db_connector as dbc
from models.db_modelsx import ImageX, TagX


def fetch_image_tags(query_dict: dict = None) -> list[TagX]:
    if query_dict is None:
        query_dict = {}

    result = list(map(lambda _: TagX(_),
                      dbc.select_all(TagX.get_query(list(query_dict.keys())), list(query_dict.values()))))
    return result


def fetch_image_from_id(image_id: int) -> ImageX:
    return ImageX(dbc.select_one(ImageX.get_query(["id"]), [image_id]))


def fetch_images(query_dict: dict[str, any] = None) -> list[ImageX]:
    if query_dict is None:
        query_dict = {}
    return list(map(lambda _: ImageX(_),
                    dbc.select_all(ImageX.get_query(list(query_dict.keys())), list(query_dict.values()))))


if __name__ == "__main__":
    print(fetch_image_tags())
    print(fetch_images({"tag_ids": (1, 2)}))
    print(fetch_image_from_id(7))
