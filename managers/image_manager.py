from connectors import db_connector as dbc
from models.db_models import Image, Tags


def fetch_image_tags(query_dict: dict = None) -> list[Tags]:
    if query_dict is None:
        query_dict = {}

    result = list(map(lambda _: Tags(_),
                      dbc.select_all(Tags.get_query(list(query_dict.keys())), list(query_dict.values()))))
    return result


def fetch_images(query_dict: dict = None) -> list[Image]:
    if query_dict is None:
        query_dict = {}

    return list(map(lambda _: Image(_),
                    dbc.select_all(Image.get_query(list(query_dict.keys())), list(query_dict.values()))))


if __name__ == "__main__":
    print(fetch_images())
    print(fetch_image_tags())
